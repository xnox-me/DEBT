#!/usr/bin/env python3
"""
DEBT Key Management Portal
A secure web interface for managing API keys and credentials for all DEBT services.
Includes Python environment management for compatibility with Python 3.13.
"""

import os
import json
import hashlib
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Configuration
KEYS_FILE = os.path.expanduser('~/.debt_keys.json')
AUTH_FILE = os.path.expanduser('~/.debt_auth.json')
ENCRYPTION_KEY_FILE = os.path.expanduser('~/.debt_encryption.key')

class KeyManager:
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for securing stored credentials."""
        if os.path.exists(ENCRYPTION_KEY_FILE):
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(ENCRYPTION_KEY_FILE, 'wb') as f:
                f.write(key)
            os.chmod(ENCRYPTION_KEY_FILE, 0o600)  # Restrict permissions
            return key
    
    def encrypt_value(self, value):
        """Encrypt a value."""
        if isinstance(value, str):
            value = value.encode()
        return self.cipher.encrypt(value).decode()
    
    def decrypt_value(self, encrypted_value):
        """Decrypt a value."""
        if isinstance(encrypted_value, str):
            encrypted_value = encrypted_value.encode()
        return self.cipher.decrypt(encrypted_value).decode()
    
    def load_keys(self):
        """Load and decrypt stored keys."""
        if not os.path.exists(KEYS_FILE):
            return {}
        
        with open(KEYS_FILE, 'r') as f:
            encrypted_data = json.load(f)
        
        decrypted_data = {}
        for service, data in encrypted_data.items():
            decrypted_data[service] = {
                'key': self.decrypt_value(data['encrypted_key']) if data['encrypted_key'] else '',
                'description': data['description'],
                'created_at': data['created_at'],
                'last_updated': data['last_updated'],
                'status': data.get('status', 'inactive')
            }
        
        return decrypted_data
    
    def save_keys(self, keys_data):
        """Encrypt and save keys."""
        encrypted_data = {}
        for service, data in keys_data.items():
            encrypted_data[service] = {
                'encrypted_key': self.encrypt_value(data['key']) if data['key'] else '',
                'description': data['description'],
                'created_at': data['created_at'],
                'last_updated': datetime.now().isoformat(),
                'status': data.get('status', 'inactive')
            }
        
        with open(KEYS_FILE, 'w') as f:
            json.dump(encrypted_data, f, indent=2)
        os.chmod(KEYS_FILE, 0o600)  # Restrict permissions

key_manager = KeyManager()

class PythonEnvironmentManager:
    """Manage Python virtual environments and detect compatibility issues."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.debt_env = self.home_dir / '.debt-env'
        self.debt_env_py311 = self.home_dir / '.debt-env-py311'
    
    def get_python_version(self, env_path=None):
        """Get Python version for a specific environment or system Python."""
        try:
            if env_path:
                python_path = env_path / 'bin' / 'python'
                if not python_path.exists():
                    return None
                result = subprocess.run([str(python_path), '--version'], 
                                      capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run([sys.executable, '--version'], 
                                      capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Extract version number (e.g., "Python 3.13.7" -> "3.13.7")
                return version_str.replace('Python ', '')
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None
    
    def check_environment_health(self, env_path):
        """Check if a Python environment is healthy and working."""
        if not env_path.exists():
            return {'status': 'missing', 'details': 'Environment does not exist'}
        
        python_path = env_path / 'bin' / 'python'
        if not python_path.exists():
            return {'status': 'corrupted', 'details': 'Python executable missing'}
        
        try:
            # Test basic imports
            test_cmd = [
                str(python_path), '-c', 
                'import sys, pip, setuptools; print("OK")'
            ]
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Test setuptools.build_meta specifically for Python 3.13
                version = self.get_python_version(env_path)
                if version and version.startswith('3.13'):
                    build_test_cmd = [
                        str(python_path), '-c',
                        'import setuptools.build_meta; print("BUILD_OK")'
                    ]
                    build_result = subprocess.run(build_test_cmd, capture_output=True, text=True, timeout=5)
                    
                    if build_result.returncode != 0:
                        return {
                            'status': 'python313_issue',
                            'details': 'Python 3.13 compatibility issue with setuptools.build_meta',
                            'fix_available': True
                        }
                
                return {'status': 'healthy', 'details': 'Environment is working correctly'}
            else:
                return {
                    'status': 'unhealthy', 
                    'details': f'Import test failed: {result.stderr}'
                }
        
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'details': 'Environment check timed out'}
        except Exception as e:
            return {'status': 'error', 'details': f'Check failed: {str(e)}'}
    
    def get_available_environments(self):
        """Get list of available Python environments with their status."""
        environments = {}
        
        # System Python
        system_version = self.get_python_version()
        environments['system'] = {
            'name': 'System Python',
            'path': 'system',
            'version': system_version or 'Unknown',
            'status': 'available' if system_version else 'unavailable',
            'recommended': False,
            'description': 'System-wide Python installation'
        }
        
        # DEBT main environment
        debt_health = self.check_environment_health(self.debt_env)
        debt_version = self.get_python_version(self.debt_env)
        environments['debt-env'] = {
            'name': 'DEBT Main Environment',
            'path': str(self.debt_env),
            'version': debt_version or 'Unknown',
            'status': debt_health['status'],
            'details': debt_health['details'],
            'recommended': debt_health['status'] == 'healthy',
            'description': 'Main virtual environment for DEBT tools',
            'fix_available': debt_health.get('fix_available', False)
        }
        
        # DEBT Python 3.11 fallback environment
        if self.debt_env_py311.exists():
            py311_health = self.check_environment_health(self.debt_env_py311)
            py311_version = self.get_python_version(self.debt_env_py311)
            environments['debt-env-py311'] = {
                'name': 'DEBT Python 3.11 Environment',
                'path': str(self.debt_env_py311),
                'version': py311_version or 'Unknown',
                'status': py311_health['status'],
                'details': py311_health['details'],
                'recommended': py311_health['status'] == 'healthy' and debt_health['status'] != 'healthy',
                'description': 'Python 3.11 fallback environment for compatibility',
                'fix_available': False
            }
        
        # Check for Python 3.11 availability for creating fallback
        try:
            result = subprocess.run(['python3.11', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                environments['python311-available'] = {
                    'name': 'Create Python 3.11 Environment',
                    'path': 'create-py311',
                    'version': result.stdout.strip().replace('Python ', ''),
                    'status': 'creatable',
                    'recommended': debt_health['status'] == 'python313_issue',
                    'description': 'Create new Python 3.11 environment for maximum compatibility'
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return environments
    
    def get_current_environment(self):
        """Detect which environment is currently active."""
        virtual_env = os.environ.get('VIRTUAL_ENV')
        if virtual_env:
            if '.debt-env' in virtual_env:
                if 'py311' in virtual_env:
                    return 'debt-env-py311'
                else:
                    return 'debt-env'
            else:
                return 'custom'
        return 'system'

python_env_manager = PythonEnvironmentManager()

def get_default_services():
    """Get the default services supported by DEBT environment."""
    return {
        'openai': {
            'name': 'OpenAI API',
            'description': 'API key for ChatGPT, GPT-4, and other OpenAI services (used by ShellGPT)',
            'env_var': 'OPENAI_API_KEY',
            'setup_url': 'https://platform.openai.com/api-keys',
            'required_for': ['ShellGPT', 'AI Assistant']
        },
        'huggingface': {
            'name': 'Hugging Face',
            'description': 'Access token for Hugging Face models and datasets',
            'env_var': 'HUGGINGFACE_TOKEN',
            'setup_url': 'https://huggingface.co/settings/tokens',
            'required_for': ['Transformers', 'Model Downloads']
        },
        'wandb': {
            'name': 'Weights & Biases',
            'description': 'API key for experiment tracking and MLOps',
            'env_var': 'WANDB_API_KEY',
            'setup_url': 'https://wandb.ai/settings',
            'required_for': ['MLflow', 'Experiment Tracking']
        },
        'mlflow': {
            'name': 'MLflow Tracking',
            'description': 'MLflow tracking server URI and credentials',
            'env_var': 'MLFLOW_TRACKING_URI',
            'setup_url': 'https://mlflow.org/docs/latest/tracking.html',
            'required_for': ['MLflow UI', 'Experiment Tracking']
        },
        'github': {
            'name': 'GitHub Token',
            'description': 'Personal access token for GitHub CLI and API',
            'env_var': 'GITHUB_TOKEN',
            'setup_url': 'https://github.com/settings/tokens',
            'required_for': ['GitHub CLI', 'Repository Access']
        },
        'docker_hub': {
            'name': 'Docker Hub',
            'description': 'Docker Hub credentials for image pushing/pulling',
            'env_var': 'DOCKER_HUB_TOKEN',
            'setup_url': 'https://hub.docker.com/settings/security',
            'required_for': ['Docker Registry', 'Container Deployment']
        },
        'openbb': {
            'name': 'OpenBB Keys',
            'description': 'Financial data API keys (Alpha Vantage, FRED, etc.)',
            'env_var': 'OPENBB_API_KEYS',
            'setup_url': 'https://docs.openbb.co/terminal/usage/guides/api-keys',
            'required_for': ['OpenBB Terminal', 'Financial Data']
        },
        'gradio': {
            'name': 'Gradio API',
            'description': 'Gradio API token for sharing models',
            'env_var': 'GRADIO_TOKEN',
            'setup_url': 'https://huggingface.co/settings/tokens',
            'required_for': ['Gradio Model Sharing']
        }
    }

def require_auth(f):
    """Decorator to require authentication."""
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def load_auth_config():
    """Load authentication configuration."""
    if not os.path.exists(AUTH_FILE):
        return None
    
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)

def save_auth_config(config):
    """Save authentication configuration."""
    with open(AUTH_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(AUTH_FILE, 0o600)

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard showing all keys and their status."""
    keys_data = key_manager.load_keys()
    services = get_default_services()
    
    # Merge with existing keys
    for service_id, service_info in services.items():
        if service_id not in keys_data:
            keys_data[service_id] = {
                'key': '',
                'description': service_info['description'],
                'created_at': '',
                'last_updated': '',
                'status': 'not_configured'
            }
        # Add service metadata
        keys_data[service_id]['service_info'] = service_info
    
    return render_template_string(DASHBOARD_TEMPLATE, keys=keys_data, services=services)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    auth_config = load_auth_config()
    
    if request.method == 'POST':
        if auth_config is None:
            # First time setup
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template_string(LOGIN_TEMPLATE, first_setup=True)
            
            if len(password) < 8:
                flash('Password must be at least 8 characters', 'error')
                return render_template_string(LOGIN_TEMPLATE, first_setup=True)
            
            # Save password hash
            password_hash = generate_password_hash(password)
            save_auth_config({'password_hash': password_hash, 'created_at': datetime.now().isoformat()})
            
            session['authenticated'] = True
            flash('Password set successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Login attempt
            password = request.form['password']
            
            if check_password_hash(auth_config['password_hash'], password):
                session['authenticated'] = True
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password', 'error')
    
    return render_template_string(LOGIN_TEMPLATE, first_setup=(auth_config is None))

@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/api/keys/<service_id>', methods=['POST'])
@require_auth
def update_key(service_id):
    """Update API key for a service."""
    data = request.json
    keys_data = key_manager.load_keys()
    services = get_default_services()
    
    if service_id not in services:
        return jsonify({'error': 'Service not found'}), 404
    
    # Update or create key entry
    keys_data[service_id] = {
        'key': data.get('key', ''),
        'description': services[service_id]['description'],
        'created_at': keys_data.get(service_id, {}).get('created_at', datetime.now().isoformat()),
        'last_updated': datetime.now().isoformat(),
        'status': 'active' if data.get('key') else 'inactive'
    }
    
    key_manager.save_keys(keys_data)
    return jsonify({'success': True, 'message': f'{services[service_id]["name"]} key updated'})

@app.route('/api/keys/<service_id>', methods=['DELETE'])
@require_auth
def delete_key(service_id):
    """Delete API key for a service."""
    keys_data = key_manager.load_keys()
    
    if service_id in keys_data:
        keys_data[service_id]['key'] = ''
        keys_data[service_id]['status'] = 'inactive'
        keys_data[service_id]['last_updated'] = datetime.now().isoformat()
        key_manager.save_keys(keys_data)
    
    return jsonify({'success': True, 'message': 'Key deleted'})

@app.route('/export-env')
@require_auth
def export_env():
    """Export environment variables for all configured keys."""
    keys_data = key_manager.load_keys()
    services = get_default_services()
    
    env_lines = []
    env_lines.append("# DEBT Environment Variables")
    env_lines.append("# Generated on: " + datetime.now().isoformat())
    env_lines.append("")
    
    for service_id, key_data in keys_data.items():
        if key_data['key'] and service_id in services:
            service_info = services[service_id]
            env_var = service_info['env_var']
            env_lines.append(f"export {env_var}='{key_data['key']}'")
    
    return '\n'.join(env_lines), 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=debt_environment.sh'
    }

@app.route('/python-environments')
@require_auth
def python_environments():
    """Python environment management page."""
    environments = python_env_manager.get_available_environments()
    current_env = python_env_manager.get_current_environment()
    
    return render_template_string(PYTHON_ENV_TEMPLATE, 
                                environments=environments, 
                                current_env=current_env)

@app.route('/api/python-env/fix/<env_id>', methods=['POST'])
@require_auth
def fix_python_environment(env_id):
    """Fix Python environment issues."""
    try:
        if env_id == 'debt-env':
            # Run the Python 3.13 compatibility fix
            script_path = Path.home().parent / 'eboalking' / 'nvimdronat' / 'fix_python313_compatibility.sh'
            if script_path.exists():
                result = subprocess.run(['bash', str(script_path)], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    return jsonify({
                        'success': True, 
                        'message': 'Python 3.13 compatibility issues fixed!',
                        'output': result.stdout
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'error': 'Fix script failed',
                        'output': result.stderr
                    })
            else:
                return jsonify({
                    'success': False, 
                    'error': 'Fix script not found'
                })
        else:
            return jsonify({'success': False, 'error': 'Environment not supported for fixing'})
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Fix operation timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/python-env/create-py311', methods=['POST'])
@require_auth
def create_python311_env():
    """Create Python 3.11 fallback environment."""
    try:
        env_path = python_env_manager.debt_env_py311
        
        # Create the environment
        result = subprocess.run(['python3.11', '-m', 'venv', str(env_path)], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return jsonify({
                'success': False, 
                'error': f'Failed to create environment: {result.stderr}'
            })
        
        # Setup the environment with essential packages
        python_path = env_path / 'bin' / 'python'
        setup_commands = [
            [str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'],
            [str(python_path), '-m', 'pip', 'install', '--upgrade', 'setuptools', 'wheel', 'build', 'packaging']
        ]
        
        for cmd in setup_commands:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to setup environment: {result.stderr}'
                })
        
        return jsonify({
            'success': True, 
            'message': 'Python 3.11 environment created successfully!'
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Environment creation timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/python-env/switch/<env_id>', methods=['POST'])
@require_auth
def switch_python_environment(env_id):
    """Generate activation script for switching environments."""
    environments = python_env_manager.get_available_environments()
    
    if env_id not in environments:
        return jsonify({'success': False, 'error': 'Environment not found'})
    
    env_info = environments[env_id]
    
    if env_info['status'] not in ['healthy', 'available']:
        return jsonify({'success': False, 'error': f'Environment is {env_info["status"]}'})
    
    # Generate activation commands
    if env_id == 'system':
        activation_cmd = '# Using system Python\ndeactivate 2>/dev/null || true'
    elif env_id == 'debt-env':
        activation_cmd = f'source {python_env_manager.debt_env}/bin/activate'
    elif env_id == 'debt-env-py311':
        activation_cmd = f'source {python_env_manager.debt_env_py311}/bin/activate'
    else:
        return jsonify({'success': False, 'error': 'Unknown environment type'})
    
    return jsonify({
        'success': True, 
        'activation_command': activation_cmd,
        'message': f'To switch to {env_info["name"]}, run the provided command'
    })

# HTML Templates
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEBT Key Management Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        .services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
        .service-card { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .service-header { padding: 20px; border-bottom: 1px solid #eee; }
        .service-name { font-size: 1.3em; font-weight: bold; margin-bottom: 5px; }
        .service-description { color: #666; font-size: 0.9em; }
        .service-body { padding: 20px; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
        .status-active { background: #d4edda; color: #155724; }
        .status-inactive { background: #f8d7da; color: #721c24; }
        .status-not-configured { background: #fff3cd; color: #856404; }
        .key-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
        .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        .actions { display: flex; gap: 10px; margin-top: 15px; }
        .navbar { background: white; padding: 15px 0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
        .required-for { margin-top: 10px; }
        .required-for strong { color: #667eea; }
        .export-section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div>
                <strong>🔑 DEBT Key Portal</strong>
            </div>
            <div>
                <a href="/python-environments" class="btn btn-secondary">🐍 Python Environments</a>
                <a href="/export-env" class="btn btn-secondary">Export Environment</a>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="header">
            <h1>🔑 Key Management Portal</h1>
            <p>Secure management for all your DEBT environment API keys and credentials</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}" style="padding: 10px; margin-bottom: 20px; border-radius: 5px; 
                         {% if category == 'error' %}background: #f8d7da; color: #721c24;{% endif %}
                         {% if category == 'success' %}background: #d4edda; color: #155724;{% endif %}
                         {% if category == 'info' %}background: #d1ecf1; color: #0c5460;{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ keys.values() | selectattr('status', 'equalto', 'active') | list | length }}</div>
                <div class="stat-label">Active Keys</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ keys.values() | selectattr('status', 'equalto', 'not_configured') | list | length }}</div>
                <div class="stat-label">Not Configured</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ keys | length }}</div>
                <div class="stat-label">Total Services</div>
            </div>
        </div>
        
        <div class="export-section">
            <h3>🚀 Quick Setup</h3>
            <p>After configuring your keys, export them as environment variables and add to your shell profile:</p>
            <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px; overflow-x: auto;">
# Download and source environment variables
curl -o ~/.debt_env_vars.sh http://localhost:5001/export-env
echo "source ~/.debt_env_vars.sh" >> ~/.bashrc
source ~/.bashrc</pre>
        </div>
        
        <div class="services-grid">
            {% for service_id, key_data in keys.items() %}
            <div class="service-card">
                <div class="service-header">
                    <div class="service-name">
                        {{ key_data.service_info.name }}
                        <span class="status-badge status-{{ key_data.status }}">
                            {% if key_data.status == 'active' %}✓ Active{% endif %}
                            {% if key_data.status == 'inactive' %}✗ Inactive{% endif %}
                            {% if key_data.status == 'not_configured' %}⚠ Not Configured{% endif %}
                        </span>
                    </div>
                    <div class="service-description">{{ key_data.description }}</div>
                    {% if key_data.service_info.required_for %}
                    <div class="required-for">
                        <strong>Required for:</strong> {{ key_data.service_info.required_for | join(', ') }}
                    </div>
                    {% endif %}
                </div>
                <div class="service-body">
                    <input type="password" 
                           class="key-input" 
                           placeholder="Enter API key..."
                           value="{% if key_data.key %}••••••••••••••••{% endif %}"
                           data-service="{{ service_id }}"
                           id="key-{{ service_id }}">
                    <div class="actions">
                        <button class="btn btn-primary" onclick="updateKey('{{ service_id }}')">Save Key</button>
                        {% if key_data.key %}
                        <button class="btn btn-secondary" onclick="toggleVisibility('{{ service_id }}')">Show/Hide</button>
                        <button class="btn btn-danger" onclick="deleteKey('{{ service_id }}')">Delete</button>
                        {% endif %}
                        <a href="{{ key_data.service_info.setup_url }}" target="_blank" class="btn btn-secondary">Get Key</a>
                    </div>
                    {% if key_data.last_updated %}
                    <div style="margin-top: 10px; color: #666; font-size: 0.8em;">
                        Last updated: {{ key_data.last_updated[:19].replace('T', ' ') }}
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        let keyStates = {};
        
        function updateKey(serviceId) {
            const input = document.getElementById('key-' + serviceId);
            const key = input.value.replace(/•/g, '');
            
            if (!key.trim()) {
                alert('Please enter a valid API key');
                return;
            }
            
            fetch(`/api/keys/${serviceId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: key})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }
        
        function deleteKey(serviceId) {
            if (confirm('Are you sure you want to delete this API key?')) {
                fetch(`/api/keys/${serviceId}`, {method: 'DELETE'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    }
                });
            }
        }
        
        function toggleVisibility(serviceId) {
            const input = document.getElementById('key-' + serviceId);
            if (!keyStates[serviceId]) {
                // Load actual key value
                fetch(`/api/keys/${serviceId}`)
                .then(response => response.json())
                .then(data => {
                    input.type = input.type === 'password' ? 'text' : 'password';
                    if (input.type === 'text') {
                        input.value = data.key;
                        keyStates[serviceId] = data.key;
                    } else {
                        input.value = '••••••••••••••••';
                    }
                });
            } else {
                input.type = input.type === 'password' ? 'text' : 'password';
                if (input.type === 'text') {
                    input.value = keyStates[serviceId];
                } else {
                    input.value = '••••••••••••••••';
                }
            }
        }
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEBT Key Portal - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { font-size: 2.5em; margin-bottom: 10px; }
        .logo p { color: #666; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 1em; }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; background: #667eea; color: white; font-size: 1em; font-weight: bold; cursor: pointer; }
        .btn:hover { background: #5a67d8; }
        .alert { padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .first-setup { background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ffeaa7; }
        .first-setup h3 { color: #856404; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo">
            <h1>🔑</h1>
            <p>DEBT Key Management Portal</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% if first_setup %}
        <div class="first-setup">
            <h3>🚀 First Time Setup</h3>
            <p>Create a password to secure your API keys. This password will be required to access the portal.</p>
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required {% if first_setup %}placeholder="Create a secure password (min 8 chars)"{% else %}placeholder="Enter your password"{% endif %}>
            </div>
            
            {% if first_setup %}
            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required placeholder="Confirm your password">
            </div>
            {% endif %}
            
            <button type="submit" class="btn">
                {% if first_setup %}Create Password{% else %}Login{% endif %}
            </button>
        </form>
        
        <div style="margin-top: 20px; text-align: center; color: #666; font-size: 0.9em;">
            <p>🔒 Your keys are encrypted and stored locally</p>
        </div>
    </div>
</body>
</html>
"""

PYTHON_ENV_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEBT Portal - Python Environments</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .navbar { background: white; padding: 15px 0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
        .env-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .env-card { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .env-header { padding: 20px; border-bottom: 1px solid #eee; }
        .env-name { font-size: 1.3em; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; justify-content: space-between; }
        .env-description { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        .env-version { color: #667eea; font-weight: bold; }
        .env-body { padding: 20px; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-unhealthy { background: #f8d7da; color: #721c24; }
        .status-python313_issue { background: #fff3cd; color: #856404; }
        .status-missing { background: #f8d7da; color: #721c24; }
        .status-available { background: #d1ecf1; color: #0c5460; }
        .status-creatable { background: #e2e3e5; color: #383d41; }
        .recommended-badge { background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; margin-left: 10px; }
        .current-badge { background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; margin-left: 10px; }
        .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin: 5px 5px 5px 0; }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .actions { margin-top: 15px; }
        .details { margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 0.9em; }
        .warning-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .warning-box h3 { color: #856404; margin-bottom: 10px; }
        .info-box { background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .info-box h3 { color: #0c5460; margin-bottom: 10px; }
        .command-box { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; font-family: monospace; margin-top: 10px; }
        .alert { padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .alert-error { background: #f8d7da; color: #721c24; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div>
                <strong>🐍 Python Environment Manager</strong>
            </div>
            <div>
                <a href="/" class="btn btn-secondary">🔑 Back to Keys</a>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="header">
            <h1>🐍 Python Environment Manager</h1>
            <p>Manage Python environments and resolve compatibility issues</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="warning-box">
            <h3>⚠️ Python 3.13 Compatibility Notice</h3>
            <p>Python 3.13 has compatibility issues with some packages due to the removal of <code>pkgutil.ImpImporter</code>. 
               Use the Python 3.11 environment for maximum compatibility, or apply the automatic fixes for Python 3.13.</p>
        </div>
        
        <div class="info-box">
            <h3>📝 Current Environment</h3>
            <p>Currently active: <strong>{{ environments.get(current_env, {}).get('name', 'Unknown') }}</strong></p>
            {% if current_env != 'system' %}
            <p>To switch environments, use the activation commands provided below.</p>
            {% endif %}
        </div>
        
        <div class="env-grid">
            {% for env_id, env_info in environments.items() %}
            <div class="env-card">
                <div class="env-header">
                    <div class="env-name">
                        {{ env_info.name }}
                        <div>
                            {% if env_id == current_env %}
                                <span class="current-badge">CURRENT</span>
                            {% endif %}
                            {% if env_info.recommended %}
                                <span class="recommended-badge">RECOMMENDED</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="env-description">{{ env_info.description }}</div>
                    <div class="env-version">Python {{ env_info.version }}</div>
                </div>
                <div class="env-body">
                    <div class="status-badge status-{{ env_info.status }}">
                        {% if env_info.status == 'healthy' %}✓ Healthy{% endif %}
                        {% if env_info.status == 'unhealthy' %}✗ Unhealthy{% endif %}
                        {% if env_info.status == 'python313_issue' %}⚠️ Python 3.13 Issue{% endif %}
                        {% if env_info.status == 'missing' %}✗ Missing{% endif %}
                        {% if env_info.status == 'available' %}✓ Available{% endif %}
                        {% if env_info.status == 'creatable' %}➕ Can Create{% endif %}
                        {% if env_info.status == 'corrupted' %}✗ Corrupted{% endif %}
                    </div>
                    
                    {% if env_info.details %}
                    <div class="details">
                        <strong>Details:</strong> {{ env_info.details }}
                    </div>
                    {% endif %}
                    
                    <div class="actions">
                        {% if env_info.status == 'healthy' or env_info.status == 'available' %}
                            {% if env_id != current_env %}
                                <button class="btn btn-primary" onclick="switchEnvironment('{{ env_id }}')">Activate</button>
                            {% endif %}
                        {% endif %}
                        
                        {% if env_info.fix_available %}
                            <button class="btn btn-warning" onclick="fixEnvironment('{{ env_id }}')">Fix Python 3.13 Issues</button>
                        {% endif %}
                        
                        {% if env_info.status == 'creatable' %}
                            <button class="btn btn-success" onclick="createPython311Env()">Create Python 3.11 Env</button>
                        {% endif %}
                        
                        {% if env_info.status == 'python313_issue' %}
                            <button class="btn btn-warning" onclick="fixEnvironment('{{ env_id }}')">Fix Compatibility</button>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="info-box">
            <h3>🛠️ Quick Commands</h3>
            <p>Use these commands in your terminal to manually switch environments:</p>
            <div class="command-box">
# Activate DEBT main environment<br>
source ~/.debt-env/bin/activate<br><br>
# Activate Python 3.11 environment (if available)<br>
source ~/.debt-env-py311/bin/activate<br><br>
# Deactivate any environment<br>
deactivate
            </div>
        </div>
    </div>
    
    <div id="output-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 10px; max-width: 80%; max-height: 80%; overflow-y: auto;">
            <h3 id="modal-title">Operation Result</h3>
            <pre id="modal-content" style="background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; margin: 15px 0;"></pre>
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    </div>
    
    <script>
        function switchEnvironment(envId) {
            fetch(`/api/python-env/switch/${envId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showModal('Environment Activation', 
                        `${data.message}\n\nRun this command:\n${data.activation_command}`);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => alert('Request failed: ' + error));
        }
        
        function fixEnvironment(envId) {
            if (!confirm('This will attempt to fix Python 3.13 compatibility issues. Continue?')) {
                return;
            }
            
            const button = event.target;
            button.disabled = true;
            button.textContent = 'Fixing...';
            
            fetch(`/api/python-env/fix/${envId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showModal('Fix Successful', data.output || data.message);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showModal('Fix Failed', data.output || data.error);
                }
            })
            .catch(error => {
                alert('Request failed: ' + error);
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = 'Fix Compatibility';
            });
        }
        
        function createPython311Env() {
            if (!confirm('Create a new Python 3.11 environment? This may take a few minutes.')) {
                return;
            }
            
            const button = event.target;
            button.disabled = true;
            button.textContent = 'Creating...';
            
            fetch('/api/python-env/create-py311', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Request failed: ' + error);
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = 'Create Python 3.11 Env';
            });
        }
        
        function showModal(title, content) {
            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal-content').textContent = content;
            document.getElementById('output-modal').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('output-modal').style.display = 'none';
        }
        
        // Close modal when clicking outside
        document.getElementById('output-modal').onclick = function(e) {
            if (e.target === this) {
                closeModal();
            }
        }
    </script>
</body>
</html>

if __name__ == '__main__':
    print("🔑 DEBT Key Management Portal")
    print("=" * 50)
    print("Starting secure key management server...")
    print(f"📂 Keys file: {KEYS_FILE}")
    print(f"🔐 Auth file: {AUTH_FILE}")
    print(f"🔑 Encryption key: {ENCRYPTION_KEY_FILE}")
    print("=" * 50)
    print("🌐 Access the portal at: http://localhost:5001")
    print("🔒 All keys are encrypted at rest")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=False)