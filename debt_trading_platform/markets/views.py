from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import json
import logging

from .models import Market, Stock, MarketData, Watchlist, Alert, TradingSignal
from .serializers import (
    MarketSerializer, StockSerializer, MarketDataSerializer,
    WatchlistSerializer, AlertSerializer, TradingSignalSerializer
)
from .utils import (
    fetch_market_data, calculate_technical_indicators,
    get_tasi_companies, get_global_markets_data
)

logger = logging.getLogger('debt_trading')

# Dashboard Views
def markets_dashboard(request):
    """Main markets dashboard"""
    context = {
        'tasi_companies': get_tasi_companies(),
        'global_markets': get_global_markets_data(),
        'user_watchlists': Watchlist.objects.filter(user=request.user) if request.user.is_authenticated else [],
    }
    return render(request, 'markets/dashboard.html', context)

def tasi_dashboard(request):
    """TASI-specific dashboard"""
    tasi_market = Market.objects.filter(code='TASI').first()
    tasi_stocks = Stock.objects.filter(market=tasi_market, is_active=True) if tasi_market else []
    
    context = {
        'market': tasi_market,
        'stocks': tasi_stocks,
        'top_gainers': [],
        'top_losers': [],
        'most_active': [],
    }
    return render(request, 'markets/tasi_dashboard.html', context)

# API ViewSets
class MarketViewSet(viewsets.ModelViewSet):
    """API endpoints for markets"""
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    permission_classes = [AllowAny]

class StockViewSet(viewsets.ModelViewSet):
    """API endpoints for stocks"""
    queryset = Stock.objects.select_related('market').all()
    serializer_class = StockSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Stock.objects.select_related('market').all()
        market_code = self.request.query_params.get('market', None)
        sector = self.request.query_params.get('sector', None)
        
        if market_code:
            queryset = queryset.filter(market__code=market_code)
        if sector:
            queryset = queryset.filter(sector__icontains=sector)
            
        return queryset

class MarketDataViewSet(viewsets.ModelViewSet):
    """API endpoints for market data"""
    queryset = MarketData.objects.select_related('stock').all()
    serializer_class = MarketDataSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = MarketData.objects.select_related('stock').all()
        symbol = self.request.query_params.get('symbol', None)
        days = self.request.query_params.get('days', 30)
        
        if symbol:
            queryset = queryset.filter(stock__symbol=symbol)
            
        # Limit to recent data
        cutoff_date = datetime.now() - timedelta(days=int(days))
        queryset = queryset.filter(timestamp__gte=cutoff_date)
        
        return queryset.order_by('-timestamp')

# Real-time Market Data APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_stock_quote(request, symbol):
    """Get real-time quote for a specific stock"""
    try:
        # Try to get from database first
        stock = get_object_or_404(Stock, symbol=symbol)
        latest_data = MarketData.objects.filter(stock=stock).first()
        
        if latest_data and (datetime.now() - latest_data.created_at.replace(tzinfo=None)).seconds < 300:
            # Use cached data if less than 5 minutes old
            serializer = MarketDataSerializer(latest_data)
            return Response(serializer.data)
        
        # Fetch fresh data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period='1d')
        
        if hist.empty:
            return Response(
                {'error': f'No data found for symbol {symbol}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        latest = hist.iloc[-1]
        
        quote_data = {
            'symbol': symbol,
            'current_price': float(latest['Close']),
            'open_price': float(latest['Open']),
            'high_price': float(latest['High']),
            'low_price': float(latest['Low']),
            'volume': int(latest['Volume']),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'timestamp': datetime.now().isoformat(),
        }
        
        return Response(quote_data)
        
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {str(e)}")
        return Response(
            {'error': f'Failed to fetch data for {symbol}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tasi_overview(request):
    """Get TASI market overview"""
    try:
        tasi_symbols = [
            '2222.SR',  # Saudi Aramco
            '1120.SR',  # Al Rajhi Bank
            '2030.SR',  # SABIC
            '1180.SR',  # Al Rajhi Company
            '2380.SR',  # Petrochemical Industries
        ]
        
        overview_data = []
        
        for symbol in tasi_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                info = ticker.info
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    overview_data.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'price': float(latest['Close']),
                        'change': float(latest['Close'] - latest['Open']),
                        'change_percent': ((latest['Close'] - latest['Open']) / latest['Open']) * 100,
                        'volume': int(latest['Volume']),
                        'market_cap': info.get('marketCap'),
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                continue
        
        return Response({
            'market': 'TASI (Saudi Stock Exchange)',
            'timestamp': datetime.now().isoformat(),
            'stocks': overview_data,
            'total_companies': len(overview_data),
        })
        
    except Exception as e:
        logger.error(f"Error fetching TASI overview: {str(e)}")
        return Response(
            {'error': 'Failed to fetch TASI overview'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_global_overview(request):
    """Get global markets overview"""
    try:
        global_symbols = {
            'USA': ['AAPL', 'MSFT', 'GOOGL', 'TSLA'],
            'CRYPTO': ['BTC-USD', 'ETH-USD', 'BNB-USD'],
            'PRECIOUS': ['GC=F', 'SI=F'],  # Gold, Silver
        }
        
        global_data = {}
        
        for market, symbols in global_symbols.items():
            market_data = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d')
                    info = ticker.info
                    
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        market_data.append({
                            'symbol': symbol,
                            'name': info.get('longName', symbol),
                            'price': float(latest['Close']),
                            'change': float(latest['Close'] - latest['Open']),
                            'change_percent': ((latest['Close'] - latest['Open']) / latest['Open']) * 100,
                            'volume': int(latest['Volume']),
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                    continue
            
            global_data[market] = market_data
        
        return Response({
            'timestamp': datetime.now().isoformat(),
            'markets': global_data,
        })
        
    except Exception as e:
        logger.error(f"Error fetching global overview: {str(e)}")
        return Response(
            {'error': 'Failed to fetch global markets overview'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_market_chart(request, symbol):
    """Get chart data for a specific symbol"""
    try:
        period = request.GET.get('period', '1mo')  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval = request.GET.get('interval', '1d')  # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return Response(
                {'error': f'No chart data found for symbol {symbol}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Convert to chart-friendly format
        chart_data = []
        for timestamp, row in hist.iterrows():
            chart_data.append({
                'timestamp': timestamp.isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
            })
        
        return Response({
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': chart_data,
        })
        
    except Exception as e:
        logger.error(f"Error fetching chart data for {symbol}: {str(e)}")
        return Response(
            {'error': f'Failed to fetch chart data for {symbol}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# User-specific endpoints
class WatchlistViewSet(viewsets.ModelViewSet):
    """API endpoints for user watchlists"""
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    """API endpoints for price alerts"""
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TradingSignalViewSet(viewsets.ModelViewSet):
    """API endpoints for trading signals"""
    queryset = TradingSignal.objects.filter(is_active=True)
    serializer_class = TradingSignalSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = TradingSignal.objects.filter(is_active=True)
        symbol = self.request.query_params.get('symbol', None)
        signal_type = self.request.query_params.get('signal_type', None)
        
        if symbol:
            queryset = queryset.filter(stock__symbol=symbol)
        if signal_type:
            queryset = queryset.filter(signal_type=signal_type)
            
        return queryset.order_by('-created_at')