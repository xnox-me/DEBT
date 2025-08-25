#!/bin/bash

# DEBT ML Pipeline and Gradio Interface Startup Script
# Launches MLflow tracking server and Gradio ML interface

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 DEBT ML Pipeline & Gradio Interface${NC}"
echo -e "${BLUE}=====================================${NC}"

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

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📍 Project directory: $PROJECT_DIR${NC}"

# Create MLflow directory
MLFLOW_DIR="$PROJECT_DIR/mlflow"
mkdir -p "$MLFLOW_DIR"

# Check required packages
echo -e "${BLUE}🔍 Checking required packages...${NC}"

REQUIRED_PACKAGES=("mlflow" "gradio" "scikit-learn" "xgboost" "lightgbm" "yfinance" "plotly")
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

# Function to start MLflow server
start_mlflow() {
    echo -e "${BLUE}🔬 Starting MLflow tracking server...${NC}"
    cd "$MLFLOW_DIR"
    mlflow server \
        --backend-store-uri sqlite:///mlflow.db \
        --default-artifact-root ./artifacts \
        --host 0.0.0.0 \
        --port 5000 &
    MLFLOW_PID=$!
    echo -e "${GREEN}✅ MLflow server started (PID: $MLFLOW_PID)${NC}"
    echo -e "${BLUE}📊 MLflow UI: http://localhost:5000${NC}"
}

# Function to start Gradio interface  
start_gradio() {
    echo -e "${BLUE}🎨 Starting Gradio ML interface...${NC}"
    cd "$SCRIPT_DIR"
    python business_ml_interface.py &
    GRADIO_PID=$!
    echo -e "${GREEN}✅ Gradio interface started (PID: $GRADIO_PID)${NC}"
    echo -e "${BLUE}🤖 Gradio ML Interface: http://localhost:7860${NC}"
}

# Function to train models if needed
train_models() {
    echo -e "${BLUE}🏋️ Training ML models...${NC}"
    cd "$PROJECT_DIR/ml_pipeline"
    python train_models.py
    echo -e "${GREEN}✅ Model training completed${NC}"
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    if [[ ! -z "$MLFLOW_PID" ]]; then
        kill $MLFLOW_PID 2>/dev/null || true
        echo -e "${GREEN}✅ MLflow server stopped${NC}"
    fi
    
    if [[ ! -z "$GRADIO_PID" ]]; then
        kill $GRADIO_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Gradio interface stopped${NC}"
    fi
    
    # Kill any remaining mlflow or gradio processes
    pkill -f "mlflow server" 2>/dev/null || true
    pkill -f "business_ml_interface.py" 2>/dev/null || true
    
    echo -e "${BLUE}👋 DEBT ML Pipeline shutdown complete${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Check if models exist, train if needed
if [ ! -d "$PROJECT_DIR/ml_pipeline/models" ]; then
    echo -e "${YELLOW}📚 No trained models found. Training models first...${NC}"
    train_models
fi

# Parse command line arguments
TRAIN_MODELS=false
START_MLFLOW=true
START_GRADIO=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --train)
            TRAIN_MODELS=true
            shift
            ;;
        --mlflow-only)
            START_GRADIO=false
            shift
            ;;
        --gradio-only)
            START_MLFLOW=false
            shift
            ;;
        --help)
            echo "DEBT ML Pipeline Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --train         Force model training before starting services"
            echo "  --mlflow-only   Start only MLflow tracking server"
            echo "  --gradio-only   Start only Gradio interface"
            echo "  --help          Show this help message"
            echo ""
            echo "Services:"
            echo "  MLflow UI:      http://localhost:5000"
            echo "  Gradio ML:      http://localhost:7860"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Train models if requested
if [ "$TRAIN_MODELS" = true ]; then
    train_models
fi

echo -e "${GREEN}🚀 Starting DEBT ML Pipeline services...${NC}"

# Start services
if [ "$START_MLFLOW" = true ]; then
    start_mlflow
    sleep 3  # Wait for MLflow to start
fi

if [ "$START_GRADIO" = true ]; then
    start_gradio
    sleep 3  # Wait for Gradio to start
fi

echo ""
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo ""
echo -e "${BLUE}🌐 Available Services:${NC}"
if [ "$START_MLFLOW" = true ]; then
    echo -e "${BLUE}  📊 MLflow Tracking:    http://localhost:5000${NC}"
fi
if [ "$START_GRADIO" = true ]; then
    echo -e "${BLUE}  🤖 Gradio ML Interface: http://localhost:7860${NC}"
fi
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop all services${NC}"

# Keep script running and wait for user interrupt
wait