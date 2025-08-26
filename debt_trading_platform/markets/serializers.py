from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Market, Stock, MarketData, Watchlist, Alert, TradingSignal

class MarketSerializer(serializers.ModelSerializer):
    stocks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Market
        fields = ['id', 'name', 'code', 'market_type', 'country', 'currency', 
                 'timezone', 'is_active', 'created_at', 'stocks_count']
    
    def get_stocks_count(self, obj):
        return obj.stocks.filter(is_active=True).count()

class StockSerializer(serializers.ModelSerializer):
    market_name = serializers.CharField(source='market.name', read_only=True)
    market_code = serializers.CharField(source='market.code', read_only=True)
    latest_price = serializers.SerializerMethodField()
    price_change = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'sector', 'industry', 'market_cap',
                 'is_active', 'is_sharia_compliant', 'market_name', 'market_code',
                 'latest_price', 'price_change', 'created_at']
    
    def get_latest_price(self, obj):
        latest_data = obj.market_data.first()
        return float(latest_data.close_price) if latest_data else None
    
    def get_price_change(self, obj):
        latest_data = obj.market_data.first()
        return float(latest_data.change_percent) if latest_data else None

class MarketDataSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    
    class Meta:
        model = MarketData
        fields = ['id', 'stock_symbol', 'stock_name', 'timestamp', 'open_price',
                 'high_price', 'low_price', 'close_price', 'volume', 'change',
                 'change_percent', 'sma_20', 'sma_50', 'rsi', 'macd', 'created_at']

class WatchlistStockSerializer(serializers.ModelSerializer):
    """Simplified stock serializer for watchlists"""
    market_code = serializers.CharField(source='market.code', read_only=True)
    latest_price = serializers.SerializerMethodField()
    price_change = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'market_code', 'latest_price', 'price_change']
    
    def get_latest_price(self, obj):
        latest_data = obj.market_data.first()
        return float(latest_data.close_price) if latest_data else None
    
    def get_price_change(self, obj):
        latest_data = obj.market_data.first()
        return float(latest_data.change_percent) if latest_data else None

class WatchlistSerializer(serializers.ModelSerializer):
    stocks = WatchlistStockSerializer(many=True, read_only=True)
    stocks_count = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'description', 'stocks', 'stocks_count', 
                 'is_public', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user']
    
    def get_stocks_count(self, obj):
        return obj.stocks.count()

class AlertSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'stock', 'stock_symbol', 'stock_name', 'alert_type',
                 'threshold', 'status', 'message', 'triggered_at', 'user_name',
                 'created_at']
        read_only_fields = ['user', 'triggered_at']

class TradingSignalSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    market_code = serializers.CharField(source='stock.market.code', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = TradingSignal
        fields = ['id', 'stock_symbol', 'stock_name', 'market_code', 'signal_type',
                 'confidence', 'confidence_score', 'target_price', 'stop_loss',
                 'time_horizon', 'technical_indicators', 'fundamental_data',
                 'model_name', 'model_version', 'days_remaining', 'created_at', 'expires_at']
    
    def get_days_remaining(self, obj):
        from datetime import datetime
        if obj.expires_at:
            delta = obj.expires_at - datetime.now(obj.expires_at.tzinfo)
            return delta.days if delta.days > 0 else 0
        return None

class MarketOverviewSerializer(serializers.Serializer):
    """Serializer for market overview data"""
    symbol = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=15, decimal_places=4)
    change = serializers.DecimalField(max_digits=15, decimal_places=4)
    change_percent = serializers.DecimalField(max_digits=8, decimal_places=4)
    volume = serializers.IntegerField()
    market_cap = serializers.IntegerField(required=False, allow_null=True)

class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data"""
    timestamp = serializers.DateTimeField()
    open = serializers.DecimalField(max_digits=15, decimal_places=4)
    high = serializers.DecimalField(max_digits=15, decimal_places=4)
    low = serializers.DecimalField(max_digits=15, decimal_places=4)
    close = serializers.DecimalField(max_digits=15, decimal_places=4)
    volume = serializers.IntegerField()

class QuoteSerializer(serializers.Serializer):
    """Serializer for real-time quotes"""
    symbol = serializers.CharField()
    current_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    open_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    high_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    low_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    volume = serializers.IntegerField()
    market_cap = serializers.IntegerField(required=False, allow_null=True)
    pe_ratio = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    dividend_yield = serializers.DecimalField(max_digits=5, decimal_places=4, required=False, allow_null=True)
    timestamp = serializers.DateTimeField()

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for API responses"""
    watchlists_count = serializers.SerializerMethodField()
    alerts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                 'date_joined', 'watchlists_count', 'alerts_count']
    
    def get_watchlists_count(self, obj):
        return obj.watchlists.count()
    
    def get_alerts_count(self, obj):
        return obj.alerts.filter(status='ACTIVE').count()