# DEBT Trading Platform

A comprehensive Django-based trading platform with real-time market data, machine learning predictions, portfolio management, and automated trading integration.

## Features

### 📈 Real-Time Market Data
- **TASI Integration**: Real-time Saudi stock market data for major companies
- **Global Markets**: Data from 9 countries including USA, UK, Japan, China, India
- **Crypto Markets**: Bitcoin, Ethereum, and other major cryptocurrencies
- **Precious Metals**: Gold, Silver, Platinum, Palladium futures
- **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages

### 🤖 Machine Learning & AI
- **ML Models**: Random Forest and Linear Regression for price prediction
- **Trading Signals**: AI-generated buy/sell signals with confidence scoring
- **Market Analysis**: Comprehensive market sentiment analysis
- **Feature Engineering**: Advanced technical indicators for ML models

### 💼 Portfolio Management
- **Portfolio Tracking**: Complete portfolio management system
- **Risk Analysis**: VaR, Sharpe ratio, portfolio volatility metrics
- **Position Management**: Detailed position tracking with P&L calculations
- **Performance Metrics**: Real-time portfolio performance monitoring

### ⚙️ Automated Trading Integration
- **N8N Workflow Integration**: Full integration with N8N automation platform
- **Auto-Trading Strategies**: Configurable automated trading strategies
- **Signal Generation**: ML and technical analysis-based trading signals
- **Webhook System**: Real-time communication with external systems

### 👤 User Management & Subscription
- **User Authentication**: Complete registration, login, and profile management
- **Subscription Plans**: Free, Basic, Premium, and Professional tiers
- **API Keys**: Secure API access with key management
- **KYC Integration**: User verification system

### 🔔 Real-Time Notifications & Alerts
- **WebSocket Integration**: Real-time notifications via WebSockets
- **Alert System**: Price, portfolio, and risk-based alerts
- **Multi-Channel**: Email, push, SMS notification support
- **Notification Preferences**: User-configurable notification settings

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework, Celery
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Real-time**: WebSockets with Django Channels
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Market Data**: yfinance API
- **Task Queue**: Redis
- **Deployment**: Docker, Gunicorn, Nginx

## Installation

### Prerequisites
- Python 3.9+
- pip
- virtualenv
- Redis
- PostgreSQL (optional, for production)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd debt-trading-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load initial data**
   ```bash
   python manage.py create_subscription_plans
   python manage.py create_notification_types
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Run Celery workers (in separate terminals)**
   ```bash
   celery -A debt_trading_platform worker -l info
   celery -A debt_trading_platform beat -l info
   ```

## Project Structure

```
debt-trading-platform/
├── accounts/              # User authentication and subscription management
├── debt_trading_platform/ # Main Django project settings
├── markets/              # Market data integration and models
├── ml_predictions/       # Machine learning models and predictions
├── notifications/        # Notification system and alerts
├── portfolio/            # Portfolio management and risk analysis
├── api_gateway/          # API gateway and external integrations
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Markets
- `GET /api/markets/tasi/` - Get TASI market overview
- `GET /api/markets/global/` - Get global markets overview
- `GET /api/markets/quote/<symbol>/` - Get stock quote

### ML Predictions
- `GET /api/ml/prediction/<symbol>/` - Get ML prediction for symbol
- `GET /api/ml/signals/` - Get trading signals
- `GET /api/ml/analysis/` - Get market analysis

### Portfolio
- `GET /api/portfolio/overview/` - Get portfolio overview
- `GET /api/portfolio/<id>/risk/` - Get portfolio risk analysis
- `POST /api/portfolio/<id>/optimize/` - Optimize portfolio

### Accounts
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `GET /api/accounts/subscription/plans/` - Get subscription plans

## Deployment

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

### Docker Deployment
See [DOCKER.md](DOCKER.md) for containerized deployment instructions.

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API
- [Django](https://www.djangoproject.com/) - Web framework
- [scikit-learn](https://scikit-learn.org/) - Machine learning library
- [N8N](https://n8n.io/) - Workflow automation tool

## Support

For support, please open an issue on GitHub or contact the maintainers.