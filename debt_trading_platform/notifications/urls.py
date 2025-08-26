from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'preferences', views.UserNotificationPreferenceViewSet, basename='preference')
router.register(r'alerts', views.AlertRuleViewSet, basename='alert')

urlpatterns = [
    # Dashboard Views
    path('', views.notifications_dashboard, name='dashboard'),
    path('<uuid:notification_id>/', views.notification_detail, name='detail'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Custom API Endpoints
    path('api/stats/', views.get_notification_stats, name='notification-stats'),
    path('api/alerts/price/', views.create_price_alert, name='create-price-alert'),
    path('api/alerts/portfolio/', views.create_portfolio_alert, name='create-portfolio-alert'),
    path('api/alerts/<int:alert_id>/triggers/', views.get_alert_triggers, name='alert-triggers'),
]