#!/bin/bash

echo "🌍 Starting Global Markets & Crypto Intelligence Dashboard..."
echo "========================================================="
echo ""
echo "📊 Multi-Country Market Analysis"
echo "💰 Cryptocurrency Intelligence"
echo "🥇 Precious Metals Tracking"
echo ""
echo "🌐 Dashboard: http://localhost:8504"
echo "🎯 Features:"
echo "   • US, China, Japan, Brazil, UK, France, Italy, Russia, Korea"
echo "   • Bitcoin, Ethereum, Altcoins"
echo "   • Gold, Silver futures"
echo "   • Real-time global analysis"
echo ""

if [ -f "$HOME/.debt-env/bin/activate" ]; then
    source "$HOME/.debt-env/bin/activate"
fi

pip install streamlit plotly yfinance scikit-learn pandas numpy

streamlit run app.py --server.address 0.0.0.0 --server.port 8504