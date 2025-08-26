from django.db import models
from django.contrib.auth.models import User
from markets.models import Stock, Market
from decimal import Decimal
import json

class MLModel(models.Model):
    """Machine Learning models for trading predictions"""
    MODEL_TYPES = [
        ('LSTM', 'Long Short-Term Memory'),
        ('ARIMA', 'AutoRegressive Integrated Moving Average'),
        ('RF', 'Random Forest'),
        ('SVM', 'Support Vector Machine'),
        ('LINEAR', 'Linear Regression'),
        ('ENSEMBLE', 'Ensemble Model'),
    ]
    
    PREDICTION_TYPES = [
        ('PRICE', 'Price Prediction'),
        ('TREND', 'Trend Direction'),
        ('VOLATILITY', 'Volatility Forecast'),
        ('SIGNAL', 'Trading Signal'),
        ('RISK', 'Risk Assessment'),
    ]
    
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    description = models.TextField()
    
    # Model performance metrics
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Model parameters
    parameters = models.JSONField(default=dict)
    training_data_period = models.CharField(max_length=50, default='1y')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-accuracy', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.model_type})"

class Prediction(models.Model):
    """Individual predictions made by ML models"""
    CONFIDENCE_LEVELS = [
        ('VERY_LOW', 'Very Low (50-60%)'),
        ('LOW', 'Low (60-70%)'),
        ('MEDIUM', 'Medium (70-80%)'),
        ('HIGH', 'High (80-90%)'),
        ('VERY_HIGH', 'Very High (90%+)'),
    ]
    
    PREDICTION_STATUS = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('VALIDATED', 'Validated'),
        ('FAILED', 'Failed'),
    ]
    
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='ml_predictions')
    
    # Prediction details
    predicted_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    predicted_trend = models.CharField(max_length=20, null=True, blank=True)  # UP, DOWN, SIDEWAYS
    predicted_volatility = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Confidence and probability
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    probability_up = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    probability_down = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Time horizon
    prediction_horizon = models.CharField(max_length=20, default='1D')  # 1H, 4H, 1D, 1W, 1M
    target_date = models.DateTimeField()
    
    # Input features used
    input_features = models.JSONField(default=dict)
    feature_importance = models.JSONField(default=dict)
    
    # Validation
    actual_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    actual_trend = models.CharField(max_length=20, null=True, blank=True)
    is_accurate = models.BooleanField(null=True, blank=True)
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=PREDICTION_STATUS, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['confidence', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.model.name} ({self.confidence})"

class TradingStrategy(models.Model):
    """ML-based trading strategies"""
    STRATEGY_TYPES = [
        ('MOMENTUM', 'Momentum Strategy'),
        ('MEAN_REVERSION', 'Mean Reversion'),
        ('BREAKOUT', 'Breakout Strategy'),
        ('TREND_FOLLOWING', 'Trend Following'),
        ('ARBITRAGE', 'Arbitrage'),
        ('PAIRS_TRADING', 'Pairs Trading'),
    ]
    
    name = models.CharField(max_length=100)
    strategy_type = models.CharField(max_length=20, choices=STRATEGY_TYPES)
    description = models.TextField()
    
    # Strategy parameters
    entry_conditions = models.JSONField(default=dict)
    exit_conditions = models.JSONField(default=dict)
    risk_management = models.JSONField(default=dict)
    
    # Performance metrics
    total_return = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Associated models
    models_used = models.ManyToManyField(MLModel, related_name='strategies')
    markets = models.ManyToManyField(Market, related_name='strategies')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sharpe_ratio', '-total_return']
    
    def __str__(self):
        return f"{self.name} ({self.strategy_type})"

class BacktestResult(models.Model):
    """Results from backtesting trading strategies"""
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE, related_name='backtest_results')
    
    # Test parameters
    start_date = models.DateField()
    end_date = models.DateField()
    initial_capital = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    
    # Performance results
    final_capital = models.DecimalField(max_digits=15, decimal_places=2)
    total_return = models.DecimalField(max_digits=8, decimal_places=4)
    annualized_return = models.DecimalField(max_digits=8, decimal_places=4)
    volatility = models.DecimalField(max_digits=6, decimal_places=4)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=4)
    max_drawdown = models.DecimalField(max_digits=6, decimal_places=4)
    
    # Trade statistics
    total_trades = models.IntegerField()
    winning_trades = models.IntegerField()
    losing_trades = models.IntegerField()
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)
    avg_win = models.DecimalField(max_digits=8, decimal_places=4)
    avg_loss = models.DecimalField(max_digits=8, decimal_places=4)
    profit_factor = models.DecimalField(max_digits=6, decimal_places=4)
    
    # Detailed results
    daily_returns = models.JSONField(default=list)
    trade_log = models.JSONField(default=list)
    equity_curve = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.strategy.name} - {self.start_date} to {self.end_date}"

class ModelTraining(models.Model):
    """Track model training sessions"""
    TRAINING_STATUS = [
        ('STARTED', 'Training Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('STOPPED', 'Stopped'),
    ]
    
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_sessions')
    
    # Training parameters
    training_data_start = models.DateField()
    training_data_end = models.DateField()
    validation_split = models.DecimalField(max_digits=3, decimal_places=2, default=0.2)
    
    # Training configuration
    hyperparameters = models.JSONField(default=dict)
    feature_columns = models.JSONField(default=list)
    target_column = models.CharField(max_length=50)
    
    # Results
    training_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    validation_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    training_loss = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    validation_loss = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    # Training metadata
    training_time_seconds = models.IntegerField(null=True, blank=True)
    data_points_used = models.IntegerField(null=True, blank=True)
    feature_importance = models.JSONField(default=dict)
    
    status = models.CharField(max_length=20, choices=TRAINING_STATUS, default='STARTED')
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.model.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

class PredictionDashboard(models.Model):
    """Custom dashboards for ML predictions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ml_dashboards')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Dashboard configuration
    models_displayed = models.ManyToManyField(MLModel, related_name='dashboards')
    stocks_tracked = models.ManyToManyField(Stock, related_name='ml_dashboards')
    prediction_types = models.JSONField(default=list)
    time_horizons = models.JSONField(default=list)
    
    # Layout and display options
    layout_config = models.JSONField(default=dict)
    refresh_interval = models.IntegerField(default=300)  # seconds
    
    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"