# DEBT Trading Platform - Production Deployment Guide

## System Requirements

### Hardware Requirements
- Minimum: 2 CPU cores, 4GB RAM, 20GB SSD
- Recommended: 4+ CPU cores, 8GB+ RAM, 50GB+ SSD

### Software Requirements
- Ubuntu 20.04 LTS or newer (recommended)
- Python 3.9+
- PostgreSQL 12+ (recommended) or SQLite (for development)
- Redis 6.0+ (for caching and background tasks)
- Node.js 16+ (for frontend assets)
- Nginx (for reverse proxy and static file serving)
- Certbot (for SSL certificates)

## Installation Steps

### 1. System Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx
sudo apt install -y certbot python3-certbot-nginx
sudo apt install -y supervisor
sudo apt install -y git curl wget
```

### 2. Application Setup

```bash
# Create application user
sudo adduser --system --group --shell /bin/bash debt_trading

# Create application directory
sudo mkdir -p /opt/debt_trading
sudo chown debt_trading:debt_trading /opt/debt_trading

# Clone the application (or copy files)
sudo -u debt_trading git clone <repository_url> /opt/debt_trading

# Create virtual environment
sudo -u debt_trading python3 -m venv /opt/debt_trading/.venv
source /opt/debt_trading/.venv/bin/activate

# Install Python dependencies
pip install -r /opt/debt_trading/requirements.txt
```

### 3. Database Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE debt_trading_prod;
CREATE USER debt_trading_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE debt_trading_prod TO debt_trading_user;
ALTER USER debt_trading_user CREATEDB;
\q
```

### 4. Environment Configuration

Create `/opt/debt_trading/.env`:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your_production_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=debt_trading_prod
DB_USER=debt_trading_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis for Caching and Background Tasks
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password

# N8N Integration
N8N_BASE_URL=https://n8n.yourdomain.com
N8N_API_KEY=your_n8n_api_key

# Payment Gateway (Stripe/PayPal)
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
STRIPE_SECRET_KEY=sk_live_your_stripe_key

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 5. Django Setup

```bash
# Activate virtual environment
source /opt/debt_trading/.venv/bin/activate
cd /opt/debt_trading

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Load initial data
python manage.py create_subscription_plans
```

### 6. Gunicorn Configuration

Create `/opt/debt_trading/gunicorn.conf.py`:

```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/debt_trading/access.log"
errorlog = "/var/log/debt_trading/error.log"
loglevel = "info"
capture_output = True

# Process naming
proc_name = "debt_trading"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/var/run/debt_trading.pid"
user = "debt_trading"
group = "debt_trading"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### 7. Supervisor Configuration

Create `/etc/supervisor/conf.d/debt_trading.conf`:

```ini
[group:debt_trading]
programs=web,celery_beat,celery_worker

[program:debt_trading_web]
command=/opt/debt_trading/.venv/bin/gunicorn --config /opt/debt_trading/gunicorn.conf.py debt_trading_platform.wsgi:application
directory=/opt/debt_trading
user=debt_trading
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/debt_trading/gunicorn.log

[program:debt_trading_celery_worker]
command=/opt/debt_trading/.venv/bin/celery -A debt_trading_platform worker -l info -Q trading,market_data,ml_predictions,portfolio,reports,maintenance
directory=/opt/debt_trading
user=debt_trading
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/debt_trading/celery_worker.log

[program:debt_trading_celery_beat]
command=/opt/debt_trading/.venv/bin/celery -A debt_trading_platform beat -l info
directory=/opt/debt_trading
user=debt_trading
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/debt_trading/celery_beat.log
```

### 8. Nginx Configuration

Create `/etc/nginx/sites-available/debt_trading`:

```nginx
upstream debt_trading_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect all HTTP requests to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Static files
    location /static/ {
        alias /opt/debt_trading/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/debt_trading/media/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # Application
    location / {
        proxy_pass http://debt_trading_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Logging
    access_log /var/log/nginx/debt_trading_access.log;
    error_log /var/log/nginx/debt_trading_error.log;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/debt_trading /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. SSL Certificate Setup

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 10. Log Rotation

Create `/etc/logrotate.d/debt_trading`:

```bash
/var/log/debt_trading/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 debt_trading debt_trading
    sharedscripts
    postrotate
        supervisorctl restart debt_trading:*
    endscript
}
```

### 11. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Check status
sudo ufw status
```

### 12. Monitoring and Backup

#### Backup Script

Create `/opt/debt_trading/scripts/backup.sh`:

```bash
#!/bin/bash

# Backup script for DEBT Trading Platform
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/debt_trading/backups"
DB_NAME="debt_trading_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U debt_trading_user -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/debt_trading/media/

# Compress and retain last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

#### Cron Jobs

Add to crontab (`sudo crontab -e`):

```bash
# Daily backup at 2 AM
0 2 * * * /opt/debt_trading/scripts/backup.sh

# Weekly system update on Sunday at 3 AM
0 3 * * 0 apt update && apt upgrade -y

# Daily log rotation check
0 4 * * * logrotate /etc/logrotate.d/debt_trading
```

## Starting the Application

```bash
# Start all services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start debt_trading:*

# Check status
sudo supervisorctl status

# Restart Nginx
sudo systemctl restart nginx
```

## Maintenance Commands

```bash
# Restart application
sudo supervisorctl restart debt_trading:*

# View logs
sudo supervisorctl tail -f debt_trading:debt_trading_web

# Update application
cd /opt/debt_trading
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart debt_trading:*
```

## Troubleshooting

1. **Application not starting**: Check logs in `/var/log/debt_trading/`
2. **Database connection issues**: Verify database credentials and PostgreSQL service status
3. **Static files not loading**: Ensure `collectstatic` was run and Nginx configuration is correct
4. **SSL certificate issues**: Check certificate paths and renewal status
5. **Background tasks not running**: Verify Celery worker and beat processes

## Security Considerations

1. Use strong, unique passwords for all services
2. Regularly update system packages and application dependencies
3. Restrict SSH access and use key-based authentication
4. Implement proper firewall rules
5. Regular security audits and penetration testing
6. Monitor logs for suspicious activity
7. Keep backups and test restoration procedures