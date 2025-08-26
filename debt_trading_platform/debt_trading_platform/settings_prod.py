"""
Django production settings for debt_trading_platform.

This file contains production-specific configuration that overrides
the development settings in settings.py.
"""

import os
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# This should be set in environment variables
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-here')

# Allowed hosts - should be set in environment variables
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database configuration for production
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'debt_trading_prod'),
        'USER': os.environ.get('DB_USER', 'debt_trading_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'secure_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Redis configuration for production
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email configuration for production
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.yourprovider.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@yourdomain.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your_email_password')

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/debt_trading/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'debt_trading': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Static files configuration for production
STATIC_ROOT = '/opt/debt_trading/staticfiles'
MEDIA_ROOT = '/opt/debt_trading/media'

# Performance optimizations
CONN_MAX_AGE = 60
USE_TZ = True

# N8N Integration for production
N8N_BASE_URL = os.environ.get('N8N_BASE_URL', 'https://n8n.yourdomain.com')
N8N_API_KEY = os.environ.get('N8N_API_KEY', None)
N8N_WEBHOOK_BASE_URL = os.environ.get('N8N_WEBHOOK_BASE_URL', 'https://n8n.yourdomain.com/webhook')

# Payment Gateway Configuration
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# API Rate Limiting for production
API_SETTINGS = {
    'default_page_size': 50,
    'max_page_size': 1000,
    'rate_limit': '10000/day',
    'throttle_anon': '1000/day',
    'throttle_user': '10000/day',
}

# Market Data Configuration for production
MARKET_DATA_UPDATE_INTERVAL = 60  # seconds (increased for production)
TASI_COMPANIES = [
    '2222.SR',  # Saudi Aramco
    '1120.SR',  # Al Rajhi Bank
    '2030.SR',  # SABIC
    '1180.SR',  # Al Rajhi Company
    '2380.SR',  # Petrochemical Industries Company
    '4030.SR',  # National Petrochemical Company
    '2170.SR',  # Riyad Bank
    '8210.SR',  # Alinma Bank
    '1301.SR',  # Saudi Electricity
    '7010.SR',  # Saudi Telecom
]

GLOBAL_MARKETS = {
    'USA': ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'NVDA', 'JPM', 'V', 'JNJ'],
    'UK': ['SHEL.L', 'BP.L', 'VOD.L', 'HSBA.L', 'BARC.L'],
    'JAPAN': ['7203.T', '9984.T', '8306.T', '8035.T'],
    'GERMANY': ['SAP.DE', 'SIE.DE', 'BAS.DE', 'BMW.DE'],
    'FRANCE': ['MC.PA', 'SAN.PA', 'BNP.PA', 'OR.PA'],
    'INDIA': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS'],
    'CHINA': ['BABA', 'TCEHY', 'JD', 'BIDU'],
    'CRYPTO': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL-USD'],
    'PRECIOUS': ['GC=F', 'SI=F', 'PL=F', 'PA=F']  # Gold, Silver, Platinum, Palladium futures
}

# Machine Learning Configuration for production
ML_MODEL_UPDATE_INTERVAL = 7200  # 2 hours (increased for production)
ML_PREDICTION_CACHE_TIMEOUT = 3600  # 1 hour (increased for production)