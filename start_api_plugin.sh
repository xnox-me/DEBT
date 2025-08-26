#!/bin/bash

# DEBT API Plugin Startup Script
# Unified API gateway for all DEBT business intelligence capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Header
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          🌐 DEBT API Plugin - Business Intelligence Gateway       ║
║                                                                  ║
║     Unified API for Financial Analysis • ML • Business Intelligence ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Get script directory and DEBT root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEBT_ROOT="$SCRIPT_DIR"

echo -e "${CYAN}📂 DEBT Directory: $DEBT_ROOT${NC}"

# Function to check DEBT environment
check_debt_environment() {
    echo -e "\n${PURPLE}▶ Checking DEBT Environment${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..35})${NC}"
    
    # Check if DEBT environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${YELLOW}⚠️  DEBT environment not activated. Attempting activation...${NC}"
        
        if [ -f "$HOME/.debt-env/bin/activate" ]; then
            source "$HOME/.debt-env/bin/activate"
            echo -e "${GREEN}✅ DEBT environment activated${NC}"
        else
            echo -e "${RED}❌ DEBT environment not found${NC}"
            echo -e "${YELLOW}Please install DEBT first:${NC}"
            echo -e "${CYAN}  cd $DEBT_ROOT${NC}"
            echo -e "${CYAN}  chmod +x install-packages.sh${NC}"
            echo -e "${CYAN}  sudo ./install-packages.sh${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ DEBT environment active: $VIRTUAL_ENV${NC}"
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '(?<=Python )[0-9.]+')
    echo -e "${BLUE}🐍 Python version: $PYTHON_VERSION${NC}"
}

# Function to install plugin dependencies
install_dependencies() {
    echo -e "\n${PURPLE}▶ Installing API Plugin Dependencies${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..40})${NC}"
    
    # Check and install required packages
    REQUIRED_PACKAGES=("fastapi" "uvicorn" "aiohttp" "pydantic" "yfinance")
    MISSING_PACKAGES=()
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}  ✅ $package${NC}"
        else
            echo -e "${RED}  ❌ $package${NC}"
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    # Install missing packages
    if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
        echo -e "\n${YELLOW}📦 Installing missing packages: ${MISSING_PACKAGES[*]}${NC}"
        pip install "${MISSING_PACKAGES[@]}"
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ All dependencies satisfied${NC}"
    fi
}

# Function to setup plugin configuration
setup_plugin_config() {
    echo -e "\n${PURPLE}▶ Setting Up Plugin Configuration${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..40})${NC}"
    
    # Create plugin directory structure
    PLUGIN_DIR="$DEBT_ROOT/plugins/api_plugin"
    mkdir -p "$PLUGIN_DIR"
    mkdir -p "$DEBT_ROOT/logs"
    
    # Create plugin configuration if it doesn't exist
    CONFIG_FILE="$PLUGIN_DIR/config.json"
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${CYAN}📝 Creating plugin configuration...${NC}"
        python "$DEBT_ROOT/api_plugin_config.py" > /dev/null 2>&1 || true
    fi
    
    # Set environment variables
    export DEBT_API_HOST=0.0.0.0
    export DEBT_API_PORT=9000
    export DEBT_API_DEBUG=false
    export DEBT_ROOT_DIR="$DEBT_ROOT"
    
    echo -e "${GREEN}✅ Plugin configuration ready${NC}"
    echo -e "${CYAN}📁 Plugin directory: $PLUGIN_DIR${NC}"
}

# Function to check port availability
check_port_availability() {
    local port=$1
    local service_name=$2
    
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        
        # Try to identify what's using the port
        local process=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$process" ]; then
            local process_name=$(ps -p $process -o comm= 2>/dev/null || echo "unknown")
            echo -e "${CYAN}   Process: $process_name (PID: $process)${NC}"
            
            # Ask user if they want to continue
            read -p "Do you want to continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}❌ Startup cancelled${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${GREEN}✅ Port $port available for $service_name${NC}"
    fi
}

# Function to start the API plugin
start_api_plugin() {
    echo -e "\n${PURPLE}▶ Starting DEBT API Plugin${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..35})${NC}"
    
    # Check port availability
    check_port_availability 9000 "API Plugin"
    
    # Start the API plugin
    echo -e "${BLUE}🚀 Starting API gateway on port 9000...${NC}"
    
    # Change to DEBT root directory
    cd "$DEBT_ROOT"
    
    # Start the plugin with proper logging
    LOG_FILE="$DEBT_ROOT/logs/api_plugin.log"
    
    echo -e "${CYAN}📝 Logging to: $LOG_FILE${NC}"
    
    # Start in background or foreground based on user preference
    if [ "$1" = "--background" ] || [ "$1" = "-bg" ]; then
        echo -e "${BLUE}🔄 Starting in background mode...${NC}"
        nohup python api_plugin.py > "$LOG_FILE" 2>&1 &
        API_PLUGIN_PID=$!
        echo "$API_PLUGIN_PID" > "$DEBT_ROOT/logs/api_plugin.pid"
        echo -e "${GREEN}✅ API Plugin started in background (PID: $API_PLUGIN_PID)${NC}"
        
        # Wait a moment and check if it's running
        sleep 3
        if kill -0 $API_PLUGIN_PID 2>/dev/null; then
            echo -e "${GREEN}✅ API Plugin running successfully${NC}"
        else
            echo -e "${RED}❌ API Plugin failed to start${NC}"
            cat "$LOG_FILE"
            exit 1
        fi
    else
        echo -e "${BLUE}🔄 Starting in foreground mode...${NC}"
        echo -e "${YELLOW}💡 Press Ctrl+C to stop the API Plugin${NC}"
        exec python api_plugin.py
    fi
}

# Function to display service information
show_service_info() {
    echo -e "\n${GREEN}🎉 DEBT API Plugin Started Successfully!${NC}"
    echo -e "${GREEN}=============================================${NC}"
    
    echo -e "\n${BLUE}🌐 API Gateway Information:${NC}"
    echo -e "${CYAN}  📡 Base URL:           http://localhost:9000${NC}"
    echo -e "${CYAN}  📚 API Documentation:  http://localhost:9000/api/docs${NC}"
    echo -e "${CYAN}  📖 ReDoc:             http://localhost:9000/api/redoc${NC}"
    echo -e "${CYAN}  🔍 Health Check:      http://localhost:9000/api/health${NC}"
    
    echo -e "\n${BLUE}🚀 Available API Endpoints:${NC}"
    echo -e "${YELLOW}  Financial Analysis:${NC}"
    echo -e "${CYAN}    GET  /api/financial/market/{symbol}     - Market data${NC}"
    echo -e "${CYAN}    GET  /api/financial/portfolio           - Portfolio analysis${NC}"
    
    echo -e "\n${YELLOW}  Machine Learning:${NC}"
    echo -e "${CYAN}    POST /api/ml/predict/churn             - Customer churn prediction${NC}"
    echo -e "${CYAN}    POST /api/ml/predict/sales             - Sales forecasting${NC}"
    
    echo -e "\n${YELLOW}  Business Intelligence:${NC}"
    echo -e "${CYAN}    GET  /api/business/kpis                - Business KPIs${NC}"
    echo -e "${CYAN}    GET  /api/analytics/dashboard/{type}   - Dashboard data${NC}"
    
    echo -e "\n${YELLOW}  Service Management:${NC}"
    echo -e "${CYAN}    GET  /api/services                     - Service status${NC}"
    echo -e "${CYAN}    POST /api/services/start/{service}     - Start service${NC}"
    echo -e "${CYAN}    POST /api/services/stop/{service}      - Stop service${NC}"
    
    echo -e "\n${YELLOW}  Workflow Automation:${NC}"
    echo -e "${CYAN}    GET  /api/workflows/status             - Workflow status${NC}"
    echo -e "${CYAN}    POST /api/workflows/trigger/{name}     - Trigger workflow${NC}"
    
    echo -e "\n${BLUE}🔗 Integrated DEBT Services:${NC}"
    echo -e "${GREEN}  ✓ Financial Dashboard  (Port 8501)${NC}"
    echo -e "${GREEN}  ✓ ML Interface         (Port 7860)${NC}"
    echo -e "${GREEN}  ✓ MLflow Tracking      (Port 5000)${NC}"
    echo -e "${GREEN}  ✓ JupyterLab          (Port 8888)${NC}"
    echo -e "${GREEN}  ✓ n8n Workflows       (Port 5678)${NC}"
    echo -e "${GREEN}  ✓ API Services         (Port 8000)${NC}"
    
    echo -e "\n${PURPLE}💡 Quick Test Commands:${NC}"
    echo -e "${YELLOW}  # Check API health${NC}"
    echo -e "${CYAN}  curl http://localhost:9000/api/health${NC}"
    
    echo -e "\n${YELLOW}  # Get market data${NC}"
    echo -e "${CYAN}  curl http://localhost:9000/api/financial/market/AAPL${NC}"
    
    echo -e "\n${YELLOW}  # Get business KPIs${NC}"
    echo -e "${CYAN}  curl http://localhost:9000/api/business/kpis${NC}"
    
    echo -e "\n${BLUE}📊 Business Intelligence Features:${NC}"
    echo -e "${GREEN}  • Real-time financial market analysis${NC}"
    echo -e "${GREEN}  • ML-powered customer and sales predictions${NC}"
    echo -e "${GREEN}  • Comprehensive business KPI monitoring${NC}"
    echo -e "${GREEN}  • Automated workflow management${NC}"
    echo -e "${GREEN}  • Service orchestration and monitoring${NC}"
    echo -e "${GREEN}  • Advanced analytics and reporting${NC}"
}

# Function to cleanup and stop
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping DEBT API Plugin...${NC}"
    
    # Kill API plugin if running in background
    if [ -f "$DEBT_ROOT/logs/api_plugin.pid" ]; then
        PID=$(cat "$DEBT_ROOT/logs/api_plugin.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            echo -e "${GREEN}✅ API Plugin stopped (PID: $PID)${NC}"
        fi
        rm -f "$DEBT_ROOT/logs/api_plugin.pid"
    fi
    
    echo -e "${BLUE}👋 DEBT API Plugin shutdown complete${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo -e "${CYAN}Starting DEBT API Plugin initialization...${NC}\n"
    
    check_debt_environment
    install_dependencies
    setup_plugin_config
    start_api_plugin "$@"
    show_service_info
    
    # If running in foreground, wait for interrupt
    if [ "$1" != "--background" ] && [ "$1" != "-bg" ]; then
        echo -e "\n${YELLOW}🔄 API Plugin is running. Press Ctrl+C to stop...${NC}"
        while true; do
            sleep 1
        done
    fi
}

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "DEBT API Plugin Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --background, -bg    Start in background mode"
    echo "  --help, -h          Show this help message"
    echo ""
    echo "The API Plugin provides a unified gateway for all DEBT capabilities:"
    echo "  • Financial market analysis and portfolio management"
    echo "  • Machine learning predictions and business intelligence"
    echo "  • Service management and workflow automation"
    echo "  • Advanced analytics and real-time monitoring"
    echo ""
    echo "Default API URL: http://localhost:9000"
    echo "Documentation: http://localhost:9000/api/docs"
    exit 0
fi

# Run main function
main "$@"