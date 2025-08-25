# DEBT Quick Start Guide

## 🚀 Get Started with DEBT in 5 Minutes

DEBT (Development Environment & Business Tools) is your all-in-one platform for business intelligence, financial analysis, and development. This guide will get you up and running quickly.

## 📋 Prerequisites

- Linux system (Ubuntu/Debian or Arch Linux)
- Git installed
- Basic command line knowledge

## ⚡ Fast Installation

### Step 1: Clone DEBT
```bash
git clone <repository-url> DEBT
cd DEBT
```

### Step 2: Install Business Environment
```bash
chmod +x install-packages.sh
sudo ./install-packages.sh
```

### Step 3: Activate DEBT
```bash
source activate_env.sh
```

### Step 4: Launch Business Platform
```bash
./menu.sh
```

## 🎯 First Business Tasks

### 1. Financial Analysis with OpenBB
```bash
# From DEBT menu, select: 5. Start OpenBB (Financial Data & Analysis)
# Try these commands:
import pandas as pd
from openbb import obb

# Get stock data
stock_data = obb.equity.price.historical("AAPL", start_date="2024-01-01")
print(stock_data.head())

# Analyze market trends
spy_data = obb.equity.price.historical("SPY", start_date="2024-01-01")
print(f"SPY performance: {((spy_data.close.iloc[-1] / spy_data.close.iloc[0]) - 1) * 100:.2f}%")
```

### 2. Business Dashboard with Streamlit
```bash
# From DEBT menu: 8. Start ML/AI (Business Intelligence Tools) → 6. Streamlit
# Access at: http://localhost:8501
# Create interactive business dashboards and KPI tracking
```

### 3. Business Data Analysis with JupyterLab
```bash
# From DEBT menu: 8. Start ML/AI → 1. JupyterLab
# Access at: http://localhost:8888
# Perfect for financial modeling and business analytics
```

### 4. AI Business Assistant
```bash
# From DEBT menu: 6. Start ShellGPT (AI Business Assistant)
sgpt "analyze quarterly sales performance trends"
sgpt --code "create a financial dashboard with KPIs"
sgpt "suggest business process automation ideas"
```

### 5. Business Process Automation
```bash
# From DEBT menu: 2. Start n8n (Business Workflow Automation)
# Access at: http://localhost:5678
# Create automated business workflows and data pipelines
```

## 🔧 Essential DEBT Commands

### Environment Management
```bash
# Activate DEBT environment
source activate_env.sh

# Deactivate environment
deactivate

# Check available packages
source activate_env.sh && pip list
```

### Business Intelligence Tools
```bash
# Start business intelligence helper
./ml-helper.sh jupyter      # JupyterLab for business analytics
./ml-helper.sh streamlit    # Business dashboards
./ml-helper.sh gradio       # Business ML demos
./ml-helper.sh mlflow       # Business ML tracking
```

### Remote Business Access
```bash
# Manage business remote access
./shellngn-helper.sh start   # Start business remote access
./shellngn-helper.sh status  # Check access status
./shellngn-helper.sh stop    # Stop remote access
```

## 📊 Quick Business Examples

### Financial Analysis Example
```python
# Quick stock analysis
import pandas as pd
import matplotlib.pyplot as plt

# Sample financial data analysis
def analyze_stock_performance(symbol):
    # This would use real OpenBB data in DEBT
    print(f"Analyzing {symbol} performance...")
    print("📈 Key Metrics:")
    print("• Price Change: +5.2%")
    print("• Volume: 2.3M shares")
    print("• P/E Ratio: 18.5")
    return "Analysis complete"

# Run analysis
result = analyze_stock_performance("AAPL")
```

### Business KPI Dashboard
```python
# Create quick business metrics dashboard
import streamlit as st
import pandas as pd
import numpy as np

# Business KPI example
def create_business_dashboard():
    st.title("🏢 Business Performance Dashboard")
    
    # Sample KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Revenue", "$1.2M", "12%")
    with col2:
        st.metric("Customers", "3,421", "8%")
    with col3:
        st.metric("Profit Margin", "23.5%", "2.1%")
    
    # Sample chart
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Sales', 'Marketing', 'Operations']
    )
    st.line_chart(chart_data)

# Run in Streamlit via DEBT menu
```

### Business Automation Workflow
```bash
# Example n8n workflow steps:
# 1. Monitor business email for new orders
# 2. Extract order data automatically
# 3. Update inventory database
# 4. Generate invoice and send to customer
# 5. Create sales report entry
# 6. Notify fulfillment team
```

## 🎯 Business Use Case Scenarios

### Scenario 1: Financial Analyst
```bash
1. Launch DEBT: ./menu.sh
2. Start OpenBB: Option 5
3. Analyze market data and create reports
4. Build dashboards in Streamlit: Menu → 8 → 6
5. Present findings with Gradio demos: Menu → 8 → 5
```

### Scenario 2: Business Intelligence Developer
```bash
1. Start development environment: Menu → 1 (Neovim)
2. Build APIs for business data
3. Create ML models in JupyterLab: Menu → 8 → 1
4. Deploy with Docker containers
5. Monitor with MLflow: Menu → 8 → 7
```

### Scenario 3: Business Operations Manager
```bash
1. Create automation workflows: Menu → 2 (n8n)
2. Set up business dashboards: Menu → 8 → 6
3. Monitor KPIs and performance metrics
4. Use AI assistant for insights: Menu → 6
5. Generate automated reports
```

### Scenario 4: Remote Business Access
```bash
1. Start remote access: Menu → 7 (Shellngn Pro)
2. Access business servers securely
3. Transfer business documents via SFTP
4. Connect to business applications via VNC/RDP
5. Manage multiple business connections
```

## 🔍 Troubleshooting

### Common Issues
```bash
# Virtual environment not activated
source ~/.debt-env/bin/activate

# Docker permission issues
sudo usermod -aG docker $USER
# Then logout/login

# Package conflicts
./install-packages.sh  # Re-run installer

# Port already in use
sudo lsof -i :8888  # Check what's using the port
```

### Getting Help
```bash
# Check DEBT status
./menu.sh  # Main menu with all options

# Test business intelligence tools
python test_ml_ai.py

# Test financial analysis
python test_openbb.py

# Test AI assistant
python test_shellgpt.py

# Test remote access
./test_shellngn.sh
```

## 🎉 Next Steps

1. **Explore Business Tools**: Try each tool in the DEBT menu
2. **Build Your First Dashboard**: Use Streamlit to create KPI tracking
3. **Analyze Financial Data**: Use OpenBB for market analysis
4. **Automate Business Processes**: Create workflows with n8n
5. **Develop Business Applications**: Use Neovim for full-stack development

## 📚 Learning Resources

- **DEBT_PROJECT_OVERVIEW.md**: Complete project documentation
- **README.md**: Detailed installation and usage guide
- **Test Scripts**: Validate your DEBT installation
- **Helper Scripts**: Quick access to business tools

---

**Welcome to DEBT!** Your business intelligence and development platform is ready. Start building amazing business solutions! 🚀