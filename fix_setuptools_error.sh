#!/bin/bash
# Fix setuptools.build_meta import error
# This script addresses the "Cannot import 'setuptools.build_meta'" error

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

# Function to fix setuptools in virtual environment
fix_virtual_env() {
    local venv_path="$1"
    
    if [[ ! -d "$venv_path" ]]; then
        log_error "Virtual environment not found at $venv_path"
        return 1
    fi
    
    log_info "Fixing setuptools in virtual environment: $venv_path"
    
    # Activate virtual environment
    source "$venv_path/bin/activate"
    
    # Upgrade pip first
    log_info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Force reinstall setuptools and wheel
    log_info "Reinstalling setuptools and wheel..."
    pip uninstall -y setuptools wheel || true
    pip install --upgrade setuptools wheel
    
    # Verify setuptools.build_meta is available
    log_info "Verifying setuptools.build_meta availability..."
    if python -c "import setuptools.build_meta; print('✅ setuptools.build_meta is working')" 2>/dev/null; then
        log_success "setuptools.build_meta is now available"
    else
        log_error "setuptools.build_meta still not available"
        return 1
    fi
    
    # Install build dependencies
    log_info "Installing essential build dependencies..."
    pip install build packaging
    
    deactivate
    log_success "Virtual environment fixed successfully"
}

# Function to create a fresh virtual environment
create_fresh_env() {
    local venv_path="$1"
    
    log_warning "Creating fresh virtual environment (backup existing if present)..."
    
    # Backup existing environment
    if [[ -d "$venv_path" ]]; then
        mv "$venv_path" "${venv_path}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "Backed up existing environment"
    fi
    
    # Create new environment
    log_info "Creating new virtual environment at $venv_path"
    python -m venv "$venv_path"
    
    # Activate and setup
    source "$venv_path/bin/activate"
    
    # Upgrade pip and install essential packages
    python -m pip install --upgrade pip
    pip install --upgrade setuptools wheel build packaging
    
    # Verify
    if python -c "import setuptools.build_meta; print('✅ Fresh environment ready')" 2>/dev/null; then
        log_success "Fresh virtual environment created successfully"
    else
        log_error "Failed to create working environment"
        return 1
    fi
    
    deactivate
}

# Function to clean pip cache
clean_pip_cache() {
    log_info "Cleaning pip cache..."
    pip cache purge 2>/dev/null || true
    rm -rf ~/.cache/pip/* 2>/dev/null || true
    log_success "Pip cache cleaned"
}

# Main function
main() {
    log_info "Starting setuptools.build_meta error fix"
    
    # Clean pip cache first
    clean_pip_cache
    
    # Try to fix existing virtual environment
    local venv_path="$HOME/.debt-env"
    
    if [[ -d "$venv_path" ]]; then
        log_info "Attempting to fix existing virtual environment..."
        if fix_virtual_env "$venv_path"; then
            log_success "Existing environment fixed successfully!"
        else
            log_warning "Failed to fix existing environment. Creating fresh one..."
            create_fresh_env "$venv_path"
        fi
    else
        log_info "No existing virtual environment found. Creating fresh one..."
        create_fresh_env "$venv_path"
    fi
    
    # Test the environment
    log_info "Testing the environment with a simple package installation..."
    source "$venv_path/bin/activate"
    
    # Test with a simple package
    if pip install --no-cache-dir requests >/dev/null 2>&1; then
        log_success "Environment is working correctly!"
        pip uninstall -y requests >/dev/null 2>&1 || true
    else
        log_error "Environment still has issues"
        return 1
    fi
    
    deactivate
    
    log_success "setuptools.build_meta error has been fixed!"
    echo
    log_info "You can now:"
    log_info "  1. Activate the environment: source $venv_path/bin/activate"
    log_info "  2. Run the install-packages.sh script again"
    log_info "  3. Install your desired Python packages"
}

# Additional troubleshooting function
troubleshoot() {
    echo
    log_info "=== TROUBLESHOOTING TIPS ==="
    echo
    log_info "If you still encounter setuptools.build_meta errors:"
    echo
    echo "1. System-level fix (if using system Python):"
    echo "   sudo python -m pip install --upgrade setuptools wheel"
    echo
    echo "2. Force reinstall in virtual environment:"
    echo "   source ~/.debt-env/bin/activate"
    echo "   pip install --force-reinstall --no-cache-dir setuptools wheel"
    echo
    echo "3. Alternative: Use conda instead of venv:"
    echo "   conda create -n debt-env python=3.11"
    echo "   conda activate debt-env"
    echo
    echo "4. For specific package issues, try:"
    echo "   pip install --no-build-isolation package_name"
    echo
    echo "5. If all else fails, try Python 3.11 instead of 3.13:"
    echo "   Python 3.13 is very new and some packages may not be compatible"
    echo
}

# Parse command line arguments
case "${1:-}" in
    "troubleshoot"|"help"|"-h"|"--help")
        troubleshoot
        exit 0
        ;;
    *)
        main "$@"
        troubleshoot
        ;;
esac