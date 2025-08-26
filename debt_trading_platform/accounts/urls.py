from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    # Authentication Views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('subscription/', views.subscription_view, name='subscription'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    path('api/register/', views.register_api, name='api-register'),
    path('api/login/', views.login_api, name='api-login'),
    path('api/subscription/plans/', views.get_subscription_plans, name='api-subscription-plans'),
    path('api/subscription/current/', views.get_user_subscription, name='api-current-subscription'),
    path('api/subscription/subscribe/<int:plan_id>/', views.subscribe_to_plan, name='api-subscribe'),
    path('api/api-keys/generate/', views.generate_api_key, name='api-generate-key'),
    path('api/api-keys/list/', views.list_api_keys, name='api-list-keys'),
    path('api/api-keys/revoke/<int:key_id>/', views.revoke_api_key, name='api-revoke-key'),
]