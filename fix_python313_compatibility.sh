#!/bin/bash
# Python 3.13 Compatibility Fix Script
# Resolves "AttributeError: module 'pkgutil' has no attribute 'ImpImporter'"

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Function to fix Python 3.13 compatibility issues
fix_python313_compatibility() {
    local venv_path="$HOME/.debt-env"
    
    log_info "Fixing Python 3.13 compatibility issues..."
    
    # Activate virtual environment
    source "$venv_path/bin/activate"
    
    # Clear pip cache completely
    log_info "Clearing all pip cache..."
    pip cache purge || true
    rm -rf ~/.cache/pip/* 2>/dev/null || true
    
    # Upgrade pip to latest version first
    log_info "Upgrading pip to latest version..."
    python -m pip install --upgrade --no-cache-dir pip
    
    # Remove problematic packages and reinstall with Python 3.13 compatible versions
    log_info "Removing and reinstalling setuptools with Python 3.13 compatibility..."
    pip uninstall -y setuptools pkg_resources distribute || true
    
    # Install the latest setuptools that should be compatible with Python 3.13
    log_info "Installing Python 3.13 compatible setuptools..."
    pip install --no-cache-dir --upgrade "setuptools>=75.0.0"
    
    # Install wheel and build tools
    pip install --no-cache-dir --upgrade wheel build packaging
    
    # Verify the fix
    log_info "Testing Python 3.13 compatibility..."
    if python -c "import setuptools; import pkg_resources; print('✅ setuptools and pkg_resources working')" 2>/dev/null; then
        log_success "Python 3.13 compatibility fixed!"
    else
        log_warning "Standard fix didn't work. Trying alternative approach..."
        
        # Alternative: Install development versions or use --no-build-isolation
        pip install --no-cache-dir --force-reinstall --no-build-isolation "setuptools>=75.0.0"
        
        if python -c "import setuptools; print('✅ setuptools working')" 2>/dev/null; then
            log_success "Alternative fix successful!"
        else
            log_error "Failed to fix Python 3.13 compatibility"
            deactivate
            return 1
        fi
    fi
    
    deactivate
}

# Function to create Python 3.11 fallback environment
create_python311_fallback() {
    log_warning "Creating Python 3.11 fallback environment for better compatibility..."
    
    # Check if Python 3.11 is available
    if command -v python3.11 >/dev/null 2>&1; then
        local fallback_env="$HOME/.debt-env-py311"
        
        # Create Python 3.11 environment
        log_info "Creating Python 3.11 virtual environment at $fallback_env..."
        python3.11 -m venv "$fallback_env"
        
        # Setup the environment
        source "$fallback_env/bin/activate"
        python -m pip install --upgrade pip
        pip install --upgrade setuptools wheel build packaging
        
        # Test the environment
        if python -c "import setuptools; print('✅ Python 3.11 environment working')" 2>/dev/null; then
            log_success "Python 3.11 fallback environment created successfully!"
            log_info "To use Python 3.11 environment: source $fallback_env/bin/activate"
        else
            log_error "Failed to create Python 3.11 fallback"
            deactivate
            return 1
        fi
        
        deactivate
    else
        log_warning "Python 3.11 not available. Install it with: sudo pacman -S python311"
        return 1
    fi
}

# Function to install packages with Python 3.13 workarounds
install_with_workarounds() {
    local venv_path="$HOME/.debt-env"
    source "$venv_path/bin/activate"
    
    log_info "Installing packages with Python 3.13 workarounds..."
    
    # Set environment variables for better compatibility
    export PIP_NO_BUILD_ISOLATION=0
    export PIP_USE_PEP517=1
    
    # Install packages one by one with error handling
    local packages=(
        "wheel"
        "packaging" 
        "build"
        "pip-tools"
    )
    
    for package in "${packages[@]}"; do
        log_info "Installing $package..."
        if ! pip install --no-cache-dir "$package"; then
            log_warning "Failed to install $package normally. Trying without build isolation..."
            pip install --no-build-isolation "$package" || log_error "Failed to install $package"
        fi
    done
    
    deactivate
}

# Function to test package installation
test_package_installation() {
    local venv_path="$HOME/.debt-env"
    source "$venv_path/bin/activate"
    
    log_info "Testing package installation capabilities..."
    
    # Test with a simple package
    local test_package="requests"
    if pip install --no-cache-dir "$test_package" >/dev/null 2>&1; then
        log_success "Package installation working! Cleaning up test package..."
        pip uninstall -y "$test_package" >/dev/null 2>&1
        log_success "Environment is ready for package installation"
    else
        log_error "Package installation still failing"
        deactivate
        return 1
    fi
    
    deactivate
}

# Main function with multiple fix strategies
main() {
    log_info "Starting Python 3.13 compatibility fix..."
    echo
    
    # Strategy 1: Fix current Python 3.13 environment
    log_info "=== STRATEGY 1: Fixing Python 3.13 Environment ==="
    if fix_python313_compatibility; then
        log_success "Python 3.13 environment fixed!"
        
        # Test installation capabilities
        if test_package_installation; then
            log_success "All compatibility issues resolved!"
            echo
            log_info "Your Python 3.13 environment is now ready for package installation."
            return 0
        fi
    fi
    
    # Strategy 2: Enhanced workarounds
    log_info "=== STRATEGY 2: Applying Enhanced Workarounds ==="
    if install_with_workarounds && test_package_installation; then
        log_success "Enhanced workarounds successful!"
        return 0
    fi
    
    # Strategy 3: Python 3.11 fallback
    log_info "=== STRATEGY 3: Python 3.11 Fallback Environment ==="
    if create_python311_fallback; then
        log_warning "Python 3.13 has compatibility issues. Use Python 3.11 environment instead:"
        log_info "  source ~/.debt-env-py311/bin/activate"
        return 0
    fi
    
    # All strategies failed
    log_error "All strategies failed. Manual intervention required."
    return 1
}

# Display troubleshooting information
display_troubleshooting() {
    echo
    log_info "=== PYTHON 3.13 TROUBLESHOOTING ==="
    echo
    log_warning "Python 3.13 is very new and has compatibility issues with some packages:"
    echo
    echo "1. **Root Cause**: pkgutil.ImpImporter was removed in Python 3.13"
    echo "   Some packages still reference this deprecated feature"
    echo
    echo "2. **Recommended Solutions**:"
    echo "   a) Use Python 3.11: sudo pacman -S python311"
    echo "   b) Wait for package updates to support Python 3.13"
    echo "   c) Use --no-build-isolation for problematic packages"
    echo
    echo "3. **Workaround Commands**:"
    echo "   pip install --no-build-isolation package_name"
    echo "   pip install --no-cache-dir --force-reinstall setuptools"
    echo
    echo "4. **Alternative Environment**:"
    echo "   python3.11 -m venv ~/.debt-env-py311"
    echo "   source ~/.debt-env-py311/bin/activate"
    echo
}

# Parse command line arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        display_troubleshooting
        exit 0
        ;;
    *)
        main "$@"
        exit_code=$?
        if [[ $exit_code -ne 0 ]]; then
            display_troubleshooting
        fi
        exit $exit_code
        ;;
esac