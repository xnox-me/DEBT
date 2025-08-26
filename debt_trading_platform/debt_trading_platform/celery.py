from celery import Celery
from celery.schedules import crontab
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'debt_trading_platform.settings')

app = Celery('debt_trading_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat Schedule for Automated Trading
app.conf.beat_schedule = {
    # Process active trading strategies every 5 minutes during trading hours
    'process-active-strategies': {
        'task': 'portfolio.n8n_integration.process_active_strategies',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'queue': 'trading'}
    },
    
    # Sync N8N executions every 2 minutes
    'sync-n8n-executions': {
        'task': 'portfolio.n8n_integration.sync_n8n_executions',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes
        'options': {'queue': 'trading'}
    },
    
    # Update portfolio values every 10 minutes
    'update-portfolio-values': {
        'task': 'portfolio.n8n_integration.update_portfolio_values',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {'queue': 'portfolio'}
    },
    
    # Generate daily report at 6 PM
    'generate-daily-report': {
        'task': 'portfolio.n8n_integration.generate_daily_report',
        'schedule': crontab(hour=18, minute=0),  # 6:00 PM daily
        'options': {'queue': 'reports'}
    },
    
    # Clean up old logs weekly on Sunday at 2 AM
    'cleanup-old-logs': {
        'task': 'portfolio.n8n_integration.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2:00 AM
        'options': {'queue': 'maintenance'}
    },
    
    # Market data sync every hour
    'sync-market-data': {
        'task': 'markets.tasks.sync_market_data',
        'schedule': crontab(minute=0),  # Every hour
        'options': {'queue': 'market_data'}
    },
    
    # Generate ML predictions every 30 minutes
    'generate-ml-predictions': {
        'task': 'ml_predictions.tasks.generate_batch_predictions',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {'queue': 'ml_predictions'}
    },
}

# Celery Configuration
app.conf.update(
    # Task routing
    task_routes={
        'portfolio.n8n_integration.*': {'queue': 'trading'},
        'markets.tasks.*': {'queue': 'market_data'},
        'ml_predictions.tasks.*': {'queue': 'ml_predictions'},
    },
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Riyadh',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Result backend
    result_backend='redis://localhost:6379/0',
    result_expires=3600,  # 1 hour
    
    # Broker settings
    broker_url='redis://localhost:6379/0',
    broker_transport_options={
        'visibility_timeout': 3600,
        'fanout_prefix': True,
        'fanout_patterns': True
    },
    
    # Security
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')