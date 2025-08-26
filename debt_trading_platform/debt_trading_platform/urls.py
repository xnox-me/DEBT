"""
URL configuration for debt_trading_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import render

def dashboard_home(request):
    """Main trading dashboard homepage"""
    return render(request, 'dashboard/home.html')

def api_health(request):
    """API health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'platform': 'DEBT Trading Platform',
        'features': {
            'tasi_markets': True,
            'global_markets': True,
            'ml_predictions': True,
            'portfolio_management': True,
            'real_time_notifications': True
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main Dashboard
    path('', dashboard_home, name='dashboard_home'),
    
    # API Health Check
    path('api/health/', api_health, name='api_health'),
    
    # App URLs
    path('api/markets/', include('markets.urls')),
    path('api/ml/', include('ml_predictions.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/gateway/', include('api_gateway.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('accounts/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
