from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auto_trading_views

app_name = 'portfolio'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'portfolios', views.PortfolioViewSet, basename='portfolio')
router.register(r'positions', views.PositionViewSet, basename='position')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'auto-strategies', auto_trading_views.AutoTradingStrategyViewSet, basename='auto-strategy')

urlpatterns = [
    # Dashboard Views
    path('', views.portfolio_dashboard, name='dashboard'),
    path('<int:portfolio_id>/', views.portfolio_detail, name='detail'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Portfolio Management API
    path('api/overview/', views.get_portfolio_overview, name='portfolio-overview'),
    path('api/<int:portfolio_id>/risk/', views.get_portfolio_risk, name='portfolio-risk'),
    path('api/<int:portfolio_id>/optimize/', views.optimize_portfolio_api, name='portfolio-optimize'),
    path('api/<int:portfolio_id>/allocation/', views.get_portfolio_allocation, name='portfolio-allocation'),
    
    # Auto-Trading API
    path('api/auto-trading/overview/', auto_trading_views.get_auto_trading_overview, name='auto-trading-overview'),
    path('api/auto-trading/signals/', auto_trading_views.get_trading_signals, name='trading-signals'),
    path('api/auto-trading/n8n-workflow/', auto_trading_views.create_n8n_workflow, name='create-n8n-workflow'),
    
    # N8N Webhooks
    path('webhooks/n8n/', auto_trading_views.n8n_webhook_receiver, name='n8n-webhook'),
    
    # Quick actions
    path('api/<int:portfolio_id>/quick-trade/', views.PortfolioViewSet.as_view({'post': 'add_position'}), name='quick-trade'),
    path('api/<int:portfolio_id>/performance/', views.PortfolioViewSet.as_view({'get': 'performance'}), name='portfolio-performance'),
    path('api/<int:portfolio_id>/positions/', views.PortfolioViewSet.as_view({'get': 'positions'}), name='portfolio-positions'),
]