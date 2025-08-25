#!/usr/bin/env python3
"""
DEBT API Plugin Configuration
Configuration management for the DEBT API Plugin system.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class APIPluginConfig:
    """Configuration class for DEBT API Plugin."""
    
    # API Server Configuration
    host: str = "0.0.0.0"
    port: int = 9000
    debug: bool = False
    reload: bool = True
    
    # Authentication & Security
    enable_auth: bool = False
    api_key: Optional[str] = None
    jwt_secret: str = "debt-api-plugin-secret-key"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Service Registry
    services: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "financial_dashboard": {
            "url": "http://localhost:8501",
            "name": "Financial Dashboard", 
            "type": "streamlit",
            "startup_script": "./sophisticated_example/financial_dashboard/start_dashboard.sh"
        },
        "ml_interface": {
            "url": "http://localhost:7860",
            "name": "ML Interface",
            "type": "gradio", 
            "startup_script": "python ./sophisticated_example/gradio_demos/business_ml_interface.py"
        },
        "mlflow_tracking": {
            "url": "http://localhost:5000",
            "name": "MLflow Tracking",
            "type": "mlflow",
            "startup_script": "mlflow server --host 0.0.0.0 --port 5000"
        },
        "jupyter_lab": {
            "url": "http://localhost:8888", 
            "name": "JupyterLab",
            "type": "jupyter",
            "startup_script": "jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root"
        },
        "n8n_workflows": {
            "url": "http://localhost:5678",
            "name": "n8n Workflows", 
            "type": "n8n",
            "startup_script": "n8n start --port 5678"
        },
        "api_services": {
            "url": "http://localhost:8000",
            "name": "DEBT API Services",
            "type": "fastapi",
            "startup_script": "python ./sophisticated_example/api_services/main.py"
        }
    })
    
    # Feature Flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "financial_analysis": True,
        "ml_predictions": True,
        "business_intelligence": True,
        "workflow_automation": True,
        "service_management": True,
        "advanced_analytics": True,
        "real_time_monitoring": True,
        "automated_alerts": True
    })
    
    # Business Intelligence Settings
    business_config: Dict[str, any] = field(default_factory=lambda: {
        "default_market_symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"],
        "analysis_periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
        "ml_confidence_threshold": 0.7,
        "kpi_refresh_interval": 300,  # seconds
        "alert_thresholds": {
            "churn_rate": 0.15,
            "satisfaction_score": 6.5,
            "revenue_decline": -0.1
        }
    })
    
    # Data Sources Configuration
    data_sources: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "yahoo_finance": {
            "enabled": True,
            "rate_limit": "2000/hour",
            "cache_duration": "300"
        },
        "alpha_vantage": {
            "enabled": False,
            "api_key": "",
            "rate_limit": "5/minute"
        },
        "openbb": {
            "enabled": False, 
            "api_key": "",
            "rate_limit": "100/minute"
        }
    })
    
    # Logging Configuration
    logging: Dict[str, any] = field(default_factory=lambda: {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/api_plugin.log",
        "max_size": "10MB",
        "backup_count": 5
    })
    
    # Cache Configuration
    cache: Dict[str, any] = field(default_factory=lambda: {
        "enabled": True,
        "backend": "memory",  # memory, redis, file
        "ttl": 300,  # seconds
        "max_size": "100MB"
    })
    
    # Monitoring Configuration
    monitoring: Dict[str, any] = field(default_factory=lambda: {
        "health_check_interval": 30,  # seconds
        "metrics_collection": True,
        "performance_tracking": True,
        "error_reporting": True
    })

    @classmethod
    def from_env(cls) -> 'APIPluginConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Override with environment variables
        config.host = os.getenv('DEBT_API_HOST', config.host)
        config.port = int(os.getenv('DEBT_API_PORT', config.port))
        config.debug = os.getenv('DEBT_API_DEBUG', 'false').lower() == 'true'
        config.enable_auth = os.getenv('DEBT_API_AUTH', 'false').lower() == 'true'
        config.api_key = os.getenv('DEBT_API_KEY', config.api_key)
        
        return config
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "reload": self.reload,
            "enable_auth": self.enable_auth,
            "services": self.services,
            "features": self.features,
            "business_config": self.business_config,
            "data_sources": self.data_sources,
            "logging": self.logging,
            "cache": self.cache,
            "monitoring": self.monitoring
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        # Check port range
        if not (1000 <= self.port <= 65535):
            errors.append(f"Invalid port {self.port}. Must be between 1000-65535")
        
        # Check required fields
        if self.enable_auth and not self.api_key:
            errors.append("API key required when authentication is enabled")
        
        # Validate service URLs
        for service_name, service_config in self.services.items():
            if not service_config.get('url'):
                errors.append(f"Missing URL for service {service_name}")
        
        return errors

# Global configuration instance
config = APIPluginConfig.from_env()

# Plugin installation and management utilities
class PluginManager:
    """Manage DEBT API Plugin installation and lifecycle."""
    
    def __init__(self, config: APIPluginConfig):
        self.config = config
        self.debt_root = Path("/home/eboalking/Dronat011/DEBT")
        
    def install_plugin(self) -> Dict[str, any]:
        """Install the API plugin into DEBT system."""
        try:
            # Create plugin directory
            plugin_dir = self.debt_root / "plugins" / "api_plugin"
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # Create plugin configuration
            config_file = plugin_dir / "config.json"
            with open(config_file, 'w') as f:
                import json
                json.dump(self.config.to_dict(), f, indent=2)
            
            # Create startup script
            startup_script = plugin_dir / "start_plugin.sh"
            with open(startup_script, 'w') as f:
                f.write(f"""#!/bin/bash
# DEBT API Plugin Startup Script

set -e

echo "🚀 Starting DEBT API Plugin..."

# Activate DEBT environment
if [ -f "$HOME/.debt-env/bin/activate" ]; then
    source "$HOME/.debt-env/bin/activate"
else
    echo "❌ DEBT environment not found"
    exit 1
fi

# Start API plugin
cd {self.debt_root}
python api_plugin.py

echo "✅ DEBT API Plugin started on port {self.config.port}"
""")
            
            startup_script.chmod(0o755)
            
            # Register plugin in DEBT menu
            self.register_in_menu()
            
            return {
                "status": "success",
                "message": "API Plugin installed successfully",
                "plugin_dir": str(plugin_dir),
                "config_file": str(config_file),
                "startup_script": str(startup_script)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Installation failed: {str(e)}"
            }
    
    def register_in_menu(self):
        """Register plugin in DEBT main menu."""
        try:
            menu_file = self.debt_root / "menu.sh"
            if menu_file.exists():
                # Read current menu
                with open(menu_file, 'r') as f:
                    menu_content = f.read()
                
                # Add API plugin option if not already present
                plugin_option = '''        9)
            echo "🌐 Starting DEBT API Plugin..."
            cd "$DEBT_DIR"
            python api_plugin.py
            ;;'''
            
                if "DEBT API Plugin" not in menu_content:
                    # Find the position to insert (before the quit option)
                    insert_pos = menu_content.find('        0)')
                    if insert_pos != -1:
                        new_content = (menu_content[:insert_pos] + 
                                     plugin_option + "\n        " + 
                                     menu_content[insert_pos:])
                        
                        # Update menu options display
                        new_content = new_content.replace(
                            '"0) Exit DEBT"',
                            '"9) DEBT API Plugin\\n0) Exit DEBT"'
                        )
                        
                        # Write updated menu
                        with open(menu_file, 'w') as f:
                            f.write(new_content)
                            
        except Exception as e:
            print(f"Warning: Could not register in menu: {e}")
    
    def uninstall_plugin(self) -> Dict[str, any]:
        """Uninstall the API plugin from DEBT system."""
        try:
            plugin_dir = self.debt_root / "plugins" / "api_plugin"
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)
            
            return {
                "status": "success",
                "message": "API Plugin uninstalled successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Uninstall failed: {str(e)}"
            }

# Utility functions
def get_plugin_status() -> Dict[str, any]:
    """Get current plugin installation and runtime status."""
    plugin_dir = Path("/home/eboalking/Dronat011/DEBT/plugins/api_plugin")
    
    status = {
        "installed": plugin_dir.exists(),
        "config_exists": (plugin_dir / "config.json").exists() if plugin_dir.exists() else False,
        "startup_script_exists": (plugin_dir / "start_plugin.sh").exists() if plugin_dir.exists() else False,
        "plugin_version": "2.0.0",
        "debt_integration": True
    }
    
    # Check if plugin is running
    try:
        import requests
        response = requests.get(f"http://localhost:{config.port}/", timeout=3)
        status["running"] = response.status_code == 200
        status["api_accessible"] = True
    except:
        status["running"] = False
        status["api_accessible"] = False
    
    return status

def create_plugin_requirements():
    """Create requirements file for the API plugin."""
    requirements = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0", 
        "aiohttp>=3.8.0",
        "pydantic>=2.4.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "yfinance>=0.2.0",
        "requests>=2.31.0",
        "python-multipart>=0.0.6"
    ]
    
    requirements_file = Path("/home/eboalking/Dronat011/DEBT/plugins/api_plugin/requirements.txt")
    requirements_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(requirements_file, 'w') as f:
        f.write('\n'.join(requirements))
    
    return str(requirements_file)

if __name__ == "__main__":
    # Plugin configuration validation
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration valid")
        print(f"🌐 API Plugin configured for {config.host}:{config.port}")
        print(f"🔧 Features enabled: {sum(config.features.values())}/{len(config.features)}")
        print(f"🚀 Services registered: {len(config.services)}")