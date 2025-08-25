#!/bin/bash
# DEBT (Development Environment & Business Tools) Activation Script
# This script activates the DEBT Python virtual environment

echo "🚀 Activating DEBT Environment..."
echo "📊 Development Environment & Business Tools"

# Activate the virtual environment
source ~/.debt-env/bin/activate

# Set environment variables
export DEBT_ENV_ACTIVE=1
export DEBT_VERSION="1.0"

# Add useful aliases
alias sgpt-help="sgpt --help"
alias debt-status="echo 'DEBT Environment Active - Version: $DEBT_VERSION'"

echo "✅ DEBT Environment Activated!"
echo "💡 Available tools:"
echo "   • sgpt - AI assistant (requires API key setup)"
echo "   • python - Python with ML/AI packages"
echo "   • pip - Package manager"
echo ""
echo "🔧 To get started:"
echo "   1. Run './menu.sh' for interactive tools"
echo "   2. Run 'sgpt --install' to setup AI assistant"
echo "   3. Run 'debt-status' to check environment"
echo ""
echo "📚 Documentation: Check README.md and other docs in DEBT folder"