# Chapter 25: API Reference

## 🌐 DEBT Platform API Documentation

Complete reference for all API endpoints across the DEBT platform.

## Base URLs

| Service | Base URL | Description |
|---------|----------|-------------|
| **API Gateway** | `http://localhost:9000` | Unified access point |
| **Original Suite** | `http://localhost:8000` | Sophisticated example APIs |
| **TASI Suite** | `http://localhost:8003` | Islamic finance APIs |
| **Global Markets** | `http://localhost:8005` | International markets APIs |

## Authentication

### API Key Authentication (Optional)
```bash
# Include in headers for protected endpoints
curl -H "X-API-Key: your_api_key" http://localhost:9000/api/endpoint
```

### Rate Limiting
- **Standard**: 100 requests per minute
- **Premium**: 1000 requests per minute
- **Headers**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## API Gateway Endpoints

### Health & Status

#### GET /health
Check overall system health
```bash
curl http://localhost:9000/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "financial_dashboard": "healthy",
    "ml_interface": "healthy",
    "mlflow_tracking": "healthy"
  },
  "timestamp": "2025-08-25T12:00:00Z"
}
```

#### GET /api/status
Detailed service status information
```bash
curl http://localhost:9000/api/status
```

**Response:**
```json
{
  "gateway_status": "operational",
  "version": "1.0.0",
  "uptime": "2h 30m 15s",
  "cache_status": "95% hit ratio",
  "active_connections": 42
}
```

### Financial Data Endpoints

#### GET /api/financial/market/{symbol}
Get real-time market data for a stock symbol

**Parameters:**
- `symbol` (path): Stock symbol (e.g., AAPL, GOOGL)
- `period` (query): Data period (1d, 1mo, 3mo, 6mo, 1y)

**Example:**
```bash
curl "http://localhost:9000/api/financial/market/AAPL?period=1d"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "current_price": 150.25,
  "change": 2.50,
  "change_percent": 1.69,
  "volume": 45234567,
  "market_cap": 2450000000000,
  "pe_ratio": 28.5,
  "52_week_high": 180.95,
  "52_week_low": 124.17,
  "timestamp": "2025-08-25T15:30:00Z"
}
```

#### GET /api/financial/portfolio
Analyze a portfolio of stocks

**Parameters:**
- `symbols` (query): Comma-separated stock symbols
- `weights` (query, optional): Comma-separated weights

**Example:**
```bash
curl "http://localhost:9000/api/financial/portfolio?symbols=AAPL,GOOGL,MSFT"
```

**Response:**
```json
{
  "portfolio": [
    {
      "symbol": "AAPL",
      "price": 150.25,
      "weight": 33.33,
      "value": 15025.00,
      "volatility": 18.5
    }
  ],
  "total_value": 45075.00,
  "expected_return": 12.5,
  "portfolio_volatility": 16.2,
  "sharpe_ratio": 0.77
}
```

### Machine Learning Endpoints

#### POST /api/ml/predict/churn
Predict customer churn probability

**Request Body:**
```json
{
  "age": 35,
  "income": 65000,
  "tenure": 24,
  "num_products": 3,
  "satisfaction_score": 7.5,
  "support_calls": 2
}
```

**Example:**
```bash
curl -X POST "http://localhost:9000/api/ml/predict/churn" \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "income": 65000, "tenure": 24, "num_products": 3}'
```

**Response:**
```json
{
  "prediction": false,
  "probability": 0.23,
  "confidence": 0.89,
  "risk_level": "Low",
  "factors": {
    "tenure": "positive",
    "income": "positive", 
    "satisfaction": "neutral"
  },
  "recommendations": [
    "Continue standard engagement",
    "Monitor satisfaction scores",
    "Upsell opportunities available"
  ]
}
```

#### POST /api/ml/predict/sales
Predict sales performance

**Request Body:**
```json
{
  "customer_age": 42,
  "income": 75000,
  "previous_purchases": 8,
  "engagement_score": 8.2,
  "season": "Q4",
  "region": "North America"
}
```

**Response:**
```json
{
  "predicted_sales": 1250.75,
  "confidence_interval": [1100.50, 1401.00],
  "category": "HIGH",
  "factors": {
    "income": "high_impact",
    "engagement": "medium_impact",
    "season": "positive"
  },
  "next_best_action": "Premium product recommendation"
}
```

### Business Intelligence Endpoints

#### GET /api/business/kpis
Get comprehensive business KPIs

**Example:**
```bash
curl http://localhost:9000/api/business/kpis
```

**Response:**
```json
{
  "revenue": {
    "monthly": 875000,
    "quarterly": 2625000,
    "growth_rate": 15.2
  },
  "customers": {
    "total": 12500,
    "active": 9800,
    "churn_rate": 8.5,
    "acquisition_cost": 125
  },
  "operations": {
    "efficiency_score": 87,
    "cost_per_transaction": 2.45,
    "uptime": 99.7
  }
}
```

## TASI Islamic Finance APIs

### Base URL: http://localhost:8003

#### GET /tasi/companies
List all TASI companies with Islamic compliance status

**Example:**
```bash
curl http://localhost:8003/tasi/companies
```

**Response:**
```json
{
  "total_companies": 10,
  "islamic_compliant_count": 10,
  "companies": [
    {
      "symbol": "2222.SR",
      "name": "Saudi Aramco",
      "sector": "Energy",
      "islamic_compliant": true,
      "compliance_status": "✅ Halal"
    }
  ]
}
```

#### GET /tasi/market/{symbol}
Get TASI stock data with Islamic compliance information

**Example:**
```bash
curl http://localhost:8003/tasi/market/2222.SR
```

**Response:**
```json
{
  "symbol": "2222.SR",
  "company_name": "Saudi Aramco",
  "islamic_compliant": true,
  "current_price_sar": 35.50,
  "change_sar": 0.75,
  "change_percent": 2.16,
  "volume": 2345678,
  "islamic_status": "✅ Sharia Compliant",
  "currency": "SAR"
}
```

#### GET /tasi/halal/screening
Screen all TASI companies for Islamic compliance

**Response:**
```json
{
  "screening_summary": {
    "total_companies_screened": 10,
    "halal_compliant": 10,
    "compliance_percentage": 100
  },
  "screening_criteria": [
    "Business activities must be Halal",
    "No involvement in prohibited industries",
    "Low debt-to-equity ratios"
  ]
}
```

## Global Markets APIs

### Base URL: http://localhost:8005

#### GET /global/markets
Get overview of all global markets

**Example:**
```bash
curl http://localhost:8005/global/markets
```

**Response:**
```json
{
  "total_markets": 25,
  "markets_by_type": {
    "cryptocurrencies": 5,
    "stocks": 15,
    "indices": 3,
    "commodities": 2
  },
  "markets": [
    {
      "symbol": "BTC-USD",
      "name": "Bitcoin",
      "type": "crypto",
      "current_price": 43250.75,
      "change_percent": 2.8
    }
  ]
}
```

#### GET /crypto/overview
Get cryptocurrency market overview

**Response:**
```json
{
  "total_cryptocurrencies": 5,
  "total_market_cap_usd": 1750000000000,
  "market_sentiment": "Bullish",
  "cryptocurrencies": [
    {
      "symbol": "BTC-USD",
      "name": "Bitcoin",
      "current_price": 43250.75,
      "market_cap": 850000000000,
      "change_percent": 2.8
    }
  ]
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Stock symbol 'INVALID' not found",
    "details": "Please use valid stock symbols like AAPL, GOOGL, etc.",
    "timestamp": "2025-08-25T15:30:00Z"
  }
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `404` - Not Found (symbol/endpoint not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable

## SDK Examples

### Python SDK Usage
```python
import requests

class DEBTClient:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
    
    def get_stock_data(self, symbol, period="1d"):
        response = requests.get(
            f"{self.base_url}/api/financial/market/{symbol}",
            params={"period": period}
        )
        return response.json()
    
    def predict_churn(self, customer_data):
        response = requests.post(
            f"{self.base_url}/api/ml/predict/churn",
            json=customer_data
        )
        return response.json()

# Usage
client = DEBTClient()
stock_data = client.get_stock_data("AAPL")
churn_prediction = client.predict_churn({
    "age": 35,
    "income": 65000,
    "tenure": 24
})
```

### JavaScript SDK Usage
```javascript
class DEBTClient {
    constructor(baseUrl = 'http://localhost:9000') {
        this.baseUrl = baseUrl;
    }
    
    async getStockData(symbol, period = '1d') {
        const response = await fetch(
            `${this.baseUrl}/api/financial/market/${symbol}?period=${period}`
        );
        return response.json();
    }
    
    async predictChurn(customerData) {
        const response = await fetch(
            `${this.baseUrl}/api/ml/predict/churn`,
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(customerData)
            }
        );
        return response.json();
    }
}

// Usage
const client = new DEBTClient();
const stockData = await client.getStockData('AAPL');
const churnPrediction = await client.predictChurn({
    age: 35,
    income: 65000,
    tenure: 24
});
```

## Webhooks

### Webhook Configuration
```bash
# Register webhook for real-time updates
curl -X POST "http://localhost:9000/api/webhooks/register" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhook",
    "events": ["market_update", "prediction_ready"],
    "secret": "your_secret_key"
  }'
```

### Webhook Payload Format
```json
{
  "event": "market_update",
  "data": {
    "symbol": "AAPL",
    "price": 150.25,
    "change": 2.50
  },
  "timestamp": "2025-08-25T15:30:00Z",
  "signature": "sha256=abc123..."
}
```

---

**📖 Next: [Chapter 26: Command Line Reference](./26_cli_reference.md)**