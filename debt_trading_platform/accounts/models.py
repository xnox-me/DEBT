from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid


class UserProfile(models.Model):
    """Extended user profile for trading platform"""
    
    RISK_TOLERANCE_CHOICES = [
        ('LOW', 'Conservative'),
        ('MEDIUM', 'Moderate'),
        ('HIGH', 'Aggressive'),
        ('VERY_HIGH', 'Very Aggressive'),
    ]
    
    INVESTMENT_EXPERIENCE_CHOICES = [
        ('BEGINNER', 'Beginner (0-1 years)'),
        ('INTERMEDIATE', 'Intermediate (1-5 years)'),
        ('ADVANCED', 'Advanced (5-10 years)'),
        ('EXPERT', 'Expert (10+ years)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    
    # Trading Profile
    risk_tolerance = models.CharField(max_length=20, choices=RISK_TOLERANCE_CHOICES, default='MEDIUM')
    investment_experience = models.CharField(max_length=20, choices=INVESTMENT_EXPERIENCE_CHOICES, default='BEGINNER')
    investment_goals = models.TextField(blank=True)
    
    # Platform Settings
    preferred_currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='Asia/Riyadh')
    language = models.CharField(max_length=10, default='en')
    
    # Notifications Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    trading_alerts = models.BooleanField(default=True)
    market_news = models.BooleanField(default=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    kyc_status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ], default='PENDING')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class SubscriptionPlan(models.Model):
    """Subscription plans for the trading platform"""
    
    PLAN_TYPES = [
        ('FREE', 'Free Plan'),
        ('BASIC', 'Basic Plan'),
        ('PREMIUM', 'Premium Plan'),
        ('PROFESSIONAL', 'Professional Plan'),
        ('ENTERPRISE', 'Enterprise Plan'),
    ]
    
    BILLING_CYCLES = [
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUALLY', 'Annually'),
        ('LIFETIME', 'Lifetime'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    currency = models.CharField(max_length=3, default='USD')
    
    # Plan Features
    max_portfolios = models.IntegerField(default=1)
    max_positions_per_portfolio = models.IntegerField(default=10)
    max_auto_strategies = models.IntegerField(default=0)
    
    # API Limits
    api_calls_per_day = models.IntegerField(default=1000)
    real_time_data = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    
    # Features Access
    ml_predictions = models.BooleanField(default=False)
    auto_trading = models.BooleanField(default=False)
    portfolio_optimization = models.BooleanField(default=False)
    risk_analysis = models.BooleanField(default=False)
    custom_alerts = models.BooleanField(default=False)
    
    # Support
    email_support = models.BooleanField(default=True)
    priority_support = models.BooleanField(default=False)
    phone_support = models.BooleanField(default=False)
    
    # Plan Status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'price']
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}/{self.billing_cycle}"


class UserSubscription(models.Model):
    """User's subscription details"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('PENDING', 'Pending Payment'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    
    # Subscription Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    
    # Payment Information
    payment_method = models.CharField(max_length=50, blank=True)
    subscription_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    external_subscription_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe, PayPal, etc.
    
    # Usage Tracking
    api_calls_used = models.IntegerField(default=0)
    portfolios_created = models.IntegerField(default=0)
    strategies_created = models.IntegerField(default=0)
    
    # Billing
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE' and self.end_date > timezone.now()
    
    @property
    def days_remaining(self):
        if self.is_active:
            return (self.end_date - timezone.now()).days
        return 0
    
    def extend_subscription(self, days):
        """Extend subscription by specified days"""
        self.end_date += timedelta(days=days)
        self.save()
    
    def cancel_subscription(self):
        """Cancel the subscription"""
        self.status = 'CANCELLED'
        self.auto_renew = False
        self.save()


class Payment(models.Model):
    """Payment records"""
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CRYPTO', 'Cryptocurrency'),
        ('APPLE_PAY', 'Apple Pay'),
        ('GOOGLE_PAY', 'Google Pay'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    payment_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    external_payment_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe, PayPal, etc.
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Payment Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Provider Details
    provider = models.CharField(max_length=50, blank=True)  # Stripe, PayPal, etc.
    provider_response = models.JSONField(default=dict)
    
    # Metadata
    description = models.TextField(blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency} ({self.status})"


class APIKey(models.Model):
    """API keys for external access"""
    
    KEY_TYPES = [
        ('READ_ONLY', 'Read Only'),
        ('TRADING', 'Trading Enabled'),
        ('FULL_ACCESS', 'Full Access'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    
    # Key Details
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    secret = models.CharField(max_length=128)
    key_type = models.CharField(max_length=20, choices=KEY_TYPES, default='READ_ONLY')
    
    # Permissions
    can_read_portfolio = models.BooleanField(default=True)
    can_place_orders = models.BooleanField(default=False)
    can_cancel_orders = models.BooleanField(default=False)
    can_withdraw = models.BooleanField(default=False)
    
    # Rate Limiting
    calls_per_minute = models.IntegerField(default=60)
    calls_per_day = models.IntegerField(default=10000)
    
    # Usage Statistics
    total_calls = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Security
    allowed_ips = models.TextField(blank=True, help_text="Comma-separated list of allowed IP addresses")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.key_type})"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        if not self.secret:
            self.secret = self.generate_secret()
        super().save(*args, **kwargs)
    
    def generate_key(self):
        """Generate API key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def generate_secret(self):
        """Generate API secret"""
        import secrets
        return secrets.token_urlsafe(64)


class LoginAttempt(models.Model):
    """Track login attempts for security"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='login_attempts')
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username} - {status} - {self.created_at}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    NOTIFICATION_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Trading Notifications
    trade_executions = models.BooleanField(default=True)
    order_fills = models.BooleanField(default=True)
    price_alerts = models.BooleanField(default=True)
    portfolio_updates = models.BooleanField(default=True)
    
    # Market Notifications
    market_news = models.BooleanField(default=False)
    earnings_reports = models.BooleanField(default=False)
    analyst_ratings = models.BooleanField(default=False)
    
    # Account Notifications
    login_alerts = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    subscription_updates = models.BooleanField(default=True)
    
    # ML/Auto-trading Notifications
    ml_predictions = models.BooleanField(default=False)
    auto_trading_alerts = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'notification_type']
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"