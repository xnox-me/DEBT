import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger('debt_trading')

def get_tasi_companies() -> List[Dict]:
    """Get list of major TASI companies with their data"""
    tasi_symbols = [
        {'symbol': '2222.SR', 'name': 'Saudi Aramco', 'sector': 'Energy'},
        {'symbol': '1120.SR', 'name': 'Al Rajhi Bank', 'sector': 'Banking'},
        {'symbol': '2030.SR', 'name': 'SABIC', 'sector': 'Petrochemicals'},
        {'symbol': '1180.SR', 'name': 'Al Rajhi Company', 'sector': 'Real Estate'},
        {'symbol': '2380.SR', 'name': 'Petrochemical Industries', 'sector': 'Petrochemicals'},
        {'symbol': '4030.SR', 'name': 'National Petrochemical', 'sector': 'Petrochemicals'},
        {'symbol': '2010.SR', 'name': 'Saudi Basic Industries', 'sector': 'Basic Materials'},
        {'symbol': '1211.SR', 'name': 'Alinma Bank', 'sector': 'Banking'},
        {'symbol': '1050.SR', 'name': 'Bank AlJazira', 'sector': 'Banking'},
        {'symbol': '4020.SR', 'name': 'Saudi Cement', 'sector': 'Building Materials'},
    ]
    
    return tasi_symbols

def get_global_markets_data() -> Dict:
    """Get configuration for global markets"""
    return {
        'USA': {
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'META', 'NVDA'],
            'indices': ['^GSPC', '^DJI', '^IXIC'],  # S&P 500, Dow Jones, NASDAQ
        },
        'China': {
            'stocks': ['BABA', 'BIDU', 'JD', 'TCEHY'],
            'indices': ['000001.SS'],  # SSE Composite
        },
        'Japan': {
            'stocks': ['TM', 'SONY', '6758.T', '7203.T'],  # Toyota, Sony
            'indices': ['^N225'],  # Nikkei 225
        },
        'UK': {
            'stocks': ['SHEL', 'BP', 'VOD'],
            'indices': ['^FTSE'],  # FTSE 100
        },
        'CRYPTO': {
            'major': ['BTC-USD', 'ETH-USD', 'BNB-USD'],
            'altcoins': ['XRP-USD', 'ADA-USD', 'SOL-USD', 'DOGE-USD'],
        },
        'PRECIOUS_METALS': {
            'futures': ['GC=F', 'SI=F', 'PL=F', 'PA=F'],  # Gold, Silver, Platinum, Palladium
        }
    }

def fetch_market_data(symbol: str, period: str = '1mo', interval: str = '1d') -> Optional[pd.DataFrame]:
    """Fetch market data for a given symbol"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            logger.warning(f"No data found for symbol: {symbol}")
            return None
        
        return hist
    
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for market data"""
    if data.empty:
        return data
    
    try:
        # Simple Moving Averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        data['BB_Width'] = data['BB_Upper'] - data['BB_Lower']
        data['BB_Position'] = (data['Close'] - data['BB_Lower']) / data['BB_Width']
        
        # Volume indicators
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']
        
        # Price changes
        data['Price_Change'] = data['Close'].diff()
        data['Price_Change_Pct'] = data['Close'].pct_change() * 100
        
        # Support and Resistance levels (simplified)
        data['Resistance'] = data['High'].rolling(window=20).max()
        data['Support'] = data['Low'].rolling(window=20).min()
        
        return data
    
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        return data

def analyze_trading_signals(data: pd.DataFrame) -> Dict:
    """Analyze data to generate trading signals"""
    if data.empty or len(data) < 50:
        return {'signal': 'HOLD', 'confidence': 'LOW', 'reasons': ['Insufficient data']}
    
    try:
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        signals = []
        confidence_factors = []
        
        # RSI Analysis
        if 'RSI' in data.columns and not pd.isna(latest['RSI']):
            if latest['RSI'] < 30:
                signals.append('BUY')
                confidence_factors.append('RSI Oversold')
            elif latest['RSI'] > 70:
                signals.append('SELL')
                confidence_factors.append('RSI Overbought')
        
        # MACD Analysis
        if 'MACD' in data.columns and 'MACD_Signal' in data.columns:
            if (latest['MACD'] > latest['MACD_Signal'] and 
                prev['MACD'] <= prev['MACD_Signal']):
                signals.append('BUY')
                confidence_factors.append('MACD Bullish Crossover')
            elif (latest['MACD'] < latest['MACD_Signal'] and 
                  prev['MACD'] >= prev['MACD_Signal']):
                signals.append('SELL')
                confidence_factors.append('MACD Bearish Crossover')
        
        # Moving Average Analysis
        if 'SMA_20' in data.columns and 'SMA_50' in data.columns:
            if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                signals.append('BUY')
                confidence_factors.append('Price Above Moving Averages')
            elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
                signals.append('SELL')
                confidence_factors.append('Price Below Moving Averages')
        
        # Bollinger Bands Analysis
        if 'BB_Position' in data.columns and not pd.isna(latest['BB_Position']):
            if latest['BB_Position'] < 0.1:
                signals.append('BUY')
                confidence_factors.append('Price Near Lower Bollinger Band')
            elif latest['BB_Position'] > 0.9:
                signals.append('SELL')
                confidence_factors.append('Price Near Upper Bollinger Band')
        
        # Volume Analysis
        if 'Volume_Ratio' in data.columns and not pd.isna(latest['Volume_Ratio']):
            if latest['Volume_Ratio'] > 1.5:
                confidence_factors.append('High Volume Confirmation')
        
        # Determine overall signal
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        
        if buy_signals > sell_signals:
            final_signal = 'STRONG_BUY' if buy_signals >= 3 else 'BUY'
        elif sell_signals > buy_signals:
            final_signal = 'STRONG_SELL' if sell_signals >= 3 else 'SELL'
        else:
            final_signal = 'HOLD'
        
        # Determine confidence
        total_factors = len(confidence_factors)
        if total_factors >= 4:
            confidence = 'VERY_HIGH'
        elif total_factors >= 3:
            confidence = 'HIGH'
        elif total_factors >= 2:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'confidence_score': min(95, 50 + (total_factors * 10)),
            'reasons': confidence_factors,
            'technical_data': {
                'rsi': float(latest['RSI']) if 'RSI' in data.columns and not pd.isna(latest['RSI']) else None,
                'macd': float(latest['MACD']) if 'MACD' in data.columns and not pd.isna(latest['MACD']) else None,
                'bb_position': float(latest['BB_Position']) if 'BB_Position' in data.columns and not pd.isna(latest['BB_Position']) else None,
                'volume_ratio': float(latest['Volume_Ratio']) if 'Volume_Ratio' in data.columns and not pd.isna(latest['Volume_Ratio']) else None,
            }
        }
    
    except Exception as e:
        logger.error(f"Error analyzing trading signals: {str(e)}")
        return {'signal': 'HOLD', 'confidence': 'LOW', 'reasons': ['Analysis error']}

def get_market_summary(symbols: List[str]) -> Dict:
    """Get summary data for multiple symbols"""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'symbols': [],
        'market_status': 'OPEN',  # Simplified
        'total_symbols': len(symbols),
    }
    
    for symbol in symbols:
        try:
            data = fetch_market_data(symbol, period='1d', interval='1d')
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                prev_close = data.iloc[-2]['Close'] if len(data) > 1 else latest['Open']
                
                symbol_data = {
                    'symbol': symbol,
                    'price': float(latest['Close']),
                    'change': float(latest['Close'] - prev_close),
                    'change_percent': float(((latest['Close'] - prev_close) / prev_close) * 100),
                    'volume': int(latest['Volume']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                }
                
                summary['symbols'].append(symbol_data)
        
        except Exception as e:
            logger.warning(f"Failed to get summary for {symbol}: {str(e)}")
            continue
    
    return summary

def validate_symbol(symbol: str) -> bool:
    """Validate if a symbol exists and has data"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return 'symbol' in info or 'shortName' in info
    except:
        return False

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency amounts"""
    if currency == 'SAR':
        return f"ر.س {amount:,.2f}"
    elif currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_portfolio_metrics(holdings: List[Dict]) -> Dict:
    """Calculate portfolio performance metrics"""
    total_value = sum(holding.get('current_value', 0) for holding in holdings)
    total_cost = sum(holding.get('cost_basis', 0) for holding in holdings)
    
    if total_cost == 0:
        return {'total_value': 0, 'total_return': 0, 'return_percent': 0}
    
    total_return = total_value - total_cost
    return_percent = (total_return / total_cost) * 100
    
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_return': total_return,
        'return_percent': return_percent,
        'holdings_count': len(holdings),
    }