#!/bin/bash
# DEBT (Development Environment & Business Tools) Package Installation Script
# Cross-platform package manager for business development environment
# Supports Ubuntu/Debian (apt) and Arch Linux (pacman)

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Detect the Linux distribution
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "$ID"
    elif [[ -f /etc/debian_version ]]; then
        echo "debian"
    elif [[ -f /etc/arch-release ]]; then
        echo "arch"
    else
        log_error "Unable to detect Linux distribution"
        exit 1
    fi
}

# Update package manager cache
update_cache() {
    local distro="$1"
    log_info "Updating package manager cache..."
    
    case "$distro" in
        ubuntu|debian)
            apt-get update
            ;;
        arch|manjaro)
            pacman -Sy
            ;;
        *)
            log_error "Unsupported distribution: $distro"
            exit 1
            ;;
    esac
    
    log_success "Package cache updated"
}

# Install packages using the appropriate package manager
install_packages() {
    local distro="$1"
    shift
    local packages=("$@")
    
    log_info "Installing packages: ${packages[*]}"
    
    case "$distro" in
        ubuntu|debian)
            DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
            ;;
        arch|manjaro)
            pacman -S --noconfirm "${packages[@]}"
            ;;
        *)
            log_error "Unsupported distribution: $distro"
            exit 1
            ;;
    esac
    
    log_success "Packages installed successfully"
}

# Clean package manager cache
clean_cache() {
    local distro="$1"
    log_info "Cleaning package manager cache..."
    
    case "$distro" in
        ubuntu|debian)
            apt-get autoremove -y
            apt-get autoclean
            rm -rf /var/lib/apt/lists/*
            ;;
        arch|manjaro)
            pacman -Sc --noconfirm
            ;;
        *)
            log_error "Unsupported distribution: $distro"
            exit 1
            ;;
    esac
    
    log_success "Package cache cleaned"
}

# Install business development packages based on distribution
install_dev_packages() {
    local distro="$1"
    
    log_info "Installing DEBT business development packages for $distro"
    
    case "$distro" in
        ubuntu|debian)
            local ubuntu_packages=(
                "build-essential"
                "curl"
                "wget"
                "unzip"
                "git"
                "sudo"
                "ripgrep"
                "fd-find"
                "python3-pip"
                "python3-venv"
                "python3-dev"
                "tmux"
                "nodejs"
                "npm"
                "jq"
                "ca-certificates"
                "gnupg"
                "lsb-release"
                "software-properties-common"
            )
            install_packages "$distro" "${ubuntu_packages[@]}"
            ;;
        arch|manjaro)
            local arch_packages=(
                "base-devel"
                "curl"
                "wget"
                "unzip"
                "git"
                "sudo"
                "ripgrep"
                "fd"
                "python"
                "python-pip"
                "python-virtualenv"
                "tmux"
                "nodejs"
                "npm"
                "jq"
                "ca-certificates"
                "which"
            )
            install_packages "$distro" "${arch_packages[@]}"
            ;;
        *)
            log_error "Unsupported distribution: $distro"
            exit 1
            ;;
    esac
}

# Install GitHub CLI for business collaboration
install_github_cli() {
    local distro="$1"
    
    log_info "Installing GitHub CLI for DEBT business collaboration on $distro"
    
    case "$distro" in
        ubuntu|debian)
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
                tee /usr/share/keyrings/githubcli-archive-keyring.gpg > /dev/null
            chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
                tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            apt-get update
            apt-get install -y gh
            ;;
        arch|manjaro)
            pacman -S --noconfirm github-cli
            ;;
        *)
            log_error "Unsupported distribution: $distro"
            exit 1
            ;;
    esac
    
    log_success "GitHub CLI installed successfully"
}

# Install Python packages including OpenBB, ShellGPT, and ML/AI tools
install_python_packages() {
    log_info "Installing Python packages including OpenBB, ShellGPT, and comprehensive ML/AI tools"
    
    # Create virtual environment for DEBT project
    local venv_path="$HOME/.debt-env"
    log_info "Creating virtual environment at $venv_path"
    python -m venv "$venv_path"
    
    # Activate virtual environment and install packages
    source "$venv_path/bin/activate"
    
    # Install essential Python packages and fix setuptools.build_meta issue
    log_info "Upgrading pip and essential build tools..."
    python -m pip install --upgrade pip
    
    # Python 3.13 compatibility: Clear cache and install compatible setuptools
    if [[ $(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null) == "3.13" ]]; then
        log_info "Detected Python 3.13 - applying compatibility fixes..."
        pip cache purge || true
        pip install --no-cache-dir --upgrade "setuptools>=75.0.0" wheel build packaging
    else
        pip install --upgrade setuptools wheel build packaging
    fi
    
    # Verify setuptools.build_meta is available
    if ! python -c "import setuptools.build_meta" 2>/dev/null; then
        log_error "setuptools.build_meta not available. Fixing..."
        pip install --force-reinstall --no-cache-dir setuptools wheel
        if ! python -c "import setuptools.build_meta" 2>/dev/null; then
            log_error "Failed to fix setuptools.build_meta. Please run fix_setuptools_error.sh"
            deactivate
            return 1
        fi
    fi
    log_success "setuptools.build_meta is available"
    
    # Core packages
    pip install meson openbb shell-gpt jupyter ipython pandas numpy matplotlib
    
    # ML/AI Frameworks
    log_info "Installing ML/AI frameworks..."
    pip install tensorflow torch torchvision torchaudio
    pip install scikit-learn xgboost lightgbm catboost
    
    # Deep learning and transformers
    pip install keras transformers accelerate diffusers
    
    # Data science tools
    pip install seaborn plotly scipy
    
    # Jupyter ecosystem
    pip install jupyterlab notebook jupyterlab-git
    
    # Computer vision
    pip install opencv-python pillow albumentations
    
    # Natural language processing
    pip install nltk spacy textblob gensim
    
    # MLOps and experiment tracking
    pip install mlflow wandb tensorboard
    
    # AutoML and hyperparameter tuning
    pip install optuna hyperopt
    
    # Model deployment and serving
    pip install fastapi uvicorn gradio streamlit
    
    # Additional utilities
    pip install ipywidgets tqdm joblib
    
    deactivate
    
    # Create activation script
    echo '#!/bin/bash' > "$HOME/activate_debt_env.sh"
    echo "source $venv_path/bin/activate" >> "$HOME/activate_debt_env.sh"
    chmod +x "$HOME/activate_debt_env.sh"
    
    log_success "Python packages including OpenBB, ShellGPT, and ML/AI tools installed successfully in virtual environment"
    log_info "To activate the environment, run: source $HOME/activate_debt_env.sh"
}

# Install Docker for Shellngn Pro support
install_docker() {
    local distro="$1"
    
    log_info "Installing Docker for Shellngn Pro support"
    
    case "$distro" in
        ubuntu|debian)
            # Add Docker's official GPG key
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # Set up the repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Update package index
            apt-get update
            
            # Install Docker Engine
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            
            # Add user to docker group (requires re-login to take effect)
            usermod -aG docker $USER || true
            ;;
        arch|manjaro)
            pacman -S --noconfirm docker docker-compose
            systemctl enable docker
            usermod -aG docker $USER || true
            ;;
        *)
            log_warning "Docker installation not configured for $distro. Please install Docker manually for Shellngn Pro support."
            return 1
            ;;
    esac
    
    log_success "Docker installed successfully. Note: You may need to re-login for group changes to take effect."
}

# Main function to orchestrate package installation
main() {
    log_info "Starting cross-distro package installation"
    
    # Detect distribution
    DISTRO=$(detect_distro)
    log_info "Detected distribution: $DISTRO"
    
    # Update package cache
    update_cache "$DISTRO"
    
    # Install development packages
    install_dev_packages "$DISTRO"
    
    # Install GitHub CLI
    install_github_cli "$DISTRO"
    
    # Install Python packages including OpenBB
    install_python_packages
    
    # Install Docker for Shellngn Pro support  
    install_docker "$DISTRO"
    
    # Clean package cache
    clean_cache "$DISTRO"
    
    log_success "All packages installed successfully!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi