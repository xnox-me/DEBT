from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Notification, NotificationType, UserNotificationPreference,
    AlertRule, AlertTrigger, NotificationTemplate,
    EmailNotification, PushNotification, Device,
    NotificationStatistics
)


class NotificationTypeSerializer(serializers.ModelSerializer):
    """Serializer for NotificationType model"""
    
    class Meta:
        model = NotificationType
        fields = ['id', 'name', 'description', 'icon', 'color', 'is_active', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    notification_type = NotificationTypeSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title', 'message', 'data',
            'priority', 'status', 'related_object_type', 'related_object_id',
            'is_sent', 'sent_at', 'read_at', 'expires_at', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'is_sent', 'sent_at', 'read_at']


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserNotificationPreference model"""
    notification_type = NotificationTypeSerializer(read_only=True)
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'email_enabled', 'push_enabled',
            'sms_enabled', 'in_app_enabled', 'quiet_hours_start',
            'quiet_hours_end', 'daily_digest', 'weekly_digest',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user']


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule model"""
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'user', 'name', 'description', 'alert_type', 'symbol',
            'condition_field', 'condition_operator', 'condition_value',
            'parameters', 'notification_channels', 'priority', 'frequency',
            'last_triggered', 'next_check', 'is_active', 'trigger_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'last_triggered', 'next_check', 'trigger_count']


class AlertTriggerSerializer(serializers.ModelSerializer):
    """Serializer for AlertTrigger model"""
    
    class Meta:
        model = AlertTrigger
        fields = [
            'id', 'alert_rule', 'notification', 'triggered_at',
            'trigger_data', 'trigger_value', 'is_processed', 'processed_at'
        ]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    notification_type = NotificationTypeSerializer(read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'template_type', 'notification_type',
            'subject', 'title_template', 'message_template',
            'available_variables', 'is_active', 'created_at', 'updated_at'
        ]


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Serializer for EmailNotification model"""
    
    class Meta:
        model = EmailNotification
        fields = [
            'id', 'notification', 'recipient', 'subject', 'body',
            'from_email', 'to_email', 'status', 'sent_at',
            'provider', 'provider_response', 'created_at'
        ]


class PushNotificationSerializer(serializers.ModelSerializer):
    """Serializer for PushNotification model"""
    
    class Meta:
        model = PushNotification
        fields = [
            'id', 'notification', 'recipient', 'device_token', 'platform',
            'message', 'payload', 'status', 'sent_at', 'delivered_at',
            'provider', 'provider_response', 'created_at'
        ]


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""
    
    class Meta:
        model = Device
        fields = [
            'id', 'user', 'device_token', 'platform', 'name',
            'model', 'os_version', 'is_active', 'last_seen', 'created_at'
        ]
        read_only_fields = ['user', 'last_seen']


class NotificationStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for NotificationStatistics model"""
    
    notification_type = NotificationTypeSerializer(read_only=True)
    
    class Meta:
        model = NotificationStatistics
        fields = [
            'id', 'user', 'notification_type', 'total_sent', 'total_read',
            'total_clicked', 'open_rate', 'click_rate', 'avg_response_time',
            'last_updated'
        ]


class NotificationSummarySerializer(serializers.Serializer):
    """Serializer for notification summary data"""
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    read_notifications = serializers.IntegerField()
    recent_notifications = serializers.IntegerField()
    notification_types = serializers.DictField(
        child=serializers.IntegerField(),
        required=False
    )


class CreatePriceAlertSerializer(serializers.Serializer):
    """Serializer for creating price alerts"""
    symbol = serializers.CharField(max_length=20)
    condition = serializers.ChoiceField(choices=['above', 'below'])
    target_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    channels = serializers.ListField(
        child=serializers.CharField(),
        default=['email', 'push']
    )


class CreatePortfolioAlertSerializer(serializers.Serializer):
    """Serializer for creating portfolio alerts"""
    condition = serializers.ChoiceField(choices=['above', 'below'])
    target_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    channels = serializers.ListField(
        child=serializers.CharField(),
        default=['email', 'push']
    )


class AlertTriggerDetailSerializer(serializers.Serializer):
    """Serializer for alert trigger details"""
    alert_rule = AlertRuleSerializer()
    triggers = AlertTriggerSerializer(many=True)


class MarketAlertSerializer(serializers.Serializer):
    """Serializer for market alert notifications"""
    user_id = serializers.IntegerField()
    symbol = serializers.CharField(max_length=20)
    alert_type = serializers.CharField()
    current_value = serializers.DecimalField(max_digits=15, decimal_places=4)
    threshold_value = serializers.DecimalField(max_digits=15, decimal_places=4)


class PortfolioAlertSerializer(serializers.Serializer):
    """Serializer for portfolio alert notifications"""
    user_id = serializers.IntegerField()
    portfolio_name = serializers.CharField(max_length=100)
    alert_type = serializers.CharField()
    current_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    threshold_value = serializers.DecimalField(max_digits=15, decimal_places=2)


class MLPredictionAlertSerializer(serializers.Serializer):
    """Serializer for ML prediction alert notifications"""
    user_id = serializers.IntegerField()
    symbol = serializers.CharField(max_length=20)
    prediction_direction = serializers.CharField()
    confidence_score = serializers.DecimalField(max_digits=5, decimal_places=2)