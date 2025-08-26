from django.core.management.base import BaseCommand
from accounts.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Create default subscription plans'
    
    def handle(self, *args, **options):
        # Free Plan
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Free Plan',
            plan_type='FREE',
            defaults={
                'description': 'Perfect for beginners to explore the platform',
                'price': 0.00,
                'billing_cycle': 'LIFETIME',
                'currency': 'USD',
                'max_portfolios': 1,
                'max_positions_per_portfolio': 5,
                'max_auto_strategies': 0,
                'api_calls_per_day': 100,
                'real_time_data': False,
                'advanced_analytics': False,
                'ml_predictions': False,
                'auto_trading': False,
                'portfolio_optimization': False,
                'risk_analysis': True,
                'custom_alerts': False,
                'email_support': True,
                'priority_support': False,
                'phone_support': False,
                'is_active': True,
                'is_popular': False,
                'sort_order': 1
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {free_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'{free_plan.name} already exists')
            )
        
        # Basic Plan
        basic_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Basic Plan',
            plan_type='BASIC',
            defaults={
                'description': 'For active traders with essential features',
                'price': 9.99,
                'billing_cycle': 'MONTHLY',
                'currency': 'USD',
                'max_portfolios': 3,
                'max_positions_per_portfolio': 20,
                'max_auto_strategies': 1,
                'api_calls_per_day': 1000,
                'real_time_data': True,
                'advanced_analytics': True,
                'ml_predictions': True,
                'auto_trading': False,
                'portfolio_optimization': True,
                'risk_analysis': True,
                'custom_alerts': True,
                'email_support': True,
                'priority_support': False,
                'phone_support': False,
                'is_active': True,
                'is_popular': True,
                'sort_order': 2
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {basic_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'{basic_plan.name} already exists')
            )
        
        # Premium Plan
        premium_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Premium Plan',
            plan_type='PREMIUM',
            defaults={
                'description': 'Advanced features for serious traders',
                'price': 29.99,
                'billing_cycle': 'MONTHLY',
                'currency': 'USD',
                'max_portfolios': 10,
                'max_positions_per_portfolio': 100,
                'max_auto_strategies': 5,
                'api_calls_per_day': 10000,
                'real_time_data': True,
                'advanced_analytics': True,
                'ml_predictions': True,
                'auto_trading': True,
                'portfolio_optimization': True,
                'risk_analysis': True,
                'custom_alerts': True,
                'email_support': True,
                'priority_support': True,
                'phone_support': False,
                'is_active': True,
                'is_popular': False,
                'sort_order': 3
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {premium_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'{premium_plan.name} already exists')
            )
        
        # Professional Plan
        professional_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Professional Plan',
            plan_type='PROFESSIONAL',
            defaults={
                'description': 'Complete trading solution with all features',
                'price': 99.99,
                'billing_cycle': 'MONTHLY',
                'currency': 'USD',
                'max_portfolios': 50,
                'max_positions_per_portfolio': 500,
                'max_auto_strategies': 20,
                'api_calls_per_day': 100000,
                'real_time_data': True,
                'advanced_analytics': True,
                'ml_predictions': True,
                'auto_trading': True,
                'portfolio_optimization': True,
                'risk_analysis': True,
                'custom_alerts': True,
                'email_support': True,
                'priority_support': True,
                'phone_support': True,
                'is_active': True,
                'is_popular': False,
                'sort_order': 4
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {professional_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'{professional_plan.name} already exists')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created default subscription plans')
        )