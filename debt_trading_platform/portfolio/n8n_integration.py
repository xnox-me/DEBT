import requests
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from .auto_trading_models import (
    AutoTradingStrategy, AutoTradingSignal, WorkflowExecution,
    TradingBotConfiguration, AutoTradingLog
)
from .auto_trading_views import generate_strategy_signals, send_signal_to_n8n
from .models import Portfolio

logger = logging.getLogger('debt_trading')


class N8NIntegration:
    \"\"\"N8N workflow integration client\"\"\"
    
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url or getattr(settings, 'N8N_BASE_URL', 'http://localhost:5678')
        self.api_key = api_key or getattr(settings, 'N8N_API_KEY', None)
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({'X-N8N-API-KEY': self.api_key})
    
    def create_workflow(self, workflow_data):
        \"\"\"Create a new workflow in N8N\"\"\"
        try:
            response = self.session.post(
                f\"{self.base_url}/api/v1/workflows\",
                json=workflow_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f\"Error creating N8N workflow: {str(e)}\")
            return None
    
    def activate_workflow(self, workflow_id):
        \"\"\"Activate a workflow in N8N\"\"\"
        try:
            response = self.session.post(
                f\"{self.base_url}/api/v1/workflows/{workflow_id}/activate\",
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f\"Error activating N8N workflow {workflow_id}: {str(e)}\")
            return False
    
    def deactivate_workflow(self, workflow_id):
        \"\"\"Deactivate a workflow in N8N\"\"\"
        try:
            response = self.session.post(
                f\"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate\",
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f\"Error deactivating N8N workflow {workflow_id}: {str(e)}\")
            return False
    
    def get_execution_status(self, execution_id):
        \"\"\"Get execution status from N8N\"\"\"
        try:
            response = self.session.get(
                f\"{self.base_url}/api/v1/executions/{execution_id}\",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f\"Error getting N8N execution status {execution_id}: {str(e)}\")
            return None
    
    def trigger_workflow(self, workflow_id, data):
        \"\"\"Manually trigger a workflow\"\"\"
        try:
            response = self.session.post(
                f\"{self.base_url}/api/v1/workflows/{workflow_id}/trigger\",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f\"Error triggering N8N workflow {workflow_id}: {str(e)}\")
            return None


class TradingScheduler:
    \"\"\"Scheduler for automated trading tasks\"\"\"
    
    @staticmethod
    def is_trading_hours(bot_config=None):
        \"\"\"Check if current time is within trading hours\"\"\"
        if bot_config:
            start_time = bot_config.trading_start_time
            end_time = bot_config.trading_end_time
        else:
            start_time = datetime.strptime('09:00:00', '%H:%M:%S').time()
            end_time = datetime.strptime('16:00:00', '%H:%M:%S').time()
        
        current_time = datetime.now().time()
        return start_time <= current_time <= end_time
    
    @staticmethod
    def should_execute_strategy(strategy):
        \"\"\"Determine if strategy should be executed based on schedule\"\"\"
        if strategy.status != 'ACTIVE':
            return False
        
        # Check if bot is enabled
        try:
            bot_config = TradingBotConfiguration.objects.get(user=strategy.user)
            if not bot_config.is_enabled:
                return False
            
            # Check trading hours
            if not TradingScheduler.is_trading_hours(bot_config):
                return False
        except TradingBotConfiguration.DoesNotExist:
            return False
        
        # Check daily trade limits
        today_signals = strategy.signals.filter(
            created_at__date=datetime.now().date(),
            status__in=['EXECUTED', 'SENT']
        )
        
        if today_signals.count() >= strategy.max_daily_trades:
            return False
        
        # Check last execution time (avoid too frequent execution)
        if strategy.last_executed:
            time_since_last = datetime.now() - strategy.last_executed.replace(tzinfo=None)
            if time_since_last < timedelta(minutes=5):  # Minimum 5 minutes between executions
                return False
        
        return True


# Celery Tasks for Background Processing

@shared_task
def process_active_strategies():
    \"\"\"Process all active trading strategies\"\"\"
    try:
        active_strategies = AutoTradingStrategy.objects.filter(status='ACTIVE')
        
        processed_count = 0
        error_count = 0
        
        for strategy in active_strategies:
            try:
                if TradingScheduler.should_execute_strategy(strategy):
                    signals = generate_strategy_signals(strategy)
                    
                    strategy.last_executed = timezone.now()
                    strategy.save(update_fields=['last_executed'])
                    
                    processed_count += 1
                    
                    # Log successful processing
                    AutoTradingLog.objects.create(
                        strategy=strategy,
                        level='INFO',
                        category='STRATEGY_EXECUTION',
                        message=f'Strategy processed successfully, generated {len(signals)} signals',
                        context_data={
                            'signals_count': len(signals),
                            'task': 'process_active_strategies'
                        }
                    )
                    
            except Exception as e:
                error_count += 1
                logger.error(f\"Error processing strategy {strategy.id}: {str(e)}\")
                
                # Log error
                AutoTradingLog.objects.create(
                    strategy=strategy,
                    level='ERROR',
                    category='STRATEGY_EXECUTION',
                    message=f'Error processing strategy: {str(e)}',
                    context_data={
                        'error': str(e),
                        'task': 'process_active_strategies'
                    }
                )
        
        logger.info(f\"Processed {processed_count} strategies, {error_count} errors\")
        return {
            'processed': processed_count,
            'errors': error_count,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f\"Error in process_active_strategies task: {str(e)}\")
        return {'error': str(e)}


@shared_task
def sync_n8n_executions():
    \"\"\"Sync execution status from N8N\"\"\"
    try:
        n8n = N8NIntegration()
        
        # Get pending signals with N8N execution IDs
        pending_signals = AutoTradingSignal.objects.filter(
            status='SENT',
            n8n_execution_id__isnull=False
        )
        
        updated_count = 0
        
        for signal in pending_signals:
            try:
                execution_data = n8n.get_execution_status(signal.n8n_execution_id)
                
                if execution_data:
                    status = execution_data.get('finished', False)
                    success = execution_data.get('success', False)
                    
                    if status:
                        if success:
                            signal.status = 'EXECUTED'
                            signal.executed_at = timezone.now()
                        else:
                            signal.status = 'FAILED'
                            signal.error_message = execution_data.get('error', 'N8N execution failed')
                        
                        signal.execution_response = execution_data
                        signal.save()
                        updated_count += 1
                        
            except Exception as e:
                logger.error(f\"Error syncing signal {signal.id} with N8N: {str(e)}\")
                continue
        
        logger.info(f\"Synced {updated_count} signal executions with N8N\")
        return {'synced': updated_count}
        
    except Exception as e:
        logger.error(f\"Error in sync_n8n_executions task: {str(e)}\")
        return {'error': str(e)}


@shared_task
def update_portfolio_values():
    \"\"\"Update portfolio values for auto-trading strategies\"\"\"
    try:
        from .views import update_portfolio_value
        
        portfolios = Portfolio.objects.filter(
            is_active=True,
            auto_trading_strategies__status='ACTIVE'
        ).distinct()
        
        updated_count = 0
        
        for portfolio in portfolios:
            try:
                update_portfolio_value(portfolio)
                updated_count += 1
            except Exception as e:
                logger.error(f\"Error updating portfolio {portfolio.id}: {str(e)}\")
                continue
        
        logger.info(f\"Updated {updated_count} portfolio values\")
        return {'updated': updated_count}
        
    except Exception as e:
        logger.error(f\"Error in update_portfolio_values task: {str(e)}\")
        return {'error': str(e)}


@shared_task
def cleanup_old_logs():
    \"\"\"Clean up old trading logs to prevent database bloat\"\"\"
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = AutoTradingLog.objects.filter(
            timestamp__lt=cutoff_date,
            level__in=['DEBUG', 'INFO']
        ).delete()[0]
        
        logger.info(f\"Cleaned up {deleted_count} old trading logs\")
        return {'deleted': deleted_count}
        
    except Exception as e:
        logger.error(f\"Error in cleanup_old_logs task: {str(e)}\")
        return {'error': str(e)}


@shared_task
def generate_daily_report():
    \"\"\"Generate daily trading report\"\"\"
    try:
        today = datetime.now().date()
        
        # Get today's statistics
        strategies_active = AutoTradingStrategy.objects.filter(status='ACTIVE').count()
        signals_generated = AutoTradingSignal.objects.filter(created_at__date=today).count()
        signals_executed = AutoTradingSignal.objects.filter(
            executed_at__date=today,
            status='EXECUTED'
        ).count()
        
        # Calculate success rate
        success_rate = (signals_executed / signals_generated * 100) if signals_generated > 0 else 0
        
        report_data = {
            'date': today.isoformat(),
            'active_strategies': strategies_active,
            'signals_generated': signals_generated,
            'signals_executed': signals_executed,
            'success_rate': round(success_rate, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f\"Daily report generated: {report_data}\")
        return report_data
        
    except Exception as e:
        logger.error(f\"Error generating daily report: {str(e)}\")
        return {'error': str(e)}


# Utility Functions

def create_default_trading_workflow(strategy):
    \"\"\"Create a default N8N workflow for a trading strategy\"\"\"
    workflow_template = {
        \"name\": f\"DEBT Auto Trading - {strategy.name}\",
        \"active\": True,
        \"nodes\": [
            {
                \"parameters\": {
                    \"httpMethod\": \"POST\",
                    \"path\": f\"debt-trading-{strategy.id}\",
                    \"responseMode\": \"onReceived\",
                    \"options\": {}
                },
                \"name\": \"Trading Signal Webhook\",
                \"type\": \"n8n-nodes-base.webhook\",
                \"typeVersion\": 1,
                \"position\": [200, 200],
                \"id\": \"webhook-node\"
            },
            {
                \"parameters\": {
                    \"conditions\": {
                        \"string\": [
                            {
                                \"value1\": \"={{$json[\\\"confidence\\\"]}}\",
                                \"operation\": \"equal\",
                                \"value2\": \"HIGH\"
                            }
                        ]
                    }
                },
                \"name\": \"High Confidence?\",
                \"type\": \"n8n-nodes-base.if\",
                \"typeVersion\": 1,
                \"position\": [400, 200],
                \"id\": \"confidence-check\"
            },
            {
                \"parameters\": {
                    \"mode\": \"webhook\",
                    \"webhook\": {
                        \"httpMethod\": \"POST\",
                        \"url\": \"{{$json[\\\"callback_url\\\"]}}\",
                        \"sendBody\": True,
                        \"bodyParameters\": {
                            \"parameters\": [
                                {
                                    \"name\": \"execution_id\",
                                    \"value\": \"={{$execution.id}}\"
                                },
                                {
                                    \"name\": \"status\",
                                    \"value\": \"success\"
                                },
                                {
                                    \"name\": \"signal_id\",
                                    \"value\": \"={{$json[\\\"signal_id\\\"]}}\"
                                }
                            ]
                        }
                    }
                },
                \"name\": \"Send Confirmation\",
                \"type\": \"n8n-nodes-base.httpRequest\",
                \"typeVersion\": 1,
                \"position\": [600, 200],
                \"id\": \"confirmation-node\"
            },
            {
                \"parameters\": {
                    \"message\": \"=Trading signal processed: {{$json[\\\"signal_type\\\"]}} {{$json[\\\"symbol\\\"]}} at {{$json[\\\"target_price\\\"]}}\"
                },
                \"name\": \"Log Trade\",
                \"type\": \"n8n-nodes-base.function\",
                \"typeVersion\": 1,
                \"position\": [800, 200],
                \"id\": \"log-node\"
            }
        ],
        \"connections\": {
            \"Trading Signal Webhook\": {
                \"main\": [
                    [
                        {
                            \"node\": \"High Confidence?\",
                            \"type\": \"main\",
                            \"index\": 0
                        }
                    ]
                ]
            },
            \"High Confidence?\": {
                \"main\": [
                    [
                        {
                            \"node\": \"Send Confirmation\",
                            \"type\": \"main\",
                            \"index\": 0
                        }
                    ]
                ]
            },
            \"Send Confirmation\": {
                \"main\": [
                    [
                        {
                            \"node\": \"Log Trade\",
                            \"type\": \"main\",
                            \"index\": 0
                        }
                    ]
                ]
            }
        },
        \"settings\": {
            \"timezone\": \"Asia/Riyadh\"
        },
        \"tags\": [
            {
                \"name\": \"DEBT Trading\"
            },
            {
                \"name\": \"Automated\"
            }
        ]
    }
    
    return workflow_template


def setup_strategy_n8n_integration(strategy, n8n_base_url):
    \"\"\"Set up N8N integration for a trading strategy\"\"\"
    try:
        n8n = N8NIntegration()
        
        # Create workflow
        workflow_data = create_default_trading_workflow(strategy)
        result = n8n.create_workflow(workflow_data)
        
        if result and 'id' in result:
            workflow_id = result['id']
            
            # Activate workflow
            if n8n.activate_workflow(workflow_id):
                # Update strategy with N8N details
                strategy.n8n_workflow_id = workflow_id
                strategy.n8n_webhook_url = f\"{n8n_base_url}/webhook/debt-trading-{strategy.id}\"
                strategy.save()
                
                return True, f\"N8N workflow created with ID: {workflow_id}\"
            else:
                return False, \"Failed to activate N8N workflow\"
        else:
            return False, \"Failed to create N8N workflow\"
            
    except Exception as e:
        logger.error(f\"Error setting up N8N integration for strategy {strategy.id}: {str(e)}\")
        return False, str(e)