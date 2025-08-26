from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'models', views.MLModelViewSet)
router.register(r'predictions', views.PredictionViewSet)
router.register(r'strategies', views.TradingStrategyViewSet)

app_name = 'ml_predictions'

urlpatterns = [
    # Dashboard Views
    path('', views.ml_dashboard, name='dashboard'),
    path('predictions/', views.predictions_overview, name='predictions'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    
    # ML Prediction APIs
    path('api/predict/<str:symbol>/', views.get_ml_prediction, name='ml_prediction'),
    path('api/signals/', views.get_trading_signals, name='trading_signals'),
    path('api/train/', views.train_model_api, name='train_model'),
    path('api/performance/', views.get_model_performance, name='model_performance'),
    path('api/analysis/', views.get_market_analysis, name='market_analysis'),
]