#!/bin/bash

# TASI ML Services Startup Script
# Islamic Finance-Compliant Machine Learning Pipeline

echo "🇸🇦 Starting TASI ML Services..."
echo "================================"
echo ""
echo "🤖 Islamic Finance-Compliant Machine Learning"
echo "📊 TASI Market Intelligence Pipeline"
echo "🕌 Sharia-Compliant Analysis"
echo ""

# Activate DEBT environment
if [ -f "$HOME/.debt-env/bin/activate" ]; then
    source "$HOME/.debt-env/bin/activate"
fi

# Install ML requirements
pip install mlflow scikit-learn pandas numpy yfinance plotly joblib

# Create directories
mkdir -p models
mkdir -p mlruns

# Function to start MLflow server
start_mlflow() {
    echo "🔬 Starting MLflow Tracking Server for TASI..."
    echo "Access MLflow UI at: http://localhost:5001"
    mlflow server --host 0.0.0.0 --port 5001 --default-artifact-root ./mlruns &
    MLFLOW_PID=$!
    echo "MLflow PID: $MLFLOW_PID"
}

# Function to train TASI models
train_tasi_models() {
    echo ""
    echo "🏦 Training TASI Islamic Finance Models..."
    echo "This will train ML models for:"
    echo "  • Saudi Aramco (2222.SR)"
    echo "  • Al Rajhi Bank (1120.SR)"
    echo "  • SABIC (2030.SR)"
    echo "  • And other TASI companies..."
    echo ""
    python train_models.py
}

# Function to start Gradio interface
start_gradio_interface() {
    echo ""
    echo "🎯 Starting TASI ML Interface..."
    echo "Access interactive ML interface at: http://localhost:7861"
    python ../gradio_demos/tasi_ml_interface.py &
    GRADIO_PID=$!
    echo "Gradio PID: $GRADIO_PID"
}

# Main menu
echo "Choose an option:"
echo "1. Start MLflow Server Only"
echo "2. Train TASI Models Only"
echo "3. Start All Services (MLflow + Training + Gradio)"
echo "4. Start MLflow + Gradio Interface"
echo ""
read -p "Enter your choice [1-4]: " choice

case $choice in
    1)
        start_mlflow
        echo ""
        echo "MLflow server is running. Press Ctrl+C to stop."
        wait $MLFLOW_PID
        ;;
    2)
        train_tasi_models
        ;;
    3)
        start_mlflow
        sleep 3
        train_tasi_models
        start_gradio_interface
        echo ""
        echo "All TASI ML services are running!"
        echo "📊 MLflow UI: http://localhost:5001"
        echo "🎯 ML Interface: http://localhost:7861"
        echo ""
        echo "Press Ctrl+C to stop all services."
        wait
        ;;
    4)
        start_mlflow
        sleep 3
        start_gradio_interface
        echo ""
        echo "TASI ML services are running!"
        echo "📊 MLflow UI: http://localhost:5001"
        echo "🎯 ML Interface: http://localhost:7861"
        echo ""
        echo "Press Ctrl+C to stop services."
        wait
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac