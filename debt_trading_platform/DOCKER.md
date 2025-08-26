# DEBT Trading Platform - Docker Configuration

## Dockerfile

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_prod.txt /app/
RUN pip install --no-cache-dir -r requirements_prod.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "debt_trading_platform.wsgi:application"]
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=debt_trading
      - POSTGRES_USER=debt_user
      - POSTGRES_PASSWORD=debt_password
    restart: unless-stopped

  # Redis for caching and background tasks
  redis:
    image: redis:7-alpine
    restart: unless-stopped

  # Main Django Application
  web:
    build: .
    command: gunicorn debt_trading_platform.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=0
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=debt_trading
      - DB_USER=debt_user
      - DB_PASSWORD=debt_password
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # Celery Worker for background tasks
  celery_worker:
    build: .
    command: celery -A debt_trading_platform worker -l info
    volumes:
      - .:/app
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=debt_trading
      - DB_USER=debt_user
      - DB_PASSWORD=debt_password
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # Celery Beat for scheduled tasks
  celery_beat:
    build: .
    command: celery -A debt_trading_platform beat -l info
    volumes:
      - .:/app
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=debt_trading
      - DB_USER=debt_user
      - DB_PASSWORD=debt_password
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx:/etc/nginx/conf.d
      - ./staticfiles:/static
      - ./media:/media
      - ./certs:/etc/letsencrypt
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

## .dockerignore

```
.git
.gitignore
README.md
Dockerfile
.dockerignore
.env
*.log
*.sqlite3
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
.env.local
.env.*.local
.pytest_cache/
.coverage
htmlcov/
.pytest_cache/
.coverage
htmlcov/
.pytest_cache/
.coverage
htmlcov/
```

## config/nginx/nginx.conf

```nginx
upstream debt_trading_app {
    server web:8000;
}

server {
    listen 80;
    server_name localhost;
    
    # Static files
    location /static/ {
        alias /static/;
    }
    
    location /media/ {
        alias /media/;
    }
    
    # Application
    location / {
        proxy_pass http://debt_trading_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Environment Variables (.env)

```
# Django Settings
DEBUG=0
SECRET_KEY=your_production_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=debt_trading
DB_USER=debt_user
DB_PASSWORD=debt_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (if needed)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.yourprovider.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your_email@yourdomain.com
# EMAIL_HOST_PASSWORD=your_email_password
```

## Deployment Commands

### Build and Run

```bash
# Build the images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Initial Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Load initial data
docker-compose exec web python manage.py create_subscription_plans
```

### Maintenance

```bash
# Restart specific service
docker-compose restart web

# View running containers
docker-compose ps

# Execute commands in container
docker-compose exec web bash

# Backup database
docker-compose exec db pg_dump -U debt_user debt_trading > backup.sql
```

## Scaling

To scale the application, you can adjust the docker-compose.yml file:

```yaml
# Scale web workers
web:
  # ... other settings
  deploy:
    replicas: 3

# Scale celery workers
celery_worker:
  # ... other settings
  deploy:
    replicas: 2
```

Or use docker-compose scale command:

```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3

# Scale celery workers to 2 instances
docker-compose up -d --scale celery_worker=2
```

## Monitoring

You can add monitoring services to the docker-compose.yml:

```yaml
  # Monitoring with Prometheus and Grafana
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus:/etc/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  postgres_data:
  grafana_data:
```

## Backup and Restore

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U debt_user debt_trading > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U debt_user debt_trading < backup_file.sql
```

### Media Files Backup

```bash
# Create backup of media files
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

This Docker configuration provides a complete containerized environment for the DEBT Trading Platform that can be easily deployed to any cloud provider or on-premises infrastructure.