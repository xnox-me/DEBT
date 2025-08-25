#!/bin/bash

# DEBT Financial Dashboard Startup Script
# Launches the sophisticated financial analysis dashboard

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏦 DEBT Financial Intelligence Dashboard${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Not in a virtual environment. Activating DEBT environment...${NC}"
    
    # Try to activate DEBT environment
    if [ -f "$HOME/.debt-env/bin/activate" ]; then
        source "$HOME/.debt-env/bin/activate"
        echo -e "${GREEN}✅ DEBT environment activated${NC}"
    else
        echo -e "${RED}❌ DEBT environment not found. Please run DEBT installation first.${NC}"
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -oP '(?<=Python )[0-9.]+')
echo -e "${BLUE}📍 Using Python $PYTHON_VERSION${NC}"

# Check required packages
echo -e "${BLUE}🔍 Checking required packages...${NC}"

REQUIRED_PACKAGES=("streamlit" "pandas" "numpy" "plotly" "yfinance" "scikit-learn")
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
    echo -e "${YELLOW}📦 Installing missing packages...${NC}"
    pip install "${MISSING_PACKAGES[@]}"
fi

# Set environment variables for better performance
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Create .streamlit directory if it doesn't exist
STREAMLIT_DIR="$(dirname "$0")/.streamlit"
mkdir -p "$STREAMLIT_DIR"

# Create Streamlit configuration
cat > "$STREAMLIT_DIR/config.toml" << EOF
[server]
port = 8501
address = "0.0.0.0"
baseUrlPath = ""
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"
font = "sans serif"

[logger]
level = "info"

[client]
showErrorDetails = false
EOF

echo -e "${GREEN}⚙️  Streamlit configuration created${NC}"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if app.py exists
if [ ! -f "$SCRIPT_DIR/app.py" ]; then
    echo -e "${RED}❌ Financial dashboard app.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Starting DEBT Financial Intelligence Dashboard...${NC}"
echo -e "${BLUE}📊 Dashboard will be available at: http://localhost:8501${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the dashboard${NC}"
echo ""

# Start the Streamlit app
cd "$SCRIPT_DIR"
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.runOnSave=true \
    --browser.serverAddress="localhost" \
    --browser.serverPort=8501