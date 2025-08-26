from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging

from .models import UserProfile, SubscriptionPlan, UserSubscription, Payment, APIKey
from portfolio.models import Portfolio

logger = logging.getLogger('debt_trading')


def register_view(request):
    """User registration page"""
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validation
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return render(request, 'accounts/register.html')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'accounts/register.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'accounts/register.html')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create default portfolio
            Portfolio.objects.create(
                user=user,
                name=f"{user.username}'s Portfolio",
                description="Default portfolio for new users"
            )
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            messages.error(request, 'An error occurred during registration')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """User login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', '/')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('markets:home')


@login_required
def profile_view(request):
    """User profile page"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        try:
            # Update profile
            profile.phone_number = request.POST.get('phone_number', profile.phone_number)
            profile.country = request.POST.get('country', profile.country)
            profile.city = request.POST.get('city', profile.city)
            profile.risk_tolerance = request.POST.get('risk_tolerance', profile.risk_tolerance)
            profile.investment_experience = request.POST.get('investment_experience', profile.investment_experience)
            profile.investment_goals = request.POST.get('investment_goals', profile.investment_goals)
            profile.preferred_currency = request.POST.get('preferred_currency', profile.preferred_currency)
            profile.timezone = request.POST.get('timezone', profile.timezone)
            
            # Update notification preferences
            profile.email_notifications = request.POST.get('email_notifications') == 'on'
            profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
            profile.push_notifications = request.POST.get('push_notifications') == 'on'
            profile.trading_alerts = request.POST.get('trading_alerts') == 'on'
            profile.market_news = request.POST.get('market_news') == 'on'
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            messages.error(request, 'Error updating profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def subscription_view(request):
    """User subscription management page"""
    try:
        # Get user's current subscription
        current_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).first()
        
        # Get available plans
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
        
        context = {
            'current_subscription': current_subscription,
            'plans': plans,
        }
        return render(request, 'accounts/subscription.html', context)
        
    except Exception as e:
        logger.error(f"Error loading subscription page: {str(e)}")
        messages.error(request, 'Error loading subscription information')
        return render(request, 'accounts/subscription.html')


# API Views
class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoints for user profiles"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """API endpoint for user registration"""
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([username, email, password]):
            return Response(
                {'error': 'Username, email, and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create profile
        profile = UserProfile.objects.create(user=user)
        
        # Create default portfolio
        Portfolio.objects.create(
            user=user,
            name=f"{user.username}'s Portfolio",
            description="Default portfolio for new users"
        )
        
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in register_api: {str(e)}")
        return Response(
            {'error': 'Registration failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """API endpoint for user login"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([username, password]):
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Error in login_api: {str(e)}")
        return Response(
            {'error': 'Login failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_plans(request):
    """Get available subscription plans"""
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
        
        plans_data = [
            {
                'id': plan.id,
                'name': plan.name,
                'plan_type': plan.plan_type,
                'description': plan.description,
                'price': float(plan.price),
                'currency': plan.currency,
                'billing_cycle': plan.billing_cycle,
                'max_portfolios': plan.max_portfolios,
                'max_positions_per_portfolio': plan.max_positions_per_portfolio,
                'max_auto_strategies': plan.max_auto_strategies,
                'api_calls_per_day': plan.api_calls_per_day,
                'real_time_data': plan.real_time_data,
                'advanced_analytics': plan.advanced_analytics,
                'ml_predictions': plan.ml_predictions,
                'auto_trading': plan.auto_trading,
                'portfolio_optimization': plan.portfolio_optimization,
                'risk_analysis': plan.risk_analysis,
                'custom_alerts': plan.custom_alerts,
                'email_support': plan.email_support,
                'priority_support': plan.priority_support,
                'phone_support': plan.phone_support,
                'is_popular': plan.is_popular,
            }
            for plan in plans
        ]
        
        return Response({'plans': plans_data})
        
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        return Response(
            {'error': 'Failed to get subscription plans'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_to_plan(request, plan_id):
    """Subscribe to a subscription plan"""
    try:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        
        # Check if user already has an active subscription
        existing_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).first()
        
        if existing_subscription:
            return Response(
                {'error': 'You already have an active subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create subscription
        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            status='ACTIVE',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),  # 30 days for demo
            auto_renew=True,
            amount_paid=plan.price,
            currency=plan.currency,
            next_billing_date=datetime.now() + timedelta(days=30)
        )
        
        return Response({
            'message': 'Subscription created successfully',
            'subscription_id': subscription.id,
            'plan_name': plan.name,
            'end_date': subscription.end_date.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error subscribing to plan: {str(e)}")
        return Response(
            {'error': 'Failed to create subscription'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscription(request):
    """Get user's current subscription"""
    try:
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).first()
        
        if not subscription:
            return Response({'subscription': None})
        
        subscription_data = {
            'id': subscription.id,
            'plan_name': subscription.plan.name,
            'plan_type': subscription.plan.plan_type,
            'status': subscription.status,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'days_remaining': subscription.days_remaining,
            'auto_renew': subscription.auto_renew,
            'amount_paid': float(subscription.amount_paid),
            'currency': subscription.currency,
        }
        
        return Response({'subscription': subscription_data})
        
    except Exception as e:
        logger.error(f"Error getting user subscription: {str(e)}")
        return Response(
            {'error': 'Failed to get subscription information'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_api_key(request):
    """Generate a new API key for the user"""
    try:
        name = request.data.get('name', 'Default API Key')
        key_type = request.data.get('key_type', 'READ_ONLY')
        
        # Create API key
        api_key = APIKey.objects.create(
            user=request.user,
            name=name,
            key_type=key_type
        )
        
        return Response({
            'message': 'API key generated successfully',
            'key': api_key.key,
            'secret': api_key.secret,
            'key_id': api_key.id
        })
        
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        return Response(
            {'error': 'Failed to generate API key'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_api_keys(request):
    """List user's API keys"""
    try:
        api_keys = APIKey.objects.filter(user=request.user)
        
        keys_data = [
            {
                'id': key.id,
                'name': key.name,
                'key_type': key.key_type,
                'is_active': key.is_active,
                'created_at': key.created_at.isoformat(),
                'last_used': key.last_used.isoformat() if key.last_used else None,
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
            }
            for key in api_keys
        ]
        
        return Response({'api_keys': keys_data})
        
    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        return Response(
            {'error': 'Failed to list API keys'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_api_key(request, key_id):
    """Revoke an API key"""
    try:
        api_key = get_object_or_404(APIKey, id=key_id, user=request.user)
        api_key.delete()
        
        return Response({'message': 'API key revoked successfully'})
        
    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        return Response(
            {'error': 'Failed to revoke API key'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )