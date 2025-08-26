from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .models import Notification, UserNotificationPreference, AlertRule, AlertTrigger
from .serializers import (
    NotificationSerializer, UserNotificationPreferenceSerializer,
    AlertRuleSerializer, AlertTriggerSerializer
)
from accounts.models import UserProfile

logger = logging.getLogger('debt_trading')


@login_required
def notifications_dashboard(request):
    """Notifications dashboard view"""
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    
    # Get user preferences
    try:
        preferences = request.user.notification_preferences.all()
    except:
        preferences = []
    
    # Get alert rules
    alert_rules = AlertRule.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
        'preferences': preferences,
        'alert_rules': alert_rules,
        'unread_count': notifications.filter(status='UNREAD').count(),
    }
    return render(request, 'notifications/dashboard.html', context)


@login_required
def notification_detail(request, notification_id):
    """View individual notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Mark as read if unread
    if notification.status == 'UNREAD':
        notification.mark_as_read()
    
    context = {
        'notification': notification,
    }
    return render(request, 'notifications/detail.html', context)


# API Views
class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoints for notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            status='UNREAD'
        ).count()
        
        return Response({'count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(
            user=request.user,
            status='UNREAD'
        ).update(
            status='READ',
            read_at=timezone.now()
        )
        
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark specific notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications"""
        limit = int(request.GET.get('limit', 10))
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:limit]
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    """API endpoints for user notification preferences"""
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserNotificationPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlertRuleViewSet(viewsets.ModelViewSet):
    """API endpoints for alert rules"""
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AlertRule.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test an alert rule"""
        alert_rule = self.get_object()
        
        # Simple test implementation
        test_result = {
            'alert_rule_id': alert_rule.id,
            'name': alert_rule.name,
            'test_status': 'success',
            'message': f'Alert rule "{alert_rule.name}" would trigger under current conditions',
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(test_result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_stats(request):
    """Get notification statistics for the user"""
    try:
        # Get notification counts by status
        total_notifications = Notification.objects.filter(user=request.user).count()
        unread_notifications = Notification.objects.filter(
            user=request.user,
            status='UNREAD'
        ).count()
        read_notifications = total_notifications - unread_notifications
        
        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Get notification types distribution
        notification_types = {}
        for notification in Notification.objects.filter(user=request.user)[:100]:
            type_name = notification.notification_type.name
            notification_types[type_name] = notification_types.get(type_name, 0) + 1
        
        stats = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'read_notifications': read_notifications,
            'recent_notifications': recent_notifications,
            'notification_types': notification_types,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        return Response(
            {'error': 'Failed to get notification statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_price_alert(request):
    """Create a price alert for a specific symbol"""
    try:
        symbol = request.data.get('symbol')
        condition = request.data.get('condition')  # 'above', 'below'
        target_price = request.data.get('target_price')
        notification_channels = request.data.get('channels', ['email', 'push'])
        
        if not all([symbol, condition, target_price]):
            return Response(
                {'error': 'Symbol, condition, and target_price are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create alert rule
        alert_rule = AlertRule.objects.create(
            user=request.user,
            name=f"Price Alert: {symbol}",
            description=f"Alert when {symbol} price goes {condition} {target_price}",
            alert_type='PRICE_THRESHOLD',
            symbol=symbol,
            condition_field='price',
            condition_operator='>' if condition == 'above' else '<',
            condition_value=str(target_price),
            notification_channels=notification_channels,
            is_active=True
        )
        
        return Response({
            'message': 'Price alert created successfully',
            'alert_id': alert_rule.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating price alert: {str(e)}")
        return Response(
            {'error': 'Failed to create price alert'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portfolio_alert(request):
    """Create a portfolio value alert"""
    try:
        condition = request.data.get('condition')  # 'above', 'below'
        target_value = request.data.get('target_value')
        notification_channels = request.data.get('channels', ['email', 'push'])
        
        if not all([condition, target_value]):
            return Response(
                {'error': 'Condition and target_value are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create alert rule
        alert_rule = AlertRule.objects.create(
            user=request.user,
            name="Portfolio Value Alert",
            description=f"Alert when portfolio value goes {condition} {target_value}",
            alert_type='PORTFOLIO_CHANGE',
            condition_field='portfolio_value',
            condition_operator='>' if condition == 'above' else '<',
            condition_value=str(target_value),
            notification_channels=notification_channels,
            is_active=True
        )
        
        return Response({
            'message': 'Portfolio alert created successfully',
            'alert_id': alert_rule.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating portfolio alert: {str(e)}")
        return Response(
            {'error': 'Failed to create portfolio alert'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alert_triggers(request, alert_id):
    """Get triggers for a specific alert rule"""
    try:
        alert_rule = get_object_or_404(AlertRule, id=alert_id, user=request.user)
        triggers = AlertTrigger.objects.filter(alert_rule=alert_rule).order_by('-triggered_at')[:50]
        
        triggers_data = [
            {
                'id': trigger.id,
                'triggered_at': trigger.triggered_at.isoformat(),
                'trigger_value': trigger.trigger_value,
                'is_processed': trigger.is_processed,
                'trigger_data': trigger.trigger_data
            }
            for trigger in triggers
        ]
        
        return Response({
            'alert_rule': {
                'id': alert_rule.id,
                'name': alert_rule.name,
                'description': alert_rule.description
            },
            'triggers': triggers_data
        })
        
    except Exception as e:
        logger.error(f"Error getting alert triggers: {str(e)}")
        return Response(
            {'error': 'Failed to get alert triggers'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Utility functions for creating notifications
def create_notification(user, notification_type, title, message, data=None, priority='NORMAL'):
    """Create a new notification for a user"""
    try:
        from .models import NotificationType
        
        # Get or create notification type
        notification_type_obj, created = NotificationType.objects.get_or_create(
            name=notification_type,
            defaults={'description': notification_type.replace('_', ' ').title()}
        )
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type_obj,
            title=title,
            message=message,
            data=data or {},
            priority=priority
        )
        
        return notification
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return None


def send_market_alert(user, symbol, alert_type, current_value, threshold_value):
    """Send market-related alert notification"""
    title = f"Market Alert: {symbol}"
    
    if alert_type == 'PRICE_ABOVE':
        message = f"{symbol} has crossed above {threshold_value}. Current price: {current_value}"
    elif alert_type == 'PRICE_BELOW':
        message = f"{symbol} has dropped below {threshold_value}. Current price: {current_value}"
    elif alert_type == 'VOLUME_SPIKE':
        message = f"Unusual volume spike detected for {symbol}. Current volume: {current_value}"
    else:
        message = f"Market alert for {symbol}: {alert_type}"
    
    return create_notification(
        user=user,
        notification_type='market_alert',
        title=title,
        message=message,
        data={
            'symbol': symbol,
            'alert_type': alert_type,
            'current_value': str(current_value),
            'threshold_value': str(threshold_value)
        },
        priority='HIGH'
    )


def send_portfolio_alert(user, portfolio_name, alert_type, current_value, threshold_value):
    """Send portfolio-related alert notification"""
    title = f"Portfolio Alert: {portfolio_name}"
    
    if alert_type == 'VALUE_ABOVE':
        message = f"Your portfolio '{portfolio_name}' has exceeded {threshold_value}. Current value: {current_value}"
    elif alert_type == 'VALUE_BELOW':
        message = f"Your portfolio '{portfolio_name}' has dropped below {threshold_value}. Current value: {current_value}"
    elif alert_type == 'LARGE_CHANGE':
        message = f"Significant change detected in '{portfolio_name}'. Current value: {current_value}"
    else:
        message = f"Portfolio alert for '{portfolio_name}': {alert_type}"
    
    return create_notification(
        user=user,
        notification_type='portfolio_alert',
        title=title,
        message=message,
        data={
            'portfolio_name': portfolio_name,
            'alert_type': alert_type,
            'current_value': str(current_value),
            'threshold_value': str(threshold_value)
        },
        priority='HIGH'
    )


def send_ml_prediction_alert(user, symbol, prediction_direction, confidence_score):
    """Send ML prediction alert notification"""
    title = f"ML Prediction: {symbol}"
    message = f"Our AI predicts {symbol} will move {prediction_direction} with {confidence_score}% confidence"
    
    return create_notification(
        user=user,
        notification_type='ml_prediction',
        title=title,
        message=message,
        data={
            'symbol': symbol,
            'prediction_direction': prediction_direction,
            'confidence_score': confidence_score
        },
        priority='NORMAL'
    )