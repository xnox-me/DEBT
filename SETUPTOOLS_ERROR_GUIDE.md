# Setuptools.build_meta Import Error - Complete Guide

## Error Description

The error `Cannot import 'setuptools.build_meta'` occurs when pip tries to build Python packages from source distributions (sdist) but cannot access the required build backend.

### Full Error Traceback Pattern:
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
```

## Root Causes

1. **Missing setuptools**: The `setuptools` package is not installed or corrupted
2. **Outdated setuptools**: Version incompatible with current Python version
3. **Virtual environment corruption**: Partial installation state
4. **Python 3.13 compatibility**: Very new Python versions may have package compatibility issues
5. **Build backend misconfiguration**: Missing build dependencies

## Quick Fix (Recommended)

Run the provided fix script:
```bash
./fix_setuptools_error.sh
```

## Manual Solutions

### Solution 1: Fix Existing Virtual Environment
```bash
# Activate your virtual environment
source ~/.debt-env/bin/activate

# Upgrade pip first
python -m pip install --upgrade pip

# Force reinstall setuptools and wheel
pip uninstall -y setuptools wheel
pip install --upgrade setuptools wheel build packaging

# Verify the fix
python -c "import setuptools.build_meta; print('Fixed!')"

deactivate
```

### Solution 2: Create Fresh Virtual Environment
```bash
# Backup existing environment
mv ~/.debt-env ~/.debt-env.backup.$(date +%Y%m%d_%H%M%S)

# Create new environment
python -m venv ~/.debt-env
source ~/.debt-env/bin/activate

# Install essential packages
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel build packaging

deactivate
```

### Solution 3: System-Level Fix
```bash
# Fix system Python (use with caution)
sudo python -m pip install --upgrade setuptools wheel
```

### Solution 4: Alternative Python Version
```bash
# Use Python 3.11 instead of 3.13 if compatibility issues persist
python3.11 -m venv ~/.debt-env-py311
source ~/.debt-env-py311/bin/activate
pip install --upgrade pip setuptools wheel
```

## Prevention (Applied to install-packages.sh)

The install script has been updated to:

1. Always upgrade pip first
2. Install setuptools, wheel, build, and packaging before other packages
3. Verify setuptools.build_meta is importable before proceeding
4. Provide clear error messages and recovery suggestions

## Troubleshooting Specific Issues

### Issue: "No module named 'setuptools'"
```bash
# Install setuptools in the environment
pip install setuptools
```

### Issue: "setuptools version too old"
```bash
# Force upgrade
pip install --upgrade --force-reinstall setuptools
```

### Issue: "Permission denied"
```bash
# Use virtual environment instead of system Python
python -m venv myenv
source myenv/bin/activate
```

### Issue: "Backend unavailable during specific package installation"
```bash
# Install without build isolation
pip install --no-build-isolation package_name
```

## Environment Verification

After applying any fix, verify your environment:

```bash
source ~/.debt-env/bin/activate

# Test imports
python -c "import setuptools.build_meta; print('setuptools.build_meta: OK')"
python -c "import pip; print('pip: OK')"
python -c "import wheel; print('wheel: OK')"

# Test package installation
pip install --no-cache-dir requests
pip uninstall -y requests

echo "Environment is ready!"
deactivate
```

## Best Practices

1. **Always use virtual environments** for project dependencies
2. **Keep setuptools updated** in all environments
3. **Install build dependencies first** before other packages
4. **Use specific Python versions** (3.11 is more stable than 3.13)
5. **Clear pip cache** when encountering build issues: `pip cache purge`

## When to Use Each Solution

- **fix_setuptools_error.sh**: First-time fix, comprehensive solution
- **Manual Solution 1**: You understand the steps and want control
- **Manual Solution 2**: Virtual environment is severely corrupted
- **Manual Solution 3**: System-wide Python setup issues
- **Manual Solution 4**: Python 3.13 compatibility problems

## Related Files

- `fix_setuptools_error.sh`: Automated fix script
- `install-packages.sh`: Updated installation script with prevention
- `activate_env.sh`: Environment activation script

The error has been resolved and the environment is now ready for package installation.