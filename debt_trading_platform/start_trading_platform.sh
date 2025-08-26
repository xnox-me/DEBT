#!/bin/bash

# DEBT Django Trading Platform Startup Script

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
║          🚀 DEBT Django Trading Platform                          ║
║                                                                  ║
║     The Ultimate Trading Experience - TASI • Global • ML • AI   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEBT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}📂 DEBT Root: $DEBT_ROOT${NC}"
echo -e "${CYAN}📂 Django Project: $SCRIPT_DIR${NC}"

# Function to check DEBT environment
check_debt_environment() {
    echo -e "\n${PURPLE}▶ Checking DEBT Environment${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..35})${NC}"
    
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${YELLOW}⚠️  DEBT environment not activated. Attempting activation...${NC}"
        
        if [ -f "$HOME/.debt-env/bin/activate" ]; then
            source "$HOME/.debt-env/bin/activate"
            echo -e "${GREEN}✅ DEBT environment activated${NC}"
        else
            echo -e "${RED}❌ DEBT environment not found${NC}"
            echo -e "${YELLOW}Please activate DEBT first:${NC}"
            echo -e "${CYAN}  cd $DEBT_ROOT${NC}"
            echo -e "${CYAN}  source activate_debt_env.sh${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ DEBT environment active: $VIRTUAL_ENV${NC}"
    fi
}

# Function to install additional dependencies
install_dependencies() {
    echo -e "\n${PURPLE}▶ Installing Trading Platform Dependencies${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..45})${NC}"
    
    # Additional packages for trading features
    TRADING_PACKAGES=("channels-redis" "django-bootstrap4" "whitenoise")
    MISSING_PACKAGES=()
    
    for package in "${TRADING_PACKAGES[@]}"; do
        if python -c "import ${package//-/_}" 2>/dev/null; then
            echo -e "${GREEN}  ✅ $package${NC}"
        else
            echo -e "${RED}  ❌ $package${NC}"
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
        echo -e "\n${YELLOW}📦 Installing missing packages: ${MISSING_PACKAGES[*]}${NC}"
        pip install "${MISSING_PACKAGES[@]}"
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ All trading dependencies satisfied${NC}"
    fi
}

# Function to setup database
setup_database() {
    echo -e "\n${PURPLE}▶ Setting Up Database${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..25})${NC}"
    
    # Run migrations
    echo -e "${CYAN}📊 Running migrations...${NC}"
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    echo -e "${CYAN}👤 Checking for superuser...${NC}"
    if python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@debt.com', 'debt123')
    print('Superuser created: admin/debt123')
else:
    print('Superuser already exists')
" 2>/dev/null; then
        echo -e "${GREEN}✅ Superuser configured${NC}"
    fi
}

# Function to check port availability
check_port_availability() {
    local port=$1
    local service_name=$2
    
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        
        local process=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$process" ]; then
            local process_name=$(ps -p $process -o comm= 2>/dev/null || echo "unknown")
            echo -e "${CYAN}   Process: $process_name (PID: $process)${NC}"
            
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

# Function to start the Django server
start_django_server() {
    echo -e "\n${PURPLE}▶ Starting Django Trading Platform${NC}"
    echo -e "${PURPLE}$(printf '%.0s─' {1..40})${NC}"
    
    # Check port availability
    check_port_availability 8000 "Django Trading Platform"
    
    echo -e "${BLUE}🚀 Starting Django development server...${NC}"
    echo -e "${CYAN}📡 Server will be available at: http://localhost:8000${NC}"
    echo -e "${CYAN}🔧 Admin interface: http://localhost:8000/admin${NC}"
    echo -e "${CYAN}📊 API endpoints: http://localhost:8000/api/${NC}"
    echo -e "${CYAN}📈 Markets API: http://localhost:8000/api/markets/${NC}"
    
    echo -e "\n${GREEN}🎉 DEBT Django Trading Platform Ready!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo -e "\n${BLUE}🌟 Features Available:${NC}"
    echo -e "${YELLOW}  📊 TASI Market Intelligence${NC}"
    echo -e "${YELLOW}  🌍 Global Markets (9+ countries)${NC}"
    echo -e "${YELLOW}  💰 Cryptocurrency Markets${NC}"
    echo -e "${YELLOW}  🥇 Precious Metals Trading${NC}"
    echo -e "${YELLOW}  🤖 ML Trading Signals${NC}"
    echo -e "${YELLOW}  📈 Portfolio Management${NC}"
    echo -e "${YELLOW}  🔔 Real-time Alerts${NC}"
    echo -e "${YELLOW}  📊 Advanced Charts${NC}"
    
    echo -e "\n${BLUE}🚀 API Examples:${NC}"
    echo -e "${CYAN}  # Get TASI overview${NC}"
    echo -e "${CYAN}  curl http://localhost:8000/api/markets/api/tasi/overview/${NC}"
    
    echo -e "\n${CYAN}  # Get global markets${NC}"
    echo -e "${CYAN}  curl http://localhost:8000/api/markets/api/global/overview/${NC}"
    
    echo -e "\n${CYAN}  # Get stock quote${NC}"
    echo -e "${CYAN}  curl http://localhost:8000/api/markets/api/quote/AAPL/${NC}"
    
    echo -e "\n${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
    echo -e "\n"
    
    # Start Django development server
    python manage.py runserver 0.0.0.0:8000
}

# Function to show service information
show_service_info() {
    echo -e "\n${GREEN}🌟 DEBT Trading Platform Information${NC}"
    echo -e "${GREEN}======================================${NC}"
    
    echo -e "\n${BLUE}🎯 Trading Features:${NC}"
    echo -e "${GREEN}  ✓ TASI Stock Exchange Integration${NC}"
    echo -e "${GREEN}  ✓ Global Markets (USA, UK, China, Japan, etc.)${NC}"
    echo -e "${GREEN}  ✓ Cryptocurrency Trading (BTC, ETH, etc.)${NC}"
    echo -e "${GREEN}  ✓ Precious Metals (Gold, Silver futures)${NC}"
    echo -e "${GREEN}  ✓ AI/ML Trading Signals${NC}"
    echo -e "${GREEN}  ✓ Portfolio Management${NC}"
    echo -e "${GREEN}  ✓ Real-time Price Alerts${NC}"
    echo -e "${GREEN}  ✓ Advanced Technical Analysis${NC}"
    
    echo -e "\n${BLUE}🔗 DEBT Integration:${NC}"
    echo -e "${GREEN}  ✓ OpenBB Financial Data${NC}"
    echo -e "${GREEN}  ✓ MLflow ML Tracking${NC}"
    echo -e "${GREEN}  ✓ n8n Workflow Automation${NC}"
    echo -e "${GREEN}  ✓ JupyterLab Analytics${NC}"
    echo -e "${GREEN}  ✓ ShellGPT AI Assistant${NC}"
    
    echo -e "\n${BLUE}📱 Web Interface:${NC}"
    echo -e "${CYAN}  • Modern responsive design${NC}"
    echo -e "${CYAN}  • Real-time charts and data${NC}"
    echo -e "${CYAN}  • Mobile-friendly trading interface${NC}"
    echo -e "${CYAN}  • Islamic finance compliance indicators${NC}"
}

# Main execution
main() {
    echo -e "${CYAN}Initializing DEBT Django Trading Platform...${NC}\n"
    
    # Change to Django project directory
    cd "$SCRIPT_DIR"
    
    check_debt_environment
    install_dependencies
    setup_database
    show_service_info
    start_django_server
}

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "DEBT Django Trading Platform"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo ""
    echo "The Django Trading Platform provides:"
    echo "  • Complete TASI market integration"
    echo "  • Global markets and cryptocurrency trading"
    echo "  • AI/ML powered trading signals"
    echo "  • Portfolio management and risk analysis"
    echo "  • Real-time notifications and alerts"
    echo ""
    echo "Access URLs:"
    echo "  • Web Interface: http://localhost:8000"
    echo "  • Admin Panel: http://localhost:8000/admin"
    echo "  • API Documentation: http://localhost:8000/api/"
    exit 0
fi

# Run main function
main "$@"