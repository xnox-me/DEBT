from django.core.management.base import BaseCommand
from notifications.models import NotificationType

class Command(BaseCommand):
    help = 'Create default notification types'
    
    def handle(self, *args, **options):
        # Define default notification types
        default_types = [
            {
                'name': 'market_alert',
                'description': 'Market price and volume alerts',
                'icon': 'trending_up',
                'color': 'red'
            },
            {
                'name': 'portfolio_alert',
                'description': 'Portfolio value and performance alerts',
                'icon': 'account_balance_wallet',
                'color': 'blue'
            },
            {
                'name': 'ml_prediction',
                'description': 'Machine learning trading predictions',
                'icon': 'auto_graph',
                'color': 'purple'
            },
            {
                'name': 'auto_trading',
                'description': 'Automated trading execution alerts',
                'icon': 'bolt',
                'color': 'green'
            },
            {
                'name': 'risk_alert',
                'description': 'Portfolio risk and exposure alerts',
                'icon': 'warning',
                'color': 'orange'
            },
            {
                'name': 'news_alert',
                'description': 'Market news and events',
                'icon': 'article',
                'color': 'indigo'
            },
            {
                'name': 'system_alert',
                'description': 'System maintenance and updates',
                'icon': 'build',
                'color': 'gray'
            },
            {
                'name': 'subscription',
                'description': 'Subscription and billing notifications',
                'icon': 'credit_card',
                'color': 'teal'
            }
        ]
        
        created_count = 0
        for type_data in default_types:
            notification_type, created = NotificationType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created notification type: {notification_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Notification type already exists: {notification_type.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} notification types')
        )