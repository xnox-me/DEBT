from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta, time
from decimal import Decimal
import json
import requests
import logging
import hashlib
import hmac

from .auto_trading_models import (
    AutoTradingStrategy, AutoTradingSignal, WorkflowExecution,
    TradingWebhook, AutoTradingLog, TradingBotConfiguration
)
from .models import Portfolio, Position, Transaction
from markets.models import Stock
from markets.utils import fetch_market_data, analyze_trading_signals

logger = logging.getLogger('debt_trading')


class AutoTradingStrategyViewSet(viewsets.ModelViewSet):
    """API endpoints for automated trading strategies"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AutoTradingStrategy.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start_strategy(self, request, pk=None):
        """Start an automated trading strategy"""
        strategy = self.get_object()
        
        try:
            # Validate strategy configuration
            if not strategy.symbols:
                return Response(
                    {'error': 'Strategy must have at least one symbol'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not strategy.portfolio:
                return Response(
                    {'error': 'Strategy must be linked to a portfolio'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update strategy status
            strategy.status = 'ACTIVE'
            strategy.save()
            
            # Log strategy start
            AutoTradingLog.objects.create(
                strategy=strategy,
                level='INFO',
                category='STRATEGY_EXECUTION',
                message=f'Strategy {strategy.name} started successfully',
                context_data={'action': 'start_strategy'}
            )

            return Response({
                'message': f'Strategy {strategy.name} started successfully',
                'status': 'ACTIVE'
            })
            
        except Exception as e:
            logger.error(f"Error starting strategy {strategy.id}: {str(e)}")
            return Response(
                {'error': 'Failed to start strategy'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def stop_strategy(self, request, pk=None):
        """Stop an automated trading strategy"""
        strategy = self.get_object()
        
        try:
            strategy.status = 'STOPPED'
            strategy.save()
            
            # Log strategy stop
            AutoTradingLog.objects.create(
                strategy=strategy,
                level='INFO',
                category='STRATEGY_EXECUTION',
                message=f'Strategy {strategy.name} stopped',
                context_data={'action': 'stop_strategy'}
            )
            
            return Response({
                'message': f'Strategy {strategy.name} stopped successfully',
                'status': 'STOPPED'
            })
            
        except Exception as e:
            logger.error(f"Error stopping strategy {strategy.id}: {str(e)}")
            return Response(
                {'error': 'Failed to stop strategy'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def generate_strategy_signals(strategy):
    """Generate trading signals for a strategy"""
    signals_generated = []
    
    try:
        # Simple implementation for demo
        for symbol in strategy.symbols[:5]:  # Limit to 5 symbols
            try:
                stock = Stock.objects.get(symbol=symbol)
                
                # Create a sample signal
                signal = AutoTradingSignal.objects.create(
                    strategy=strategy,
                    stock=stock,
                    signal_type='BUY',
                    confidence='HIGH',
                    confidence_score=Decimal('85.0'),
                    target_price=Decimal('100.0'),
                    quantity=Decimal('10.0'),
                    technical_data={'sample': 'data'}
                )
                
                signals_generated.append({
                    'id': signal.id,
                    'symbol': symbol,
                    'signal_type': 'BUY',
                    'confidence': 'HIGH'
                })
                
            except Stock.DoesNotExist:
                continue
    
    except Exception as e:
        logger.error(f"Error generating signals for strategy {strategy.id}: {str(e)}")
    
    return signals_generated


@csrf_exempt
@require_http_methods(["POST"])
def n8n_webhook_receiver(request):
    """Receive webhooks from N8N workflows"""
    try:
        payload = json.loads(request.body)
        
        return JsonResponse({'status': 'success', 'message': 'Webhook processed'})
        
    except Exception as e:
        logger.error(f"Error processing N8N webhook: {str(e)}")
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auto_trading_overview(request):
    """Get overview of automated trading activities"""
    try:
        user_strategies = AutoTradingStrategy.objects.filter(user=request.user)
        
        overview_data = {
            'total_strategies': user_strategies.count(),
            'active_strategies': user_strategies.filter(status='ACTIVE').count(),
            'strategies': [
                {
                    'id': strategy.id,
                    'name': strategy.name,
                    'status': strategy.status,
                    'strategy_type': strategy.strategy_type,
                }
                for strategy in user_strategies[:10]
            ]
        }
        
        return Response(overview_data)
        
    except Exception as e:
        logger.error(f"Error getting auto trading overview: {str(e)}")
        return Response(
            {'error': 'Failed to get overview'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trading_signals(request):
    """Get recent trading signals"""
    try:
        signals = AutoTradingSignal.objects.filter(
            strategy__user=request.user
        )[:20]
        
        signals_data = [
            {
                'id': signal.id,
                'strategy_name': signal.strategy.name,
                'symbol': signal.stock.symbol,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'status': signal.status,
                'created_at': signal.created_at.isoformat(),
            }
            for signal in signals
        ]
        
        return Response({
            'signals': signals_data,
            'total_signals': len(signals_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting trading signals: {str(e)}")
        return Response(
            {'error': 'Failed to get signals'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_n8n_workflow(request):
    """Helper endpoint to create N8N workflow configuration"""
    try:
        strategy_id = request.data.get('strategy_id')
        
        if not strategy_id:
            return Response(
                {'error': 'Strategy ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        workflow_template = {
            "name": f"DEBT Trading Strategy {strategy_id}",
            "active": True,
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "httpMethod": "POST",
                        "path": f"debt-trading-{strategy_id}"
                    }
                }
            ]
        }
        
        return Response({
            'message': 'N8N workflow template generated',
            'workflow_template': workflow_template
        })
        
    except Exception as e:
        logger.error(f"Error creating N8N workflow: {str(e)}")
        return Response(
            {'error': 'Failed to create workflow template'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )