from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json

class Market(models.Model):
    """Represents different markets (TASI, NYSE, etc.)"""
    MARKET_TYPES = [
        ('TASI', 'Saudi Stock Exchange (TASI)'),
        ('NYSE', 'New York Stock Exchange'),
        ('NASDAQ', 'NASDAQ'),
        ('LSE', 'London Stock Exchange'),
        ('CRYPTO', 'Cryptocurrency'),
        ('PRECIOUS', 'Precious Metals'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    market_type = models.CharField(max_length=20, choices=MARKET_TYPES)
    country = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Stock(models.Model):
    """Individual stocks/assets in different markets"""
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='stocks')
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_sharia_compliant = models.BooleanField(default=False)  # For Islamic finance
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['market', 'symbol']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"

class MarketData(models.Model):
    """Real-time and historical market data"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='market_data')
    timestamp = models.DateTimeField()
    
    # Price data
    open_price = models.DecimalField(max_digits=15, decimal_places=4)
    high_price = models.DecimalField(max_digits=15, decimal_places=4)
    low_price = models.DecimalField(max_digits=15, decimal_places=4)
    close_price = models.DecimalField(max_digits=15, decimal_places=4)
    volume = models.BigIntegerField()
    
    # Calculated fields
    change = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    change_percent = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Technical indicators
    sma_20 = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    sma_50 = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    rsi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    macd = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['stock', 'timestamp']
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['stock', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} at {self.timestamp}"

class Watchlist(models.Model):
    """User's watchlist of stocks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stocks = models.ManyToManyField(Stock, related_name='watchlists')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class Alert(models.Model):
    """Price alerts for stocks"""
    ALERT_TYPES = [
        ('ABOVE', 'Price Above'),
        ('BELOW', 'Price Below'),
        ('CHANGE_UP', 'Price Change Up %'),
        ('CHANGE_DOWN', 'Price Change Down %'),
        ('VOLUME', 'Volume Above'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('EXPIRED', 'Expired'),
        ('DISABLED', 'Disabled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=15, decimal_places=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    message = models.TextField(blank=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} {self.alert_type} {self.threshold}"

class TradingSignal(models.Model):
    """AI/ML generated trading signals"""
    SIGNAL_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold'),
        ('STRONG_BUY', 'Strong Buy'),
        ('STRONG_SELL', 'Strong Sell'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('LOW', 'Low (60-69%)'),
        ('MEDIUM', 'Medium (70-79%)'),
        ('HIGH', 'High (80-89%)'),
        ('VERY_HIGH', 'Very High (90%+)'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='signals')
    signal_type = models.CharField(max_length=20, choices=SIGNAL_TYPES)
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Signal details
    target_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    time_horizon = models.CharField(max_length=50)  # '1D', '1W', '1M', etc.
    
    # Technical analysis basis
    technical_indicators = models.JSONField(default=dict)
    fundamental_data = models.JSONField(default=dict)
    
    # ML model info
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=20)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', '-created_at']),
            models.Index(fields=['signal_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.signal_type} ({self.confidence})"