from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd
from decimal import Decimal
import logging

from .models import (
    Portfolio, Position, Transaction, RiskMetrics, PortfolioPerformance,
    PortfolioOptimization, PortfolioBenchmark, RebalancingRule
)
from .serializers import (
    PortfolioSerializer, PositionSerializer, TransactionSerializer,
    RiskMetricsSerializer, PortfolioPerformanceSerializer
)
from markets.models import Stock, MarketData
from markets.utils import fetch_market_data

logger = logging.getLogger('debt_trading')

# Dashboard Views
def portfolio_dashboard(request):
    """Portfolio management dashboard"""
    if not request.user.is_authenticated:
        return render(request, 'registration/login.html')
    
    user_portfolios = Portfolio.objects.filter(user=request.user, is_active=True)
    
    context = {
        'portfolios': user_portfolios,
        'total_portfolios': user_portfolios.count(),
    }
    return render(request, 'portfolio/dashboard.html', context)

def portfolio_detail(request, portfolio_id):
    """Detailed portfolio view"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    context = {
        'portfolio': portfolio,
        'positions': portfolio.positions.filter(status='OPEN'),
        'recent_transactions': portfolio.transactions.all()[:10],
        'performance_data': portfolio.performance_history.all()[:30],
    }
    return render(request, 'portfolio/detail.html', context)

# API ViewSets
class PortfolioViewSet(viewsets.ModelViewSet):
    """API endpoints for portfolios"""
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get portfolio performance data"""
        portfolio = self.get_object()
        days = int(request.GET.get('days', 30))
        
        performance_data = portfolio.performance_history.all()[:days]
        
        data = {
            'portfolio_id': portfolio.id,
            'performance': [
                {
                    'date': p.date.isoformat(),
                    'value': float(p.portfolio_value),
                    'daily_return': float(p.daily_return or 0),
                    'total_return': float(p.total_return_percentage),
                }
                for p in performance_data
            ]
        }
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def positions(self, request, pk=None):
        """Get portfolio positions"""
        portfolio = self.get_object()
        positions = portfolio.positions.filter(status='OPEN')
        
        position_data = []
        for position in positions:
            # Get current market price
            current_price = get_current_price(position.stock.symbol)
            
            if current_price:
                current_value = float(position.quantity) * float(current_price)
                unrealized_pnl = current_value - float(position.total_cost)
                unrealized_pnl_pct = (unrealized_pnl / float(position.total_cost)) * 100
                
                position_data.append({
                    'id': position.id,
                    'symbol': position.stock.symbol,
                    'name': position.stock.name,
                    'quantity': float(position.quantity),
                    'entry_price': float(position.entry_price),
                    'current_price': float(current_price),
                    'current_value': current_value,
                    'total_cost': float(position.total_cost),
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': unrealized_pnl_pct,
                    'portfolio_weight': (current_value / float(portfolio.current_value)) * 100,
                })
        
        return Response({'positions': position_data})
    
    @action(detail=True, methods=['post'])
    def add_position(self, request, pk=None):
        """Add a new position to portfolio"""
        portfolio = self.get_object()
        
        try:
            symbol = request.data.get('symbol')
            quantity = Decimal(str(request.data.get('quantity')))
            price = Decimal(str(request.data.get('price')))
            
            if not all([symbol, quantity, price]):
                return Response(
                    {'error': 'Symbol, quantity, and price are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get stock
            stock = Stock.objects.get(symbol=symbol)
            
            # Calculate costs
            total_cost = quantity * price
            commission = total_cost * Decimal('0.001')  # 0.1% commission
            total_with_fees = total_cost + commission
            
            # Check if enough cash
            if portfolio.cash_balance < total_with_fees:
                return Response(
                    {'error': 'Insufficient cash balance'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create position
            position = Position.objects.create(
                portfolio=portfolio,
                stock=stock,
                quantity=quantity,
                entry_price=price,
                total_cost=total_with_fees,
                current_price=price
            )
            
            # Create transaction
            Transaction.objects.create(
                portfolio=portfolio,
                position=position,
                stock=stock,
                transaction_type='BUY',
                quantity=quantity,
                price=price,
                amount=total_cost,
                commission=commission,
                total_cost=total_with_fees,
                cash_impact=-total_with_fees
            )
            
            # Update portfolio
            portfolio.cash_balance -= total_with_fees
            portfolio.save()
            
            return Response({
                'message': 'Position added successfully',
                'position_id': position.id
            })
            
        except Stock.DoesNotExist:
            return Response(
                {'error': f'Stock {symbol} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error adding position: {str(e)}")
            return Response(
                {'error': 'Failed to add position'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PositionViewSet(viewsets.ModelViewSet):
    """API endpoints for positions"""
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Position.objects.filter(portfolio__user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    """API endpoints for transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(portfolio__user=self.request.user)

# Risk Analysis Functions
def calculate_portfolio_risk(portfolio):
    """Calculate comprehensive risk metrics for a portfolio"""
    try:
        positions = portfolio.positions.filter(status='OPEN')
        
        if not positions.exists():
            return None
        
        # Get historical data for all positions
        symbols = [pos.stock.symbol for pos in positions]
        weights = []
        returns_data = []
        
        total_value = float(portfolio.current_value)
        
        for position in positions:
            # Calculate position weight
            current_price = get_current_price(position.stock.symbol)
            if current_price:
                position_value = float(position.quantity) * float(current_price)
                weight = position_value / total_value
                weights.append(weight)
                
                # Get historical returns
                hist_data = fetch_market_data(position.stock.symbol, period='1y', interval='1d')
                if hist_data is not None and not hist_data.empty:
                    returns = hist_data['Close'].pct_change().dropna()
                    returns_data.append(returns.values)
        
        if not returns_data:
            return None
        
        # Convert to numpy arrays
        weights = np.array(weights)
        returns_matrix = np.array(returns_data).T  # Transpose to get time x assets
        
        # Calculate portfolio returns
        portfolio_returns = np.dot(returns_matrix, weights)
        
        # Risk metrics
        portfolio_volatility = np.std(portfolio_returns) * np.sqrt(252)  # Annualized
        var_95 = np.percentile(portfolio_returns, 5) * np.sqrt(252)
        var_99 = np.percentile(portfolio_returns, 1) * np.sqrt(252)
        
        # Expected shortfall (CVaR)
        var_95_threshold = np.percentile(portfolio_returns, 5)
        expected_shortfall = np.mean(portfolio_returns[portfolio_returns <= var_95_threshold])
        
        # Correlation matrix
        correlation_matrix = np.corrcoef(returns_matrix.T)
        
        # Concentration risk (Herfindahl index)
        concentration_risk = np.sum(weights ** 2)
        
        # Diversification ratio
        individual_volatilities = np.array([np.std(ret) for ret in returns_data])
        weighted_avg_volatility = np.dot(weights, individual_volatilities)
        diversification_ratio = weighted_avg_volatility / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            'portfolio_volatility': float(portfolio_volatility),
            'var_95': float(var_95 * total_value),
            'var_99': float(var_99 * total_value),
            'expected_shortfall': float(expected_shortfall * total_value),
            'concentration_risk': float(concentration_risk),
            'diversification_ratio': float(diversification_ratio),
            'largest_position_weight': float(max(weights)) * 100,
            'correlation_matrix': correlation_matrix.tolist(),
        }
        
    except Exception as e:
        logger.error(f"Error calculating portfolio risk: {str(e)}")
        return None

def optimize_portfolio(portfolio, method='MEAN_VARIANCE', target_return=None):
    """Optimize portfolio allocation using various methods"""
    try:
        positions = portfolio.positions.filter(status='OPEN')
        
        if positions.count() < 2:
            return None
        
        # Get historical data
        symbols = [pos.stock.symbol for pos in positions]
        returns_data = []
        
        for symbol in symbols:
            hist_data = fetch_market_data(symbol, period='1y', interval='1d')
            if hist_data is not None and not hist_data.empty:
                returns = hist_data['Close'].pct_change().dropna()
                returns_data.append(returns.values)
        
        if len(returns_data) < 2:
            return None
        
        returns_matrix = np.array(returns_data).T
        mean_returns = np.mean(returns_matrix, axis=0)
        cov_matrix = np.cov(returns_matrix.T)
        
        n_assets = len(symbols)
        
        if method == 'MINIMUM_VARIANCE':
            # Minimum variance optimization
            inv_cov = np.linalg.inv(cov_matrix)
            ones = np.ones((n_assets, 1))
            weights = np.dot(inv_cov, ones) / np.dot(ones.T, np.dot(inv_cov, ones))
            weights = weights.flatten()
            
        elif method == 'RISK_PARITY':
            # Equal risk contribution
            weights = np.ones(n_assets) / n_assets
            # Iterative optimization would go here (simplified for demo)
            
        elif method == 'MAXIMUM_SHARPE':
            # Maximum Sharpe ratio (simplified)
            risk_free_rate = 0.02  # 2% risk-free rate
            excess_returns = mean_returns - risk_free_rate
            
            try:
                inv_cov = np.linalg.inv(cov_matrix)
                weights = np.dot(inv_cov, excess_returns)
                weights = weights / np.sum(weights)
            except np.linalg.LinAlgError:
                # Fallback to equal weights
                weights = np.ones(n_assets) / n_assets
                
        else:  # MEAN_VARIANCE
            # Equal weight for simplicity (full optimization would require scipy.optimize)
            weights = np.ones(n_assets) / n_assets
        
        # Calculate expected performance
        expected_return = np.dot(weights, mean_returns) * 252  # Annualized
        expected_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        expected_sharpe = expected_return / expected_risk if expected_risk > 0 else 0
        
        # Create allocation dictionary
        allocations = {}
        for i, symbol in enumerate(symbols):
            allocations[symbol] = float(weights[i] * 100)  # Convert to percentage
        
        return {
            'method': method,
            'allocations': allocations,
            'expected_return': float(expected_return),
            'expected_risk': float(expected_risk),
            'expected_sharpe': float(expected_sharpe),
        }
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {str(e)}")
        return None

def get_current_price(symbol):
    """Get current price for a symbol"""
    try:
        # Try to get from recent market data first
        stock = Stock.objects.get(symbol=symbol)
        latest_data = stock.market_data.first()
        
        if latest_data and (datetime.now() - latest_data.created_at.replace(tzinfo=None)).seconds < 3600:
            return latest_data.close_price
        
        # Fetch fresh data
        data = fetch_market_data(symbol, period='1d', interval='1d')
        if data is not None and not data.empty:
            return Decimal(str(data['Close'].iloc[-1]))
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting current price for {symbol}: {str(e)}")
        return None

# API Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio_overview(request):
    """Get overview of all user portfolios"""
    try:
        portfolios = Portfolio.objects.filter(user=request.user, is_active=True)
        
        overview_data = []
        total_value = 0
        
        for portfolio in portfolios:
            # Update portfolio value
            current_value = update_portfolio_value(portfolio)
            total_value += float(current_value)
            
            overview_data.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'portfolio_type': portfolio.portfolio_type,
                'current_value': float(current_value),
                'cash_balance': float(portfolio.cash_balance),
                'total_return': float(portfolio.total_return_percentage),
                'positions_count': portfolio.positions.filter(status='OPEN').count(),
                'updated_at': portfolio.updated_at.isoformat(),
            })
        
        return Response({
            'portfolios': overview_data,
            'total_portfolios': len(overview_data),
            'total_value': total_value,
            'timestamp': datetime.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio overview: {str(e)}")
        return Response(
            {'error': 'Failed to get portfolio overview'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio_risk(request, portfolio_id):
    """Get risk analysis for a specific portfolio"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        risk_data = calculate_portfolio_risk(portfolio)
        
        if risk_data is None:
            return Response(
                {'error': 'Unable to calculate risk metrics'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine risk rating
        volatility = risk_data['portfolio_volatility']
        if volatility < 0.1:
            risk_rating = 'LOW'
        elif volatility < 0.2:
            risk_rating = 'MEDIUM'
        elif volatility < 0.3:
            risk_rating = 'HIGH'
        else:
            risk_rating = 'VERY_HIGH'
        
        risk_data['risk_rating'] = risk_rating
        risk_data['portfolio_id'] = portfolio.id
        risk_data['portfolio_name'] = portfolio.name
        
        return Response(risk_data)
        
    except Exception as e:
        logger.error(f"Error getting portfolio risk: {str(e)}")
        return Response(
            {'error': 'Failed to calculate portfolio risk'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_portfolio_api(request, portfolio_id):
    """Optimize portfolio allocation"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        method = request.data.get('method', 'MEAN_VARIANCE')
        target_return = request.data.get('target_return')
        
        optimization_result = optimize_portfolio(portfolio, method, target_return)
        
        if optimization_result is None:
            return Response(
                {'error': 'Unable to optimize portfolio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save optimization result
        PortfolioOptimization.objects.create(
            portfolio=portfolio,
            optimization_method=method,
            target_return=target_return,
            recommended_allocations=optimization_result['allocations'],
            expected_return=Decimal(str(optimization_result['expected_return'])),
            expected_risk=Decimal(str(optimization_result['expected_risk'])),
            expected_sharpe=Decimal(str(optimization_result['expected_sharpe']))
        )
        
        return Response(optimization_result)
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {str(e)}")
        return Response(
            {'error': 'Failed to optimize portfolio'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def update_portfolio_value(portfolio):
    """Update portfolio current value based on current prices"""
    try:
        positions = portfolio.positions.filter(status='OPEN')
        total_positions_value = 0
        
        for position in positions:
            current_price = get_current_price(position.stock.symbol)
            if current_price:
                position_value = float(position.quantity) * float(current_price)
                total_positions_value += position_value
                
                # Update position
                position.current_price = current_price
                position.current_value = Decimal(str(position_value))
                position.unrealized_pnl = Decimal(str(position_value)) - position.total_cost
                position.save()
        
        # Update portfolio
        portfolio.current_value = portfolio.cash_balance + Decimal(str(total_positions_value))
        portfolio.total_return = portfolio.current_value - portfolio.initial_value
        portfolio.total_return_percentage = (portfolio.total_return / portfolio.initial_value) * 100
        portfolio.save()
        
        return portfolio.current_value
        
    except Exception as e:
        logger.error(f"Error updating portfolio value: {str(e)}")
        return portfolio.current_value

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio_allocation(request, portfolio_id):
    """Get portfolio allocation breakdown"""
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        positions = portfolio.positions.filter(status='OPEN')
        
        allocation_data = {
            'sectors': {},
            'markets': {},
            'positions': [],
            'cash_percentage': 0,
        }
        
        total_value = float(portfolio.current_value)
        
        for position in positions:
            current_price = get_current_price(position.stock.symbol)
            if current_price:
                position_value = float(position.quantity) * float(current_price)
                percentage = (position_value / total_value) * 100
                
                # Position allocation
                allocation_data['positions'].append({
                    'symbol': position.stock.symbol,
                    'name': position.stock.name,
                    'value': position_value,
                    'percentage': percentage,
                    'sector': position.stock.sector,
                    'market': position.stock.market.code,
                })
                
                # Sector allocation
                sector = position.stock.sector or 'Unknown'
                if sector in allocation_data['sectors']:
                    allocation_data['sectors'][sector] += percentage
                else:
                    allocation_data['sectors'][sector] = percentage
                
                # Market allocation
                market = position.stock.market.code
                if market in allocation_data['markets']:
                    allocation_data['markets'][market] += percentage
                else:
                    allocation_data['markets'][market] = percentage
        
        # Cash allocation
        allocation_data['cash_percentage'] = (float(portfolio.cash_balance) / total_value) * 100
        
        return Response(allocation_data)
        
    except Exception as e:
        logger.error(f"Error getting portfolio allocation: {str(e)}")
        return Response(
            {'error': 'Failed to get portfolio allocation'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )