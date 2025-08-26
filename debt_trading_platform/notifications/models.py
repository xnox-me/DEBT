from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class NotificationType(models.Model):
    """Types of notifications available in the system"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, default='blue')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """Individual notification records"""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('UNREAD', 'Unread'),
        ('READ', 'Read'),
        ('ARCHIVED', 'Archived'),
        ('DELETED', 'Deleted'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='notifications')
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # Additional structured data
    
    # Metadata
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNREAD')
    
    # Related Objects
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=100, blank=True)
    
    # Delivery
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Read Tracking
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == 'UNREAD':
            self.status = 'READ'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at', 'updated_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.status == 'READ':
            self.status = 'UNREAD'
            self.read_at = None
            self.save(update_fields=['status', 'read_at', 'updated_at'])


class UserNotificationPreference(models.Model):
    """User preferences for different notification types"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_prefs')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='user_preferences')
    
    # Delivery Methods
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)
    
    # Timing Preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Frequency
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'notification_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type.name}"


class AlertRule(models.Model):
    """Rules for automated alerts based on market conditions"""
    
    ALERT_TYPES = [
        ('PRICE_THRESHOLD', 'Price Threshold'),
        ('VOLUME_SPIKE', 'Volume Spike'),
        ('TECHNICAL_INDICATOR', 'Technical Indicator'),
        ('NEWS_EVENT', 'News Event'),
        ('PORTFOLIO_CHANGE', 'Portfolio Change'),
        ('RISK_METRIC', 'Risk Metric'),
        ('ML_PREDICTION', 'ML Prediction'),
    ]
    
    FREQUENCY_CHOICES = [
        ('ONCE', 'Once'),
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_rules')
    
    # Alert Details
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    
    # Trigger Conditions
    symbol = models.CharField(max_length=20, blank=True)
    condition_field = models.CharField(max_length=50)  # e.g., 'price', 'volume', 'rsi'
    condition_operator = models.CharField(max_length=10)  # e.g., '>', '<', '==', 'crosses_above'
    condition_value = models.CharField(max_length=50)  # Can be number, percentage, etc.
    
    # Additional Parameters
    parameters = models.JSONField(default=dict, blank=True)
    
    # Notification Settings
    notification_channels = models.JSONField(default=list)  # ['email', 'push', 'sms']
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='NORMAL')
    
    # Schedule
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='ONCE')
    last_triggered = models.DateTimeField(null=True, blank=True)
    next_check = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    trigger_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class AlertTrigger(models.Model):
    """Record of when alerts were triggered"""
    
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='triggers')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='alert_triggers', null=True, blank=True)
    
    # Trigger Details
    triggered_at = models.DateTimeField(auto_now_add=True)
    trigger_data = models.JSONField(default=dict)
    trigger_value = models.CharField(max_length=100)
    
    # Status
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"Trigger for {self.alert_rule.name} at {self.triggered_at}"


class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    
    TEMPLATE_TYPES = [
        ('EMAIL', 'Email'),
        ('PUSH', 'Push Notification'),
        ('SMS', 'SMS'),
        ('IN_APP', 'In-App'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=10, choices=TEMPLATE_TYPES)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='templates')
    
    subject = models.CharField(max_length=200, blank=True)  # For email
    title_template = models.TextField()  # Template for notification title
    message_template = models.TextField()  # Template for notification message
    
    # Variables that can be used in templates
    available_variables = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'template_type']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class EmailNotification(models.Model):
    """Track email notifications sent to users"""
    
    STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='email_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_notifications')
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    from_email = models.EmailField()
    to_email = models.EmailField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='QUEUED')
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Provider Information
    provider = models.CharField(max_length=50, blank=True)
    provider_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email to {self.to_email} - {self.status}"


class PushNotification(models.Model):
    """Track push notifications sent to devices"""
    
    STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='push_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_notifications')
    
    device_token = models.CharField(max_length=255)
    platform = models.CharField(max_length=20)  # iOS, Android, Web
    
    message = models.TextField()
    payload = models.JSONField(default=dict)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='QUEUED')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Provider Information
    provider = models.CharField(max_length=50, blank=True)
    provider_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Push to {self.platform} - {self.status}"


class Device(models.Model):
    """User devices for push notifications"""
    
    PLATFORM_CHOICES = [
        ('IOS', 'iOS'),
        ('ANDROID', 'Android'),
        ('WEB', 'Web Browser'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    
    device_token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    # Device Information
    name = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    
    # Preferences
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'device_token']
    
    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.name})"


class NotificationStatistics(models.Model):
    """Statistics for notification delivery and engagement"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_stats')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='stats')
    
    # Counts
    total_sent = models.IntegerField(default=0)
    total_read = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)
    
    # Rates
    open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Time-based metrics
    avg_response_time = models.DurationField(null=True, blank=True)
    
    # Last updated
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'notification_type']
        verbose_name_plural = "Notification Statistics"
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type.name} Stats"