from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'markets', views.MarketViewSet)
router.register(r'stocks', views.StockViewSet)
router.register(r'market-data', views.MarketDataViewSet)
router.register(r'watchlists', views.WatchlistViewSet, basename='watchlist')
router.register(r'alerts', views.AlertViewSet, basename='alert')
router.register(r'signals', views.TradingSignalViewSet)

app_name = 'markets'

urlpatterns = [
    # Dashboard Views
    path('', views.markets_dashboard, name='dashboard'),
    path('tasi/', views.tasi_dashboard, name='tasi_dashboard'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Real-time Data APIs
    path('api/quote/<str:symbol>/', views.get_stock_quote, name='stock_quote'),
    path('api/chart/<str:symbol>/', views.get_market_chart, name='market_chart'),
    path('api/tasi/overview/', views.get_tasi_overview, name='tasi_overview'),
    path('api/global/overview/', views.get_global_overview, name='global_overview'),
]