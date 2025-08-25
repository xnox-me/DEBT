# DEBT - Development Environment & Business Tools

A comprehensive portable development environment that provides a fully integrated toolkit for software development, machine learning, AI research, automation, financial analysis, and business intelligence. DEBT (Development Environment & Business Tools) combines powerful development capabilities with advanced business and financial analysis tools.

## 🚀 Quick Start

### Prerequisites
- Git
- A Linux system (tested on Arch Linux, supports Ubuntu/Debian)
- Internet connection for package downloads

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url> nvimdronat
   cd nvimdronat
   ```

2. **Install packages:**
   ```bash
   chmod +x install-packages.sh
   sudo ./install-packages.sh
   ```
   
   This script will:
   - Detect your Linux distribution (supports Ubuntu/Debian and Arch Linux)
   - Resolve Node.js package conflicts automatically
   - Install system packages (build tools, git, curl, Node.js v24.6.0, etc.)
   - Install GitHub CLI and Docker
   - Create a Python virtual environment at `~/.debt-env` (PEP 668 compliant)
   - Install comprehensive Python packages (shell-gpt, jupyter, pandas, scikit-learn, ML/AI tools)
   - Configure Docker service and user permissions

3. **Activate the development environment:**
   ```bash
   source ~/activate_debt_env.sh
   ```
   
   Or manually activate the virtual environment:
   ```bash
   source ~/.debt-env/bin/activate
   ```

4. **Run the interactive menu:**
   ```bash
   ./menu.sh
   ```

## 📦 What's Included

### System Tools (Installed via Package Manager)
- **Development Tools:** base-devel (Arch) / build-essential (Ubuntu), git, curl, wget, unzip, sudo
- **Search & Navigation:** ripgrep, fd, which
- **Terminal:** tmux for session management
- **Docker:** docker, docker-compose, python-pipx for containerized applications
- **GitHub CLI:** github-cli for seamless GitHub integration
- **Node.js:** nodejs v24.6.0, npm v11.5.2 for JavaScript development and n8n
- **JSON Processing:** jq for data manipulation
- **Security:** ca-certificates for SSL/TLS

### Python Environment (Virtual Environment: ~/.debt-env)
All Python packages are installed in an isolated virtual environment to comply with PEP 668:

#### Core AI & Development
- **AI Assistant:** shell-gpt v1.4.5 (sgpt command)
- **Development:** jupyter, jupyterlab, notebook, ipython
- **Web Frameworks:** fastapi, uvicorn for API development

#### Data Science & Analytics
- **Data Manipulation:** pandas, numpy
- **Visualization:** matplotlib, seaborn, plotly
- **Scientific Computing:** scipy

#### Machine Learning & AI
- **ML Framework:** scikit-learn
- **MLOps:** mlflow, tensorboard for experiment tracking
- **Model Serving:** gradio, streamlit for web interfaces

#### Utilities
- **HTTP Requests:** requests, httpx
- **Data Validation:** pydantic
- **CLI Tools:** typer, rich for beautiful terminal output

### DEBT Interactive Tools (via menu.sh)
1. **Neovim** - Advanced text editor with pre-configured plugins
2. **n8n** - Business workflow automation (port 5678)
3. **Bash Shell** - Enhanced command line interface
4. **Lean Projects** - Mathematical theorem proving environment
5. **OpenBB Terminal** - Financial data analysis and market intelligence
6. **ShellGPT** - AI-powered business and development assistant (requires API key)
7. **Shellngn Pro** - Web-based remote access for business systems (port 8080)
8. **ML/AI Environment** - Comprehensive business intelligence and ML tools:
   - JupyterLab (port 8888) - Modern notebook interface
   - Jupyter Notebook (port 8888) - Classic notebook interface
   - TensorBoard (port 6006) - ML experiment visualization
   - Gradio Demo Server (port 7860) - Interactive ML model demos
   - Streamlit App Server (port 8501) - Data science web apps
   - MLflow UI (port 5000) - ML experiment tracking
   - Python ML REPL - Interactive Python environment

## 🌐 Port Configuration

| Port | Service | Description |
|------|---------|-------------|
| 5678 | n8n | Business workflow automation |
| 8080 | Shellngn Pro | Web-based remote access |
| 8888 | Jupyter | JupyterLab/Notebook interface |
| 6006 | TensorBoard | ML experiment visualization |
| 7860 | Gradio | Interactive ML model demos |
| 8501 | Streamlit | Data science web applications |
| 5000 | MLflow | ML experiment tracking UI |

## 🔧 DEBT Usage Examples

### Quick Environment Activation
```bash
# Activate DEBT Python environment
source ~/activate_debt_env.sh

# Verify installation
sgpt --version  # Should show ShellGPT 1.4.5
python -c "import pandas, sklearn, gradio, mlflow; print('✓ ML environment ready')"
node --version  # Should show v24.6.0
docker --version  # Docker support available
```

### Using ShellGPT for Business & Development
```bash
# Activate DEBT environment first
source ~/activate_debt_env.sh

# Set up API key (required for ShellGPT)
sgpt --install  # Follow prompts to configure API key

# Business Intelligence queries
sgpt "analyze sales data trends"
sgpt --code "create a python script for financial reporting"
sgpt --shell "find all business data files modified today"
sgpt "suggest automation workflows for business processes"
```

### Running ML/AI Services
```bash
# Start the interactive menu
./menu.sh

# Select option 8 (ML/AI Environment), then:
# 1 - JupyterLab (http://localhost:8888)
# 2 - Jupyter Notebook (http://localhost:8888)
# 3 - TensorBoard (http://localhost:6006)
# 4 - Gradio Demo Server (http://localhost:7860)
# 5 - Streamlit App Server (http://localhost:8501)
# 6 - MLflow UI (http://localhost:5000)
```

### Docker Usage
```bash
# Docker is installed and configured
# Note: You may need to restart your session for group changes to take effect
docker --version
docker-compose --version

# Start Docker service if needed
sudo systemctl start docker

# Build and run DEBT container
docker build -t debt_environment .
docker run -it -p 5678:5678 -p 8888:8888 debt_environment
```

## 🛠️ Manual Package Installation

If you prefer to install packages manually or need to troubleshoot:

### System Packages
```bash
# Arch Linux
sudo pacman -S base-devel curl wget unzip git sudo ripgrep fd python python-pip python-virtualenv tmux nodejs npm jq ca-certificates which github-cli docker docker-compose python-pipx

# Ubuntu/Debian
sudo apt-get install build-essential curl wget unzip git sudo ripgrep fd-find python3-pip python3-venv tmux nodejs npm jq ca-certificates software-properties-common gh docker.io docker-compose
```

### Python Environment Setup
```bash
# Create virtual environment
python -m venv ~/.debt-env
source ~/.debt-env/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install core packages
pip install shell-gpt jupyter jupyterlab notebook ipython

# Install data science packages
pip install pandas numpy matplotlib seaborn plotly scipy

# Install ML/AI packages
pip install scikit-learn mlflow tensorboard gradio streamlit

# Install web development packages
pip install fastapi uvicorn requests httpx pydantic

# Install utilities
pip install typer rich tqdm joblib
```

### Service Configuration
```bash
# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER

# Create activation script
echo '#!/bin/bash' > ~/activate_debt_env.sh
echo 'source ~/.debt-env/bin/activate' >> ~/activate_debt_env.sh
chmod +x ~/activate_debt_env.sh
```

## 🐛 Troubleshooting

### Node.js Package Conflicts (Arch Linux)
If you encounter Node.js package conflicts:
```bash
# The install script handles this automatically, but if manual resolution is needed:
sudo pacman -S nodejs  # This will prompt to remove conflicting packages
# Answer 'y' when asked to remove nodejs-lts-jod
```

### Virtual Environment Issues
If the virtual environment isn't working:
```bash
# Recreate the virtual environment
rm -rf ~/.debt-env
python -m venv ~/.debt-env
source ~/.debt-env/bin/activate
pip install --upgrade pip setuptools wheel
# Reinstall packages as needed
```

### Docker Permission Issues
If you get Docker permission errors:
```bash
# Add user to docker group (requires session restart)
sudo usermod -aG docker $USER
# Then logout and login again, or restart your session

# Verify docker group membership
groups $USER

# Start Docker service if needed
sudo systemctl start docker
sudo systemctl enable docker
```

### Python Package Installation Issues
If you encounter "externally-managed-environment" errors:
```bash
# This is normal on modern Linux distributions
# Use the virtual environment approach (already implemented in install script)
python -m venv ~/.debt-env
source ~/.debt-env/bin/activate
pip install <package-name>
```

### ShellGPT Configuration
If ShellGPT isn't working:
```bash
# Activate environment and configure API key
source ~/activate_debt_env.sh
sgpt --install
# Follow the prompts to set up your OpenAI API key
```

### Package Conflicts
If you encounter package conflicts during installation:
```bash
# Update system first
sudo pacman -Syu  # Arch Linux
sudo apt-get update && sudo apt-get upgrade  # Ubuntu/Debian

# Clear package cache if needed
sudo pacman -Sc --noconfirm  # Arch Linux
sudo apt-get autoclean  # Ubuntu/Debian

# Then run install script
./install-packages.sh
```

### Menu Script Issues
If the menu script doesn't work:
```bash
# Make sure it's executable
chmod +x menu.sh

# Check if all dependencies are available
which nvim node python docker

# Activate environment before running
source ~/activate_debt_env.sh
./menu.sh
```

## 📝 Important Notes

### System Compatibility
- ✅ **Fully tested on Arch Linux** with automatic Node.js conflict resolution
- ✅ **Supports Ubuntu/Debian** with distribution-specific package management
- ✅ **Cross-platform Docker support** for containerized deployment

### Installation Behavior
- **Node.js Conflicts:** The install script automatically resolves Node.js package conflicts on Arch Linux
- **Python Environment:** Uses virtual environment (PEP 668 compliant) to prevent system package conflicts
- **OpenBB Installation:** May fail due to complex dependencies - this is expected and doesn't affect other functionality
- **Docker Group:** Membership changes require session restart to take effect

### Environment Management
- **Virtual Environment Location:** `~/.debt-env/` (not `~/.nvim_env`)
- **Activation Script:** `~/activate_debt_env.sh` for easy environment activation
- **Package Isolation:** All Python packages are installed in virtual environment for system safety
- **Service Ports:** All web services use non-conflicting port assignments

### Performance & Resource Usage
- **ML/AI Tools:** TensorBoard, MLflow, and Jupyter require adequate system resources
- **Docker Services:** Multiple containers may require significant RAM and CPU
- **Node.js Applications:** n8n and other Node.js tools benefit from Node.js v24.6.0 performance improvements

## 🎯 DEBT Docker Support

DEBT includes comprehensive Docker support for containerized business environments with full port mapping:

### Container Deployment
```bash
# Build the DEBT Docker image
docker build -t debt_environment .

# Run with all service ports exposed
docker run -it \
  -p 5678:5678 \
  -p 8080:8080 \
  -p 8888:8888 \
  -p 6006:6006 \
  -p 7860:7860 \
  -p 8501:8501 \
  -p 5000:5000 \
  --name debt_container \
  debt_environment
```

### Docker Compose (if available)
```yaml
# docker-compose.yml example
version: '3.8'
services:
  debt:
    build: .
    ports:
      - "5678:5678"   # n8n
      - "8080:8080"   # Shellngn Pro
      - "8888:8888"   # Jupyter
      - "6006:6006"   # TensorBoard
      - "7860:7860"   # Gradio
      - "8501:8501"   # Streamlit
      - "5000:5000"   # MLflow
    volumes:
      - ./data:/home/devuser/data
    environment:
      - DISPLAY=${DISPLAY}
```

### Container Management
```bash
# Start existing container
docker start debt_container

# Access running container
docker exec -it debt_container /bin/bash

# View container logs
docker logs debt_container

# Stop container
docker stop debt_container
```

## 🤝 Contributing to DEBT

We welcome contributions to enhance DEBT's capabilities! This project aims to provide the most comprehensive business-focused development environment available.

### Areas for Contribution
- 🔧 **System Integration:** Cross-platform compatibility improvements
- 🤖 **AI/ML Tools:** Additional ML frameworks and model serving capabilities
- 💼 **Business Intelligence:** Enhanced financial analysis and reporting tools
- 🔄 **Automation:** New workflow automation patterns and integrations
- 📊 **Data Science:** Advanced analytics and visualization components
- 🐳 **Containerization:** Docker optimization and orchestration improvements

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Test on both Arch Linux and Ubuntu (if possible)
4. Ensure virtual environment compatibility
5. Update documentation and README
6. Submit a pull request

### Testing Guidelines
- Test package installation on clean systems
- Verify all menu options work correctly
- Check Docker container functionality
- Validate Python virtual environment isolation
- Test Node.js conflict resolution on Arch Linux

### Issue Reporting
When reporting issues, please include:
- Operating system and version
- Installation method used
- Error messages and logs
- Steps to reproduce
- Expected vs actual behavior

DEBT is designed to be the ultimate development environment for business intelligence, financial analysis, ML/AI research, and automation tasks. Every contribution helps make it more powerful and accessible!

---

## 📋 Installation Checklist

### Pre-Installation
- [ ] Linux system (Arch Linux or Ubuntu/Debian)
- [ ] Git installed
- [ ] Internet connection available
- [ ] Sudo privileges

### Post-Installation Verification
- [ ] `source ~/activate_debt_env.sh` works
- [ ] `sgpt --version` shows ShellGPT 1.4.5
- [ ] `node --version` shows v24.6.0+
- [ ] `docker --version` works (after session restart)
- [ ] `./menu.sh` launches successfully
- [ ] Python imports work: `python -c "import pandas, sklearn, gradio"`
- [ ] JupyterLab accessible at http://localhost:8888

### Optional Configuration
- [ ] ShellGPT API key configured (`sgpt --install`)
- [ ] Docker service started (`sudo systemctl start docker`)
- [ ] User logged out/in for docker group membership

---

**DEBT v2024** - Your comprehensive development environment for business intelligence, ML/AI, and automation. 🚀
