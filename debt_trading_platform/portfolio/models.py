from django.db import models
from django.contrib.auth.models import User
from markets.models import Stock, Market
from decimal import Decimal
import json

class Portfolio(models.Model):
    """User's trading portfolio"""
    PORTFOLIO_TYPES = [
        ('AGGRESSIVE', 'Aggressive Growth'),
        ('MODERATE', 'Moderate Growth'),
        ('CONSERVATIVE', 'Conservative'),
        ('INCOME', 'Income Focused'),
        ('BALANCED', 'Balanced'),
        ('CUSTOM', 'Custom Strategy'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('SAR', 'Saudi Riyal'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CNY', 'Chinese Yuan'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    portfolio_type = models.CharField(max_length=20, choices=PORTFOLIO_TYPES, default='BALANCED')
    
    # Portfolio configuration
    base_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    initial_value = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    
    # Risk management settings
    max_position_size = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)  # Percentage
    stop_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    take_profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    
    # Performance tracking
    total_return = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    total_return_percentage = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    annualized_return = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    volatility = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Portfolio allocation targets
    stock_allocation_target = models.DecimalField(max_digits=5, decimal_places=2, default=70.0)
    bond_allocation_target = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    cash_allocation_target = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    
    is_active = models.BooleanField(default=True)
    is_paper_trading = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class Position(models.Model):
    """Individual positions in a portfolio"""
    POSITION_TYPES = [
        ('LONG', 'Long Position'),
        ('SHORT', 'Short Position'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('PARTIAL', 'Partially Closed'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='positions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='positions')
    
    # Position details
    position_type = models.CharField(max_length=10, choices=POSITION_TYPES, default='LONG')
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    entry_price = models.DecimalField(max_digits=15, decimal_places=4)
    current_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Cost and value
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unrealized_pnl = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    realized_pnl = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Risk management
    stop_loss_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    take_profit_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Position allocation
    portfolio_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['portfolio', 'status']),
            models.Index(fields=['stock', 'status']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol} ({self.quantity})"

class Transaction(models.Model):
    """Trading transactions"""
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('DIVIDEND', 'Dividend'),
        ('SPLIT', 'Stock Split'),
        ('DEPOSIT', 'Cash Deposit'),
        ('WITHDRAWAL', 'Cash Withdrawal'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Transaction costs
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Cash impact
    cash_impact = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Transaction metadata
    notes = models.TextField(blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['portfolio', '-executed_at']),
            models.Index(fields=['transaction_type', '-executed_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.stock.symbol if self.stock else 'Cash'} - {self.amount}"

class RiskMetrics(models.Model):
    """Risk analysis metrics for portfolios"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='risk_metrics')
    
    # Risk calculations date range
    calculation_date = models.DateField()
    period_days = models.IntegerField(default=252)  # Trading days in a year
    
    # Risk metrics
    var_95 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Value at Risk 95%
    var_99 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Value at Risk 99%
    expected_shortfall = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Portfolio risk measures
    portfolio_volatility = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    portfolio_beta = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    correlation_to_market = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Concentration risk
    concentration_risk = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    largest_position_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    top_5_concentration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Sector and geographic diversification
    sector_diversification_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    geographic_diversification_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Liquidity risk
    liquidity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Risk assessment
    overall_risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    risk_rating = models.CharField(max_length=20, blank=True)  # LOW, MEDIUM, HIGH, VERY_HIGH
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculation_date']
        unique_together = ['portfolio', 'calculation_date']
    
    def __str__(self):
        return f"{self.portfolio.name} - Risk Metrics ({self.calculation_date})"

class PortfolioPerformance(models.Model):
    """Daily portfolio performance tracking"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='performance_history')
    
    date = models.DateField()
    portfolio_value = models.DecimalField(max_digits=15, decimal_places=2)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2)
    positions_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Daily performance
    daily_return = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    daily_pnl = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Cumulative performance
    total_return = models.DecimalField(max_digits=8, decimal_places=4)
    total_return_percentage = models.DecimalField(max_digits=8, decimal_places=4)
    
    # Benchmark comparison
    benchmark_return = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    alpha = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['portfolio', 'date']
        indexes = [
            models.Index(fields=['portfolio', '-date']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.date}"

class PortfolioOptimization(models.Model):
    """Portfolio optimization results"""
    OPTIMIZATION_METHODS = [
        ('MEAN_VARIANCE', 'Mean Variance Optimization'),
        ('RISK_PARITY', 'Risk Parity'),
        ('BLACK_LITTERMAN', 'Black-Litterman'),
        ('MINIMUM_VARIANCE', 'Minimum Variance'),
        ('MAXIMUM_SHARPE', 'Maximum Sharpe Ratio'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='optimizations')
    
    optimization_method = models.CharField(max_length=20, choices=OPTIMIZATION_METHODS)
    target_return = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    target_risk = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Optimization constraints
    constraints = models.JSONField(default=dict)
    
    # Recommended allocations
    recommended_allocations = models.JSONField(default=dict)
    current_allocations = models.JSONField(default=dict)
    
    # Expected performance
    expected_return = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    expected_risk = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    expected_sharpe = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Implementation status
    is_implemented = models.BooleanField(default=False)
    implementation_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.optimization_method} ({self.created_at.date()})"

class PortfolioBenchmark(models.Model):
    """Benchmark indices for portfolio comparison"""
    BENCHMARK_TYPES = [
        ('INDEX', 'Market Index'),
        ('ETF', 'Exchange Traded Fund'),
        ('CUSTOM', 'Custom Benchmark'),
    ]
    
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20, unique=True)
    benchmark_type = models.CharField(max_length=20, choices=BENCHMARK_TYPES)
    description = models.TextField(blank=True)
    
    # Benchmark composition
    stocks = models.ManyToManyField(Stock, through='BenchmarkWeight', related_name='benchmarks')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"

class BenchmarkWeight(models.Model):
    """Weight of stocks in benchmark indices"""
    benchmark = models.ForeignKey(PortfolioBenchmark, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=4)  # Percentage weight
    
    class Meta:
        unique_together = ['benchmark', 'stock']
    
    def __str__(self):
        return f"{self.benchmark.symbol} - {self.stock.symbol} ({self.weight}%)"

class RebalancingRule(models.Model):
    """Automatic portfolio rebalancing rules"""
    REBALANCING_FREQUENCY = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUALLY', 'Annually'),
        ('THRESHOLD', 'Threshold Based'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='rebalancing_rules')
    
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=REBALANCING_FREQUENCY)
    
    # Threshold settings
    deviation_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)  # Percentage
    
    # Target allocations
    target_allocations = models.JSONField(default=dict)
    
    # Execution settings
    auto_execute = models.BooleanField(default=False)
    last_rebalanced = models.DateTimeField(null=True, blank=True)
    next_rebalance_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.frequency} Rebalancing"


# Import auto-trading models to make them available
from .auto_trading_models import (
    AutoTradingStrategy, AutoTradingSignal, WorkflowExecution,
    TradingWebhook, AutoTradingLog, TradingBotConfiguration
)