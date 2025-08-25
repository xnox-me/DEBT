#!/bin/bash

# TASI Market Intelligence Dashboard Startup Script
# Saudi Stock Exchange Analysis Platform

echo "🇸🇦 Starting TASI Market Intelligence Dashboard..."
echo "=============================================="
echo ""
echo "📊 Saudi Stock Exchange Real-time Analysis"
echo "🕌 Islamic Finance Compliant Platform"
echo "💰 TASI Market Business Intelligence"
echo ""
echo "🌐 Dashboard will be available at: http://localhost:8502"
echo "📈 Features:"
echo "   • Real-time TASI stock data"
echo "   • Islamic finance compliant analysis"
echo "   • Saudi Aramco, Al Rajhi Bank, SABIC analysis"
echo "   • Sharia-compliant ML predictions"
echo "   • Comprehensive portfolio management"
echo ""
echo "Press Ctrl+C to stop the dashboard."
echo ""

# Activate DEBT environment
if [ -f "$HOME/.debt-env/bin/activate" ]; then
    source "$HOME/.debt-env/bin/activate"
fi

# Install additional requirements if needed
pip install streamlit plotly yfinance scikit-learn pandas numpy

# Start the TASI dashboard on port 8502
streamlit run app.py --server.address 0.0.0.0 --server.port 8502 --theme.primaryColor="#006C35" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F8F9FA"