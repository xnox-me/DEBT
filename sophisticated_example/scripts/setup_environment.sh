#!/bin/bash

# DEBT Sophisticated Example Setup Script
# Complete setup and configuration for the sophisticated business intelligence suite

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    🏦 DEBT Sophisticated Business Intelligence Suite          ║
║                                                               ║
║    Advanced ML • Financial Analysis • Business Intelligence   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}Setting up comprehensive business intelligence platform...${NC}\n"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📍 Project Directory: $PROJECT_ROOT${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print step header
print_step() {
    echo -e "\n${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..60})${NC}"
}

# Function to check and activate DEBT environment
setup_environment() {
    print_step "Setting Up Python Environment"
    
    # Check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${YELLOW}⚠️  Not in a virtual environment. Checking for DEBT environment...${NC}"
        
        # Try to activate DEBT environment
        if [ -f "$HOME/.debt-env/bin/activate" ]; then
            source "$HOME/.debt-env/bin/activate"
            echo -e "${GREEN}✅ DEBT environment activated${NC}"
        else
            echo -e "${RED}❌ DEBT environment not found.${NC}"
            echo -e "${YELLOW}Please run the main DEBT installation first:${NC}"
            echo -e "${CYAN}  cd ../..${NC}"
            echo -e "${CYAN}  chmod +x install-packages.sh${NC}"
            echo -e "${CYAN}  sudo ./install-packages.sh${NC}"
            echo -e "${CYAN}  source activate_debt_env.sh${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Virtual environment already active: $VIRTUAL_ENV${NC}"
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '(?<=Python )[0-9.]+')
    echo -e "${BLUE}🐍 Using Python $PYTHON_VERSION${NC}"
}

# Function to install Python dependencies
install_dependencies() {
    print_step "Installing Python Dependencies"
    
    echo -e "${BLUE}📦 Installing comprehensive ML and business intelligence packages...${NC}"
    
    # Core requirements for sophisticated example
    PACKAGES=(
        # Data Science Core
        "pandas>=2.0.0"
        "numpy>=1.24.0"
        "scipy>=1.10.0"
        
        # Machine Learning
        "scikit-learn>=1.3.0"
        "xgboost>=2.0.0"
        "lightgbm>=4.0.0"
        
        # Visualization & Web Apps
        "plotly>=5.15.0"
        "matplotlib>=3.7.0"
        "seaborn>=0.12.0"
        "streamlit>=1.28.0"
        "gradio>=4.0.0"
        
        # Financial Data
        "yfinance>=0.2.0"
        
        # Web Services
        "fastapi>=0.104.0"
        "uvicorn>=0.24.0"
        
        # MLOps
        "mlflow>=2.8.0"
        "tensorboard>=2.15.0"
        
        # Jupyter
        "jupyter>=1.0.0"
        "jupyterlab>=4.0.0"
        
        # Utilities
        "requests>=2.31.0"
        "python-dotenv>=1.0.0"
        "rich>=13.6.0"
    )
    
    # Check installed packages
    echo -e "${BLUE}🔍 Checking installed packages...${NC}"
    MISSING_PACKAGES=()
    
    for package in "${PACKAGES[@]}"; do
        package_name=$(echo $package | cut -d'>' -f1 | cut -d'=' -f1)
        if python -c "import $package_name" 2>/dev/null; then
            echo -e "${GREEN}  ✅ $package_name${NC}"
        else
            echo -e "${RED}  ❌ $package_name${NC}"
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    # Install missing packages
    if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
        echo -e "\n${YELLOW}📥 Installing missing packages...${NC}"
        pip install "${MISSING_PACKAGES[@]}"
        echo -e "${GREEN}✅ All packages installed successfully${NC}"
    else
        echo -e "${GREEN}✅ All required packages already installed${NC}"
    fi
}

# Function to create configuration files
setup_configuration() {
    print_step "Setting Up Configuration"
    
    # Create config directory
    CONFIG_DIR="$PROJECT_ROOT/config"
    mkdir -p "$CONFIG_DIR"
    
    # Create environment configuration
    cat > "$CONFIG_DIR/.env" << EOF
# DEBT Sophisticated Example Configuration
# Environment variables for business intelligence suite

# API Configuration
DEBT_API_HOST=0.0.0.0
DEBT_API_PORT=8000
DEBT_DEBUG=true

# MLflow Configuration  
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=DEBT_Business_Intelligence

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Gradio Configuration
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0

# JupyterLab Configuration
JUPYTER_PORT=8888
JUPYTER_IP=0.0.0.0

# Business Intelligence Settings
DEFAULT_ANALYSIS_PERIOD=1y
MAX_CONCURRENT_REQUESTS=10
CACHE_DURATION=300

# Financial Data APIs (Optional - add your API keys)
# ALPHA_VANTAGE_API_KEY=your_key_here
# OPENBB_API_KEY=your_key_here
# FRED_API_KEY=your_key_here

# Security Settings
DEBT_SECRET_KEY=$(openssl rand -hex 32)
API_RATE_LIMIT=100
EOF
    
    echo -e "${GREEN}✅ Configuration files created${NC}"
    
    # Create Streamlit config
    mkdir -p "$PROJECT_ROOT/financial_dashboard/.streamlit"
    cat > "$PROJECT_ROOT/financial_dashboard/.streamlit/config.toml" << EOF
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"
font = "sans serif"
EOF

    echo -e "${GREEN}✅ Streamlit configuration created${NC}"
}

# Function to initialize directories and sample data
setup_data_directories() {
    print_step "Setting Up Data Directories"
    
    # Create necessary directories
    DIRECTORIES=(
        "$PROJECT_ROOT/data/raw"
        "$PROJECT_ROOT/data/processed" 
        "$PROJECT_ROOT/data/models"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/temp"
        "$PROJECT_ROOT/exports"
    )
    
    for dir in "${DIRECTORIES[@]}"; do
        mkdir -p "$dir"
        echo -e "${GREEN}✅ Created: $(basename "$dir")${NC}"
    done
    
    # Create sample business data file
    cat > "$PROJECT_ROOT/data/raw/sample_business_metrics.json" << EOF
{
    "business_kpis": {
        "total_customers": 5000,
        "monthly_revenue": 375000,
        "avg_customer_ltv": 2400,
        "churn_rate": 0.12,
        "satisfaction_score": 7.8,
        "high_value_customers": 750
    },
    "regional_performance": {
        "North": {"revenue": 125000, "customers": 1500, "satisfaction": 8.1},
        "South": {"revenue": 95000, "customers": 1250, "satisfaction": 7.6},
        "East": {"revenue": 87500, "customers": 1250, "satisfaction": 7.5},
        "West": {"revenue": 67500, "customers": 1000, "satisfaction": 8.0}
    }
}
EOF
    
    echo -e "${GREEN}✅ Sample business data created${NC}"
}

# Function to test all services
test_services() {
    print_step "Testing Service Configurations"
    
    echo -e "${BLUE}🧪 Running service configuration tests...${NC}"
    
    # Test Python imports
    echo -e "${CYAN}Testing Python package imports...${NC}"
    
    python -c "
import pandas as pd
import numpy as np
import streamlit as st
import gradio as gr
import fastapi
import mlflow
import plotly.graph_objects as go
import yfinance as yf
import sklearn
import xgboost
import lightgbm
print('✅ All core packages import successfully')
" || {
        echo -e "${RED}❌ Package import test failed${NC}"
        exit 1
    }
    
    # Test file permissions
    echo -e "${CYAN}Checking file permissions...${NC}"
    
    EXECUTABLE_FILES=(
        "$PROJECT_ROOT/financial_dashboard/start_dashboard.sh"
        "$PROJECT_ROOT/ml_pipeline/start_ml_services.sh"
        "$SCRIPT_DIR/setup_environment.sh"
    )
    
    for file in "${EXECUTABLE_FILES[@]}"; do
        if [ -x "$file" ]; then
            echo -e "${GREEN}✅ $(basename "$file") is executable${NC}"
        else
            echo -e "${YELLOW}⚠️ Making $(basename "$file") executable${NC}"
            chmod +x "$file"
        fi
    done
    
    echo -e "${GREEN}✅ All service tests passed${NC}"
}

# Function to create startup scripts
create_startup_scripts() {
    print_step "Creating Master Startup Scripts"
    
    # Create master startup script
    cat > "$PROJECT_ROOT/start_all_services.sh" << 'EOF'
#!/bin/bash

# DEBT Sophisticated Example - Master Startup Script
# Launches all business intelligence services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting DEBT Business Intelligence Suite${NC}"
echo -e "${BLUE}==========================================${NC}"

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check DEBT environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -f "$HOME/.debt-env/bin/activate" ]; then
        source "$HOME/.debt-env/bin/activate"
        echo -e "${GREEN}✅ DEBT environment activated${NC}"
    else
        echo -e "${RED}❌ DEBT environment not found${NC}"
        exit 1
    fi
fi

# Function to start service in background
start_service() {
    local service_name=$1
    local start_command=$2
    local port=$3
    local log_file="$PROJECT_DIR/logs/${service_name}.log"
    
    echo -e "${BLUE}🔄 Starting $service_name...${NC}"
    
    # Create log directory if it doesn't exist
    mkdir -p "$PROJECT_DIR/logs"
    
    # Start service
    eval "$start_command" > "$log_file" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if service started
    sleep 3
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✅ $service_name started (PID: $pid, Port: $port)${NC}"
        echo $pid > "$PROJECT_DIR/logs/${service_name}.pid"
    else
        echo -e "${RED}❌ $service_name failed to start${NC}"
        cat "$log_file"
    fi
}

# Start services
echo -e "\n${BLUE}📊 Starting Business Intelligence Services...${NC}"

# 1. MLflow Tracking Server
start_service "MLflow" "cd $PROJECT_DIR/ml_pipeline && mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0 --port 5000" "5000"

# 2. FastAPI Business Services
start_service "API-Services" "cd $PROJECT_DIR/api_services && python main.py" "8000"

# 3. Streamlit Financial Dashboard
start_service "Financial-Dashboard" "cd $PROJECT_DIR/financial_dashboard && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true" "8501"

# 4. Gradio ML Interface
start_service "ML-Interface" "cd $PROJECT_DIR/gradio_demos && python business_ml_interface.py" "7860"

# 5. JupyterLab (optional)
if command -v jupyter-lab >/dev/null 2>&1; then
    start_service "JupyterLab" "cd $PROJECT_DIR/analytics_notebooks && jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root" "8888"
fi

# Summary
echo -e "\n${GREEN}🎉 DEBT Business Intelligence Suite Started!${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "${BLUE}📊 Available Services:${NC}"
echo -e "${CYAN}  🔬 MLflow Tracking:      http://localhost:5000${NC}"
echo -e "${CYAN}  🌐 API Services:         http://localhost:8000/docs${NC}"
echo -e "${CYAN}  📈 Financial Dashboard:  http://localhost:8501${NC}"
echo -e "${CYAN}  🤖 ML Interface:         http://localhost:7860${NC}"
echo -e "${CYAN}  📓 JupyterLab:           http://localhost:8888${NC}"

echo -e "\n${YELLOW}💡 Use './stop_all_services.sh' to stop all services${NC}"
echo -e "${YELLOW}💡 Check logs in ./logs/ directory for troubleshooting${NC}"

# Keep script running
echo -e "\n${BLUE}✨ All services are running. Press Ctrl+C to stop all services...${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping all services...${NC}"
    
    # Kill all background processes
    if [ -d "$PROJECT_DIR/logs" ]; then
        for pidfile in "$PROJECT_DIR/logs"/*.pid; do
            if [ -f "$pidfile" ]; then
                pid=$(cat "$pidfile")
                service_name=$(basename "$pidfile" .pid)
                if kill -0 $pid 2>/dev/null; then
                    kill $pid
                    echo -e "${GREEN}✅ Stopped $service_name (PID: $pid)${NC}"
                fi
                rm -f "$pidfile"
            fi
        done
    fi
    
    # Kill any remaining processes
    pkill -f "streamlit run" 2>/dev/null || true
    pkill -f "gradio" 2>/dev/null || true
    pkill -f "mlflow server" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "jupyter-lab" 2>/dev/null || true
    
    echo -e "${BLUE}👋 All services stopped. Goodbye!${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for interrupt
while true; do
    sleep 1
done
EOF
    
    # Make startup script executable
    chmod +x "$PROJECT_ROOT/start_all_services.sh"
    
    # Create stop script
    cat > "$PROJECT_ROOT/stop_all_services.sh" << 'EOF'
#!/bin/bash

# DEBT Sophisticated Example - Stop All Services Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping DEBT Business Intelligence Services${NC}"
echo -e "${BLUE}===============================================${NC}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop services using PID files
if [ -d "$PROJECT_DIR/logs" ]; then
    for pidfile in "$PROJECT_DIR/logs"/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            service_name=$(basename "$pidfile" .pid)
            if kill -0 $pid 2>/dev/null; then
                kill $pid
                echo -e "${GREEN}✅ Stopped $service_name (PID: $pid)${NC}"
            else
                echo -e "${YELLOW}⚠️ $service_name was not running${NC}"
            fi
            rm -f "$pidfile"
        fi
    done
fi

# Kill any remaining processes
echo -e "${BLUE}🧹 Cleaning up remaining processes...${NC}"
pkill -f "streamlit run" 2>/dev/null || true
pkill -f "gradio" 2>/dev/null || true  
pkill -f "mlflow server" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "jupyter-lab" 2>/dev/null || true

echo -e "${GREEN}✅ All DEBT services stopped${NC}"
EOF
    
    chmod +x "$PROJECT_ROOT/stop_all_services.sh"
    
    echo -e "${GREEN}✅ Master startup and stop scripts created${NC}"
}

# Function to display final instructions
show_final_instructions() {
    print_step "Setup Complete - Next Steps"
    
    echo -e "${GREEN}🎉 DEBT Sophisticated Example Setup Complete!${NC}\n"
    
    echo -e "${BLUE}📋 Quick Start Guide:${NC}"
    echo -e "${CYAN}  1. Start all services:${NC}"
    echo -e "${YELLOW}     ./start_all_services.sh${NC}\n"
    
    echo -e "${CYAN}  2. Access the services:${NC}"
    echo -e "${YELLOW}     🔬 MLflow Tracking:      http://localhost:5000${NC}"
    echo -e "${YELLOW}     🌐 API Services:         http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}     📈 Financial Dashboard:  http://localhost:8501${NC}"
    echo -e "${YELLOW}     🤖 ML Interface:         http://localhost:7860${NC}"
    echo -e "${YELLOW}     📓 JupyterLab:           http://localhost:8888${NC}\n"
    
    echo -e "${CYAN}  3. Individual service startup:${NC}"
    echo -e "${YELLOW}     Financial Dashboard:  cd financial_dashboard && ./start_dashboard.sh${NC}"
    echo -e "${YELLOW}     ML Pipeline & Gradio: cd ml_pipeline && ./start_ml_services.sh${NC}"
    echo -e "${YELLOW}     API Services:         cd api_services && python main.py${NC}\n"
    
    echo -e "${CYAN}  4. Stop all services:${NC}"
    echo -e "${YELLOW}     ./stop_all_services.sh${NC}\n"
    
    echo -e "${BLUE}📊 What You Can Do:${NC}"
    echo -e "${GREEN}  ✓ Advanced financial market analysis with real-time data${NC}"
    echo -e "${GREEN}  ✓ Machine learning predictions for business intelligence${NC}"
    echo -e "${GREEN}  ✓ Customer churn analysis and sales forecasting${NC}"
    echo -e "${GREEN}  ✓ Interactive business dashboards and KPI monitoring${NC}"
    echo -e "${GREEN}  ✓ Comprehensive business analytics with JupyterLab${NC}"
    echo -e "${GREEN}  ✓ RESTful API services for business data integration${NC}\n"
    
    echo -e "${PURPLE}🔧 Configuration:${NC}"
    echo -e "${YELLOW}  📁 Configuration files: ./config/${NC}"
    echo -e "${YELLOW}  📊 Sample data: ./data/${NC}"
    echo -e "${YELLOW}  📝 Logs: ./logs/${NC}\n"
    
    echo -e "${BLUE}💡 Pro Tips:${NC}"
    echo -e "${CYAN}  • Train ML models first: cd ml_pipeline && python train_models.py${NC}"
    echo -e "${CYAN}  • Customize business data in data/raw/ directory${NC}"
    echo -e "${CYAN}  • Add your API keys to config/.env for enhanced features${NC}"
    echo -e "${CYAN}  • Use individual service scripts for development${NC}\n"
    
    echo -e "${GREEN}🚀 Ready to explore advanced business intelligence with DEBT!${NC}"
}

# Main setup execution
main() {
    echo -e "${BLUE}Starting DEBT Sophisticated Example setup...${NC}\n"
    
    setup_environment
    install_dependencies
    setup_configuration  
    setup_data_directories
    test_services
    create_startup_scripts
    show_final_instructions
    
    echo -e "\n${GREEN}✨ Setup completed successfully! Ready to launch business intelligence suite.${NC}"
}

# Run main setup
main "$@"