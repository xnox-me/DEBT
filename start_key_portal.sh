#!/bin/bash
# DEBT Key Management Portal Launcher
# Secure web interface for managing all your API keys and credentials

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DEBT_ENV_PATH="$HOME/.debt-env"
KEY_PORTAL_SCRIPT="$(dirname "$0")/key_portal.py"
PORTAL_PORT=5001

print_banner() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                 🔑 DEBT Key Management Portal                 ║${NC}"
    echo -e "${PURPLE}║              Secure API Key & Credential Manager             ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "$DEBT_ENV_PATH" ]; then
        echo -e "${RED}❌ DEBT virtual environment not found at $DEBT_ENV_PATH${NC}"
        echo -e "${YELLOW}💡 Run the installation script first: sudo ./install-packages.sh${NC}"
        exit 1
    fi
    
    # Check if Flask is installed
    source "$DEBT_ENV_PATH/bin/activate"
    if ! python -c "import flask, cryptography" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing required packages for key portal...${NC}"
        pip install flask cryptography werkzeug
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install required packages${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ All dependencies satisfied${NC}"
}

check_port() {
    if lsof -Pi :$PORTAL_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $PORTAL_PORT is already in use${NC}"
        echo -e "${BLUE}🌐 The portal may already be running at: http://localhost:$PORTAL_PORT${NC}"
        echo ""
        read -p "Stop existing server and start new one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}🔄 Stopping existing server...${NC}"
            pkill -f "key_portal.py" 2>/dev/null || true
            sleep 2
        else
            echo -e "${BLUE}🌐 Opening existing portal in browser...${NC}"
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "http://localhost:$PORTAL_PORT" &
            elif command -v open >/dev/null 2>&1; then
                open "http://localhost:$PORTAL_PORT" &
            fi
            exit 0
        fi
    fi
}

start_portal() {
    echo -e "${BLUE}🚀 Starting DEBT Key Management Portal...${NC}"
    echo ""
    
    # Activate virtual environment and start portal
    source "$DEBT_ENV_PATH/bin/activate"
    
    # Set secure permissions on script
    chmod 700 "$KEY_PORTAL_SCRIPT"
    
    echo -e "${GREEN}🔐 Security Features:${NC}"
    echo -e "   • Password-protected access"
    echo -e "   • AES-256 encrypted key storage"
    echo -e "   • Restricted file permissions (600)"
    echo -e "   • Local-only access (no external exposure)"
    echo ""
    
    echo -e "${BLUE}📋 Supported Services:${NC}"
    echo -e "   • OpenAI API (for ShellGPT)"
    echo -e "   • Hugging Face (for Transformers)"
    echo -e "   • Weights & Biases (for MLOps)"
    echo -e "   • MLflow Tracking"
    echo -e "   • GitHub Token"
    echo -e "   • Docker Hub"
    echo -e "   • OpenBB Financial APIs"
    echo -e "   • Gradio API"
    echo ""
    
    echo -e "${GREEN}🌐 Portal URL: ${BLUE}http://localhost:$PORTAL_PORT${NC}"
    echo -e "${YELLOW}📝 Note: The portal will create secure storage files in your home directory${NC}"
    echo ""
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Open browser automatically if available
    if command -v xdg-open >/dev/null 2>&1; then
        echo -e "${BLUE}🌐 Opening portal in browser...${NC}"
        (sleep 3 && xdg-open "http://localhost:$PORTAL_PORT") &
    elif command -v open >/dev/null 2>&1; then
        echo -e "${BLUE}🌐 Opening portal in browser...${NC}"
        (sleep 3 && open "http://localhost:$PORTAL_PORT") &
    fi
    
    # Start the portal
    python "$KEY_PORTAL_SCRIPT"
}

show_help() {
    echo -e "${BLUE}DEBT Key Management Portal${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -p, --port     Set custom port (default: 5001)"
    echo "  -s, --status   Check portal status"
    echo "  --stop         Stop running portal"
    echo ""
    echo "Examples:"
    echo "  $0                 # Start portal on default port"
    echo "  $0 -p 8080         # Start portal on port 8080"
    echo "  $0 --status        # Check if portal is running"
    echo "  $0 --stop          # Stop running portal"
    echo ""
    echo -e "${GREEN}Features:${NC}"
    echo "• Secure password-protected access"
    echo "• AES-256 encrypted key storage"
    echo "• Support for all DEBT service APIs"
    echo "• Environment variable export"
    echo "• Web-based key management interface"
}

check_status() {
    if lsof -Pi :$PORTAL_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ DEBT Key Portal is running on port $PORTAL_PORT${NC}"
        echo -e "${BLUE}🌐 Access at: http://localhost:$PORTAL_PORT${NC}"
        
        # Show process info
        PID=$(lsof -Pi :$PORTAL_PORT -sTCP:LISTEN -t)
        echo -e "${BLUE}📊 Process ID: $PID${NC}"
        
        # Show storage files
        echo -e "${BLUE}📁 Storage files:${NC}"
        [ -f "$HOME/.debt_keys.json" ] && echo -e "   • Keys: $HOME/.debt_keys.json" || echo -e "   • Keys: Not created yet"
        [ -f "$HOME/.debt_auth.json" ] && echo -e "   • Auth: $HOME/.debt_auth.json" || echo -e "   • Auth: Not created yet"
        [ -f "$HOME/.debt_encryption.key" ] && echo -e "   • Encryption: $HOME/.debt_encryption.key" || echo -e "   • Encryption: Not created yet"
    else
        echo -e "${RED}❌ DEBT Key Portal is not running${NC}"
        echo -e "${YELLOW}💡 Start with: $0${NC}"
    fi
}

stop_portal() {
    echo -e "${YELLOW}🛑 Stopping DEBT Key Portal...${NC}"
    
    if pkill -f "key_portal.py" 2>/dev/null; then
        echo -e "${GREEN}✅ Portal stopped successfully${NC}"
    else
        echo -e "${RED}❌ No running portal found${NC}"
    fi
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -s|--status)
        print_banner
        check_status
        exit 0
        ;;
    --stop)
        print_banner
        stop_portal
        exit 0
        ;;
    -p|--port)
        if [ -n "$2" ]; then
            PORTAL_PORT="$2"
        else
            echo -e "${RED}❌ Port number required${NC}"
            exit 1
        fi
        ;;
    "")
        # Default behavior - start portal
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo -e "${YELLOW}💡 Use -h for help${NC}"
        exit 1
        ;;
esac

# Main execution
print_banner
check_dependencies
check_port
start_portal