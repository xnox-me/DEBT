#!/usr/bin/env python3
"""
Financial Dashboard Configuration
Business intelligence settings and API configurations for DEBT financial analysis.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class FinancialConfig:
    """Configuration class for DEBT financial dashboard."""
    
    # API Configuration
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv('ALPHA_VANTAGE_API_KEY')
    OPENBB_API_KEY: Optional[str] = os.getenv('OPENBB_API_KEY')
    FRED_API_KEY: Optional[str] = os.getenv('FRED_API_KEY')
    
    # Business Stock Universe
    DEFAULT_STOCKS: List[str] = None
    BUSINESS_SECTORS: Dict[str, List[str]] = None
    
    # Technical Analysis Parameters
    SMA_PERIODS: List[int] = None
    EMA_PERIODS: List[int] = None
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BOLLINGER_PERIOD: int = 20
    BOLLINGER_STD: float = 2.0
    
    # ML Model Configuration
    ML_TRAIN_TEST_SPLIT: float = 0.8
    PREDICTION_DAYS_AHEAD: int = 5
    RANDOM_FOREST_ESTIMATORS: int = 100
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Dashboard Settings
    CACHE_DURATION: int = 300  # 5 minutes
    MAX_SYMBOLS_PER_REQUEST: int = 20
    DEFAULT_PERIOD: str = "1y"
    
    # Business Intelligence Thresholds
    STRONG_BUY_THRESHOLD: float = 2.0
    BUY_THRESHOLD: float = 0.5
    STRONG_SELL_THRESHOLD: float = -2.0
    SELL_THRESHOLD: float = -0.5
    
    # Risk Management
    MAX_POSITION_SIZE: float = 0.1  # 10% max per position
    STOP_LOSS_PERCENTAGE: float = 0.05  # 5% stop loss
    TAKE_PROFIT_PERCENTAGE: float = 0.15  # 15% take profit
    
    def __post_init__(self):
        """Initialize default values after instance creation."""
        if self.DEFAULT_STOCKS is None:
            self.DEFAULT_STOCKS = [
                # Technology Leaders
                "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
                # Financial Services
                "JPM", "BAC", "WFC", "GS", "MS", "C",
                # Healthcare & Consumer
                "JNJ", "PFE", "UNH", "PG", "KO", "WMT",
                # Market ETFs
                "SPY", "QQQ", "IWM", "VTI"
            ]
        
        if self.BUSINESS_SECTORS is None:
            self.BUSINESS_SECTORS = {
                "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA"],
                "Financial": ["JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA"],
                "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "BMY"],
                "Consumer": ["PG", "KO", "WMT", "HD", "MCD", "NKE"],
                "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "HAL"],
                "Industrial": ["GE", "CAT", "BA", "MMM", "UPS", "FDX"],
                "ETFs": ["SPY", "QQQ", "IWM", "VTI", "ARKK", "XLF"]
            }
        
        if self.SMA_PERIODS is None:
            self.SMA_PERIODS = [5, 10, 20, 50, 100, 200]
        
        if self.EMA_PERIODS is None:
            self.EMA_PERIODS = [12, 26, 50]

# Global configuration instance
config = FinancialConfig()

class BusinessMetrics:
    """Business-focused financial metrics and KPIs."""
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio for risk-adjusted returns."""
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / excess_returns.std() * (252 ** 0.5)
    
    @staticmethod
    def calculate_max_drawdown(prices):
        """Calculate maximum drawdown for risk assessment."""
        rolling_max = prices.expanding().max()
        drawdown = (prices - rolling_max) / rolling_max
        return drawdown.min()
    
    @staticmethod
    def calculate_volatility(returns, annualize=True):
        """Calculate price volatility."""
        vol = returns.std()
        return vol * (252 ** 0.5) if annualize else vol
    
    @staticmethod
    def calculate_beta(stock_returns, market_returns):
        """Calculate stock beta relative to market."""
        covariance = stock_returns.cov(market_returns)
        market_variance = market_returns.var()
        return covariance / market_variance
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI technical indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def generate_trading_signals(df):
        """Generate business trading signals based on technical analysis."""
        signals = []
        
        # Moving average crossover
        if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
            signals.append("MA_BULLISH")
        elif df['SMA_20'].iloc[-1] < df['SMA_50'].iloc[-1]:
            signals.append("MA_BEARISH")
        
        # RSI signals
        current_rsi = df['RSI'].iloc[-1]
        if current_rsi > 70:
            signals.append("RSI_OVERBOUGHT")
        elif current_rsi < 30:
            signals.append("RSI_OVERSOLD")
        
        # MACD signals
        if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1]:
            signals.append("MACD_BULLISH")
        else:
            signals.append("MACD_BEARISH")
        
        # Volume confirmation
        if df['Volume_Ratio'].iloc[-1] > 1.5:
            signals.append("HIGH_VOLUME")
        
        return signals

class RiskManagement:
    """Business risk management and position sizing."""
    
    @staticmethod
    def calculate_position_size(account_value, risk_per_trade, stop_loss_pct):
        """Calculate optimal position size based on risk management."""
        risk_amount = account_value * risk_per_trade
        position_size = risk_amount / stop_loss_pct
        return min(position_size, account_value * config.MAX_POSITION_SIZE)
    
    @staticmethod
    def validate_trade_parameters(entry_price, stop_loss, take_profit):
        """Validate trade parameters for business rules compliance."""
        stop_loss_pct = abs(entry_price - stop_loss) / entry_price
        take_profit_pct = abs(take_profit - entry_price) / entry_price
        
        return {
            'valid': True,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'risk_reward_ratio': take_profit_pct / stop_loss_pct if stop_loss_pct > 0 else 0
        }
    
    @staticmethod
    def calculate_portfolio_risk(positions, correlation_matrix):
        """Calculate overall portfolio risk considering correlations."""
        # Simplified portfolio risk calculation
        total_risk = 0
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions):
                correlation = correlation_matrix.iloc[i, j] if i != j else 1
                total_risk += pos1['weight'] * pos2['weight'] * correlation
        return total_risk ** 0.5

# Market data sources configuration
MARKET_DATA_SOURCES = {
    'yfinance': {
        'name': 'Yahoo Finance',
        'rate_limit': 2000,  # requests per hour
        'delay': 0.1,  # seconds between requests
        'supported_intervals': ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    },
    'alpha_vantage': {
        'name': 'Alpha Vantage',
        'rate_limit': 5,  # requests per minute (free tier)
        'delay': 12,  # seconds between requests
        'supported_intervals': ['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly']
    },
    'openbb': {
        'name': 'OpenBB Platform',
        'rate_limit': 100,  # requests per minute
        'delay': 0.6,  # seconds between requests
        'supported_intervals': ['1d', '1wk', '1mo']
    }
}

# Business intelligence report templates
REPORT_TEMPLATES = {
    'executive_summary': {
        'sections': ['market_overview', 'portfolio_performance', 'risk_metrics', 'recommendations'],
        'frequency': 'daily',
        'recipients': ['executives', 'portfolio_managers']
    },
    'technical_analysis': {
        'sections': ['price_action', 'technical_indicators', 'trading_signals', 'support_resistance'],
        'frequency': 'hourly',
        'recipients': ['traders', 'analysts']
    },
    'risk_report': {
        'sections': ['var_analysis', 'stress_testing', 'correlation_analysis', 'portfolio_metrics'],
        'frequency': 'weekly',
        'recipients': ['risk_managers', 'compliance']
    }
}