# 🔄 DEBT Business Intelligence Workflows

## n8n Automation for Business Process Optimization

This directory contains n8n workflow configurations for automating various business intelligence and data processing tasks within the DEBT platform.

## 📊 Available Workflows

### 1. **Financial Data Collection & Analysis**
- **File**: `financial_data_automation.json`
- **Purpose**: Automated collection of market data, technical analysis, and alert generation
- **Triggers**: Scheduled (hourly/daily), webhook-based
- **Actions**: Data collection, analysis, notifications, report generation

### 2. **Customer Analytics Pipeline**
- **File**: `customer_analytics_pipeline.json` 
- **Purpose**: Automated customer data processing, churn prediction, and retention campaigns
- **Triggers**: New customer data, periodic batch processing
- **Actions**: Data validation, ML predictions, business alerts

### 3. **Business KPI Monitoring**
- **File**: `kpi_monitoring_workflow.json`
- **Purpose**: Real-time business metrics monitoring and executive reporting
- **Triggers**: Scheduled intervals, threshold breaches
- **Actions**: KPI calculation, trend analysis, executive notifications

### 4. **ML Model Retraining Pipeline**
- **File**: `ml_retraining_automation.json`
- **Purpose**: Automated model performance monitoring and retraining
- **Triggers**: Performance degradation, new data availability
- **Actions**: Model evaluation, retraining, deployment automation

## 🚀 Quick Setup

### Prerequisites
- n8n installed and running (included in DEBT installation)
- DEBT environment activated
- Required API credentials configured

### Installation Steps

1. **Start n8n service**:
```bash
# From DEBT main directory
./menu.sh
# Select option 2 (n8n)
```

2. **Access n8n interface**:
   - Open browser: http://localhost:5678
   - Import workflow files from this directory

3. **Configure credentials**:
   - Set up API keys and database connections
   - Configure notification endpoints
   - Test workflow connections

## 🔧 Workflow Configuration

### Environment Variables
```bash
# Add to your DEBT environment
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=your_secure_password

# Database connection (if using PostgreSQL)
export DB_POSTGRESDB_HOST=localhost
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=debt_business
export DB_POSTGRESDB_USER=debt_user
export DB_POSTGRESDB_PASSWORD=your_db_password

# API endpoints
export DEBT_API_BASE_URL=http://localhost:8000
export STREAMLIT_WEBHOOK_URL=http://localhost:8501
```

## 📋 Workflow Details

### Financial Data Automation
- **Schedule**: Every hour during market hours
- **Data Sources**: Yahoo Finance, Alpha Vantage, Economic indicators
- **Processing**: Technical analysis, trend detection, anomaly identification
- **Outputs**: Alerts, reports, dashboard updates

### Customer Analytics Pipeline  
- **Triggers**: New customer data, daily batch processing
- **Processing**: Data validation, feature engineering, churn prediction
- **ML Integration**: Calls DEBT ML API for predictions
- **Actions**: Risk alerts, retention campaign triggers

### KPI Monitoring
- **Frequency**: Real-time and scheduled intervals
- **Metrics**: Revenue, customer satisfaction, churn rates, growth metrics
- **Thresholds**: Configurable business rule engine
- **Notifications**: Email, Slack, executive dashboards

## 🛠️ Custom Workflow Development

### Basic Workflow Structure
```json
{
  "name": "Custom Business Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Trigger Node",
      "type": "n8n-nodes-base.cron",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:8000/business/kpis",
        "options": {}
      },
      "name": "Get Business KPIs",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    }
  ],
  "connections": {
    "Trigger Node": {
      "main": [
        [
          {
            "node": "Get Business KPIs",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 📈 Business Integration Points

### DEBT API Integration
- Customer prediction endpoints
- Financial analysis services  
- KPI metrics collection
- Model training triggers

### External System Integration
- CRM systems (Salesforce, HubSpot)
- Email marketing (Mailchimp, SendGrid)
- Communication (Slack, Microsoft Teams)
- Database systems (PostgreSQL, MySQL)

## 🔍 Monitoring & Troubleshooting

### Workflow Execution Logs
- Access via n8n interface: http://localhost:5678
- Check execution history and error details
- Monitor performance and execution times

### Common Issues
1. **API Connection Failures**: Check endpoint URLs and credentials
2. **Data Format Errors**: Validate input data schemas
3. **Performance Issues**: Optimize workflow node configurations
4. **Authentication Problems**: Verify API keys and access tokens

## 📊 Business Value

### Automation Benefits
- **80% reduction** in manual data processing tasks
- **Real-time alerting** for business critical events
- **Consistent execution** of business processes
- **Scalable integration** with external systems

### ROI Metrics
- Reduced operational overhead
- Faster response to business events
- Improved data accuracy and consistency
- Enhanced business intelligence automation

## 🔄 Workflow Maintenance

### Regular Tasks
- Monitor execution success rates
- Update API credentials and endpoints  
- Optimize performance and resource usage
- Add new business rules and triggers

### Version Control
- Export workflows regularly
- Maintain backup configurations
- Document changes and updates
- Test workflows in staging environment

---

**Ready to automate your business intelligence with n8n workflows!** 🚀