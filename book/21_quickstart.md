# Chapter 21: Quick Start Guide

## 🚀 Get DEBT Running in 10 Minutes

This chapter provides the fastest path to get the DEBT platform running on your system.

## Prerequisites Check

### System Requirements
- **OS**: Linux (Ubuntu 18.04+, Debian 10+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection

### Quick Check
```bash
# Check OS
uname -a

# Check available space
df -h

# Check memory
free -h

# Check Python
python3 --version
```

## Step 1: Download DEBT Platform (2 minutes)

### Option A: Git Clone (Recommended)
```bash
git clone https://github.com/xnox-me/DEBT.git
cd DEBT
```

### Option B: Download ZIP
```bash
wget https://github.com/xnox-me/DEBT/archive/master.zip
unzip master.zip
cd DEBT-master
```

## Step 2: Install Dependencies (5 minutes)

### Automated Installation
```bash
# Make installer executable
chmod +x install-packages.sh

# Run installation (requires sudo)
sudo ./install-packages.sh
```

### What Gets Installed
- Python 3.8+ and essential packages
- Node.js for web components
- Docker for containerization
- Git for version control
- Python virtual environment
- All required Python packages

## Step 3: Activate Environment (30 seconds)

```bash
# Activate DEBT environment
source activate_env.sh
```

### Environment Check
```bash
# Verify activation
echo $DEBT_HOME
python --version
which streamlit
which mlflow
```

## Step 4: Launch Platform (1 minute)

### Interactive Menu
```bash
# Launch main menu
./menu.sh
```

### Menu Options
```
🚀 DEBT - Development Environment & Business Tools
==================================================
1. 📊 Financial Dashboard (Streamlit)
2. 🤖 ML Interface (Gradio)
3. 📈 MLflow Tracking
4. 📔 Jupyter Lab
5. 🔄 n8n Workflows
6. 🌐 API Plugin
7. 🔧 Environment Setup
8. 📚 Documentation
9. 🧪 Test Suite
10. 🇸🇦 TASI Market Intelligence
11. 🌍 Global Markets Intelligence
12. Exit
```

### Quick Launch Commands
```bash
# Start all services
./start_all_business_intelligence.sh

# Start specific components
cd sophisticated_example/financial_dashboard
./start_dashboard.sh

# Start API gateway
python api_plugin.py
```

## Step 5: Access Services (30 seconds)

### Service URLs
| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:8501 | Financial analysis dashboard |
| **API Gateway** | http://localhost:9000 | Unified API access |
| **API Docs** | http://localhost:9000/docs | Interactive API documentation |
| **MLflow** | http://localhost:5000 | ML experiment tracking |
| **TASI Dashboard** | http://localhost:8502 | Islamic finance dashboard |
| **Global Markets** | http://localhost:8504 | International markets |

### Health Check
```bash
# Check all services
curl http://localhost:9000/health

# Expected response
{
  "status": "healthy",
  "services": {...},
  "timestamp": "2025-08-25T..."
}
```

## Common Quick Start Issues

### Issue 1: Permission Denied
```bash
# Fix script permissions
chmod +x *.sh
chmod +x sophisticated_example/**/*.sh
chmod +x tasi_market_intelligence/**/*.sh
```

### Issue 2: Port Already in Use
```bash
# Check port usage
netstat -tulpn | grep :8501

# Kill process if needed
sudo kill -9 <PID>
```

### Issue 3: Python Environment Issues
```bash
# Recreate virtual environment
rm -rf ~/.debt-env
python3 -m venv ~/.debt-env
source ~/.debt-env/bin/activate
pip install -r requirements.txt
```

### Issue 4: Package Installation Failures
```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install missing dependencies
sudo apt install -y build-essential python3-dev
```

## Quick Configuration

### Environment Variables
```bash
# Add to ~/.bashrc for persistence
export DEBT_HOME=/path/to/DEBT
export PYTHONPATH=$DEBT_HOME:$PYTHONPATH
```

### Basic Customization
```bash
# Copy configuration template
cp config/default_config.py config/user_config.py

# Edit configuration
nano config/user_config.py
```

## Quick Testing

### Test Financial Dashboard
1. Open http://localhost:8501
2. Select a stock symbol (e.g., AAPL)
3. Verify real-time data loads
4. Check charts and metrics

### Test API Gateway
1. Open http://localhost:9000/docs
2. Try GET /health endpoint
3. Test financial data endpoints
4. Verify responses

### Test ML Interface
1. Open http://localhost:7860 (if Gradio is running)
2. Try customer churn prediction
3. Test with sample data
4. Verify predictions

## Quick Customization

### Add New Stock Symbol
```python
# Edit financial_dashboard/app.py
SYMBOLS = ["AAPL", "GOOGL", "MSFT", "TSLA", "YOUR_SYMBOL"]
```

### Modify Update Frequency
```python
# Edit cache settings
CACHE_TTL = 60  # seconds (change to desired interval)
```

### Add Custom Metrics
```python
# Add to dashboard
def custom_metric(data):
    return data.mean() * 1.1  # Your custom calculation

# Display in Streamlit
st.metric("Custom Metric", custom_metric(stock_data))
```

## Quick Deployment

### Docker Quick Deploy
```bash
# Build Docker image
docker build -t debt-platform .

# Run container
docker run -p 8501:8501 -p 9000:9000 debt-platform
```

### Cloud Quick Deploy
```bash
# For cloud deployment
export CLOUD_PROVIDER=aws  # or gcp, azure
./deploy/cloud_deploy.sh
```

## Performance Quick Tips

### Memory Optimization
```bash
# Limit cache size
export CACHE_MAX_SIZE=100

# Reduce concurrent connections
export MAX_CONNECTIONS=50
```

### Speed Optimization
```bash
# Enable performance mode
export PERFORMANCE_MODE=true

# Use faster JSON library
pip install orjson
```

## Next Steps After Quick Start

### Immediate (Next 30 minutes)
1. **Explore all dashboards** - Try each business intelligence suite
2. **Test API endpoints** - Use the interactive documentation
3. **Review sample data** - Understand the data structure
4. **Check logs** - Monitor system behavior

### Short-term (Next few hours)
1. **Read architecture guide** - Understand system design
2. **Customize configuration** - Adapt to your needs
3. **Add your data sources** - Integrate your data
4. **Set up monitoring** - Configure alerts and logging

### Medium-term (Next few days)
1. **Deploy to production** - Set up proper hosting
2. **Configure security** - Add authentication and HTTPS
3. **Scale services** - Optimize for your load
4. **Train custom models** - Use your business data

## Support Resources

### Documentation
- **Complete Guide**: [DEBT_COMPLETE_GUIDE.md](../DEBT_COMPLETE_GUIDE.md)
- **API Reference**: [Chapter 25](./25_api_reference.md)
- **Troubleshooting**: [Chapter 23](./23_troubleshooting.md)

### Community
- **GitHub Issues**: Report bugs and get help
- **Discussions**: Ask questions and share ideas
- **Wiki**: Community-contributed knowledge

### Professional Support
- **Consulting**: Custom implementation assistance
- **Training**: Team training and workshops
- **Support**: Priority issue resolution

---

**🎉 Congratulations! You now have DEBT running. Next: [Chapter 22: Advanced Configuration](./22_advanced_config.md)**