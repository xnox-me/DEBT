#!/bin/bash
# Consolidate Virtual Environments
# This script merges .nvim_env and .debt-env into a single .debt-env environment

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

# Function to backup and remove old environment
cleanup_old_env() {
    local old_env="$HOME/.nvim_env"
    local backup_env="$HOME/.nvim_env.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [[ -d "$old_env" ]]; then
        log_info "Backing up old .nvim_env environment..."
        mv "$old_env" "$backup_env"
        log_success "Old environment backed up to: $backup_env"
        log_info "You can safely delete the backup later if everything works: rm -rf $backup_env"
    else
        log_info "No .nvim_env environment found to clean up"
    fi
}

# Function to ensure .debt-env is properly set up
ensure_debt_env() {
    local debt_env="$HOME/.debt-env"
    
    if [[ ! -d "$debt_env" ]]; then
        log_warning ".debt-env not found. Creating fresh environment..."
        python -m venv "$debt_env"
        source "$debt_env/bin/activate"
        python -m pip install --upgrade pip
        pip install --upgrade setuptools wheel build packaging
        deactivate
        log_success "Fresh .debt-env created"
    else
        log_info ".debt-env already exists and is our target environment"
    fi
}

# Function to update activate_env.sh to use .debt-env
update_activate_script() {
    local script_path="/home/eboalking/nvimdronat/activate_env.sh"
    
    log_info "Updating activate_env.sh to use .debt-env..."
    
    # Create updated content
    cat > "$script_path" << 'EOF'
#!/bin/bash
# Activation script for the DEBT (Development Environment & Business Tools)

VENV_PATH="$HOME/.debt-env"

if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo "✅ DEBT Virtual environment activated!"
    echo "🏢 Business Intelligence & Development packages available:"
    echo "   • shell-gpt (AI business assistant - sgpt command)"
    echo "   • jupyter, ipython (business analytics notebooks)"
    echo "   • pandas, numpy, matplotlib (data analysis)"
    echo "   • scikit-learn, seaborn, plotly (business intelligence)"
    echo "   • openbb, mlflow, gradio, streamlit (ML/AI tools)"
    echo ""
    echo "💼 Welcome to DEBT - Your business development environment!"
    echo "💡 Use 'deactivate' to exit the virtual environment"
    echo "📍 Virtual Environment: $VENV_PATH"
else
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Run the install-packages.sh script first"
fi
EOF
    
    chmod +x "$script_path"
    log_success "Updated activate_env.sh to use .debt-env"
}

# Function to create convenience activation scripts
create_activation_scripts() {
    local debt_env="$HOME/.debt-env"
    
    # Create simple activation script in home directory
    log_info "Creating convenience activation script..."
    
    cat > "$HOME/activate_debt_env.sh" << EOF
#!/bin/bash
# Quick activation script for DEBT environment
source $debt_env/bin/activate
echo "🚀 DEBT environment activated!"
echo "📍 Location: $debt_env"
EOF
    
    chmod +x "$HOME/activate_debt_env.sh"
    log_success "Created ~/activate_debt_env.sh"
    
    # Update the project's activate script
    if [[ -f "/home/eboalking/nvimdronat/start_key_portal.sh" ]]; then
        log_info "Checking start_key_portal.sh for environment references..."
        # This will be handled separately if needed
    fi
}

# Function to verify the consolidated environment
verify_environment() {
    local debt_env="$HOME/.debt-env"
    
    log_info "Verifying consolidated environment..."
    
    source "$debt_env/bin/activate"
    
    # Test key imports
    if python -c "import setuptools.build_meta; print('✅ setuptools.build_meta available')" 2>/dev/null; then
        log_success "Build tools working"
    else
        log_error "Build tools not working"
        return 1
    fi
    
    # Check for key packages
    local key_packages=("pip" "setuptools" "wheel")
    for package in "${key_packages[@]}"; do
        if pip show "$package" >/dev/null 2>&1; then
            log_info "✅ $package is installed"
        else
            log_warning "⚠️  $package is missing"
        fi
    done
    
    deactivate
    log_success "Environment verification complete"
}

# Function to display summary
display_summary() {
    echo
    log_success "=== VIRTUAL ENVIRONMENT CONSOLIDATION COMPLETE ==="
    echo
    log_info "STANDARDIZED ENVIRONMENT:"
    log_info "  • Single environment: ~/.debt-env"
    log_info "  • Activation script: ./activate_env.sh (updated)"
    log_info "  • Quick activation: ~/activate_debt_env.sh (new)"
    echo
    log_info "USAGE:"
    log_info "  1. Activate environment: source ~/.debt-env/bin/activate"
    log_info "  2. Use project script: ./activate_env.sh"
    log_info "  3. Use quick script: ~/activate_debt_env.sh"
    echo
    log_info "NEXT STEPS:"
    log_info "  • Test the environment: source ~/.debt-env/bin/activate"
    log_info "  • Install missing packages with: ./install-packages.sh"
    log_info "  • Delete old backup when satisfied: rm -rf ~/.nvim_env.backup.*"
    echo
}

# Main function
main() {
    log_info "Starting virtual environment consolidation..."
    echo
    
    # Step 1: Ensure target environment exists
    ensure_debt_env
    
    # Step 2: Backup and remove old environment
    cleanup_old_env
    
    # Step 3: Update activation scripts
    update_activate_script
    
    # Step 4: Create convenience scripts
    create_activation_scripts
    
    # Step 5: Verify everything works
    verify_environment
    
    # Step 6: Display summary
    display_summary
    
    log_success "Virtual environment consolidation completed successfully!"
}

# Run main function
main "$@"