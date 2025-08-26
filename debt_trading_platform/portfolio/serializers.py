from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Portfolio, Position, Transaction, RiskMetrics, PortfolioPerformance,
    PortfolioOptimization, PortfolioBenchmark, RebalancingRule
)
from markets.models import Stock


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model"""
    user = serializers.StringRelatedField(read_only=True)
    positions_count = serializers.SerializerMethodField()
    return_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'description', 'portfolio_type', 'user',
            'initial_value', 'current_value', 'cash_balance',
            'total_return', 'total_return_percentage', 'is_active',
            'risk_tolerance', 'investment_objective', 'benchmark',
            'positions_count', 'return_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'current_value', 'total_return', 'total_return_percentage']
    
    def get_positions_count(self, obj):
        return obj.positions.filter(status='OPEN').count()
    
    def get_return_percentage(self, obj):
        if obj.initial_value and obj.initial_value > 0:
            return float(obj.total_return_percentage or 0)
        return 0.0


class StockSerializer(serializers.ModelSerializer):
    """Simplified stock serializer for positions"""
    market_name = serializers.CharField(source='market.name', read_only=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'sector', 'market_name']


class PositionSerializer(serializers.ModelSerializer):
    """Serializer for Position model"""
    stock = StockSerializer(read_only=True)
    stock_symbol = serializers.CharField(write_only=True)
    unrealized_pnl_percentage = serializers.SerializerMethodField()
    portfolio_weight = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'portfolio', 'stock', 'stock_symbol', 'quantity',
            'entry_price', 'current_price', 'current_value', 'total_cost',
            'unrealized_pnl', 'unrealized_pnl_percentage', 'portfolio_weight',
            'status', 'opened_at', 'closed_at'
        ]
        read_only_fields = ['current_price', 'current_value', 'unrealized_pnl']
    
    def get_unrealized_pnl_percentage(self, obj):
        if obj.total_cost and obj.total_cost > 0:
            return float((obj.unrealized_pnl / obj.total_cost) * 100)
        return 0.0
    
    def get_portfolio_weight(self, obj):
        if obj.portfolio.current_value and obj.portfolio.current_value > 0:
            return float((obj.current_value / obj.portfolio.current_value) * 100)
        return 0.0
    
    def create(self, validated_data):
        stock_symbol = validated_data.pop('stock_symbol')
        try:
            stock = Stock.objects.get(symbol=stock_symbol)
            validated_data['stock'] = stock
            return super().create(validated_data)
        except Stock.DoesNotExist:
            raise serializers.ValidationError(f"Stock with symbol {stock_symbol} not found")


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    stock = StockSerializer(read_only=True)
    position_id = serializers.IntegerField(source='position.id', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'portfolio', 'position_id', 'stock', 'transaction_type',
            'quantity', 'price', 'amount', 'commission', 'fees',
            'total_cost', 'cash_impact', 'notes', 'executed_at'
        ]
        read_only_fields = ['executed_at']


class RiskMetricsSerializer(serializers.ModelSerializer):
    """Serializer for RiskMetrics model"""
    
    class Meta:
        model = RiskMetrics
        fields = [
            'id', 'portfolio', 'volatility', 'beta', 'sharpe_ratio',
            'max_drawdown', 'var_95', 'var_99', 'expected_shortfall',
            'tracking_error', 'information_ratio', 'sortino_ratio',
            'calculated_at'
        ]


class PortfolioPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioPerformance model"""
    
    class Meta:
        model = PortfolioPerformance
        fields = [
            'id', 'portfolio', 'date', 'portfolio_value', 'cash_balance',
            'daily_return', 'cumulative_return', 'total_return_percentage',
            'benchmark_return', 'excess_return'
        ]


class PortfolioOptimizationSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioOptimization model"""
    
    class Meta:
        model = PortfolioOptimization
        fields = [
            'id', 'portfolio', 'optimization_method', 'target_return',
            'target_risk', 'recommended_allocations', 'expected_return',
            'expected_risk', 'expected_sharpe', 'constraints',
            'created_at'
        ]


class PortfolioBenchmarkSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioBenchmark model"""
    
    class Meta:
        model = PortfolioBenchmark
        fields = [
            'id', 'name', 'symbol', 'description', 'benchmark_type',
            'data_source', 'is_active'
        ]


class RebalancingRuleSerializer(serializers.ModelSerializer):
    """Serializer for RebalancingRule model"""
    
    class Meta:
        model = RebalancingRule
        fields = [
            'id', 'portfolio', 'rebalancing_frequency', 'threshold_percentage',
            'target_allocations', 'constraints', 'is_active',
            'last_rebalanced', 'next_rebalancing_date'
        ]


class PortfolioAnalysisSerializer(serializers.Serializer):
    """Serializer for portfolio analysis results"""
    portfolio_id = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_return = serializers.DecimalField(max_digits=15, decimal_places=2)
    return_percentage = serializers.DecimalField(max_digits=8, decimal_places=4)
    
    # Risk metrics
    volatility = serializers.DecimalField(max_digits=8, decimal_places=4, allow_null=True)
    sharpe_ratio = serializers.DecimalField(max_digits=8, decimal_places=4, allow_null=True)
    max_drawdown = serializers.DecimalField(max_digits=8, decimal_places=4, allow_null=True)
    var_95 = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    
    # Allocation
    sectors = serializers.DictField(child=serializers.DecimalField(max_digits=5, decimal_places=2))
    top_holdings = serializers.ListField(child=serializers.DictField())


class QuickTradeSerializer(serializers.Serializer):
    """Serializer for quick trade requests"""
    portfolio_id = serializers.IntegerField()
    symbol = serializers.CharField(max_length=20)
    action = serializers.ChoiceField(choices=['BUY', 'SELL'])
    quantity = serializers.DecimalField(max_digits=15, decimal_places=4)
    order_type = serializers.ChoiceField(choices=['MARKET', 'LIMIT'], default='MARKET')
    limit_price = serializers.DecimalField(max_digits=15, decimal_places=4, required=False, allow_null=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, data):
        if data['order_type'] == 'LIMIT' and not data.get('limit_price'):
            raise serializers.ValidationError("Limit price is required for limit orders")
        return data