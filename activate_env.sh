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
