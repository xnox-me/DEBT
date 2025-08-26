from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import yfinance as yf
import logging

from .models import MLModel, Prediction, TradingStrategy, BacktestResult, ModelTraining, PredictionDashboard
from .serializers import (
    MLModelSerializer, PredictionSerializer, TradingStrategySerializer,
    BacktestResultSerializer, ModelTrainingSerializer
)
from markets.models import Stock, MarketData
from markets.utils import fetch_market_data, calculate_technical_indicators

logger = logging.getLogger('debt_trading')

# Dashboard Views
def ml_dashboard(request):
    """ML predictions dashboard"""
    context = {
        'active_models': MLModel.objects.filter(is_active=True)[:5],
        'recent_predictions': Prediction.objects.filter(status='ACTIVE')[:10],
        'top_strategies': TradingStrategy.objects.filter(is_active=True)[:5],
    }
    return render(request, 'ml_predictions/dashboard.html', context)

def predictions_overview(request):
    """Predictions overview page"""
    context = {
        'predictions': Prediction.objects.filter(status='ACTIVE')[:20],
        'models': MLModel.objects.filter(is_active=True),
    }
    return render(request, 'ml_predictions/predictions.html', context)

# API ViewSets
class MLModelViewSet(viewsets.ModelViewSet):
    """API endpoints for ML models"""
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = MLModel.objects.all()
        model_type = self.request.query_params.get('model_type', None)
        prediction_type = self.request.query_params.get('prediction_type', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if model_type:
            queryset = queryset.filter(model_type=model_type)
        if prediction_type:
            queryset = queryset.filter(prediction_type=prediction_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset.order_by('-accuracy', '-created_at')

class PredictionViewSet(viewsets.ModelViewSet):
    """API endpoints for predictions"""
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Prediction.objects.all()
        symbol = self.request.query_params.get('symbol', None)
        confidence = self.request.query_params.get('confidence', None)
        status_filter = self.request.query_params.get('status', None)
        horizon = self.request.query_params.get('horizon', None)
        
        if symbol:
            queryset = queryset.filter(stock__symbol=symbol)
        if confidence:
            queryset = queryset.filter(confidence=confidence)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if horizon:
            queryset = queryset.filter(prediction_horizon=horizon)
            
        return queryset.order_by('-created_at')

class TradingStrategyViewSet(viewsets.ModelViewSet):
    """API endpoints for trading strategies"""
    queryset = TradingStrategy.objects.filter(is_active=True)
    serializer_class = TradingStrategySerializer
    permission_classes = [AllowAny]

# ML Prediction Functions
def prepare_features(data, symbol):
    """Prepare features for ML model training and prediction"""
    try:
        # Calculate technical indicators
        data_with_indicators = calculate_technical_indicators(data)
        
        if data_with_indicators.empty:
            return None, None
        
        # Feature engineering
        features = pd.DataFrame()
        
        # Price features
        features['price'] = data_with_indicators['Close']
        features['volume'] = data_with_indicators['Volume']
        features['high_low_ratio'] = data_with_indicators['High'] / data_with_indicators['Low']
        features['open_close_ratio'] = data_with_indicators['Open'] / data_with_indicators['Close']
        
        # Technical indicators
        if 'SMA_20' in data_with_indicators.columns:
            features['sma_20'] = data_with_indicators['SMA_20']
            features['price_sma_ratio'] = data_with_indicators['Close'] / data_with_indicators['SMA_20']
        
        if 'SMA_50' in data_with_indicators.columns:
            features['sma_50'] = data_with_indicators['SMA_50']
        
        if 'RSI' in data_with_indicators.columns:
            features['rsi'] = data_with_indicators['RSI']
        
        if 'MACD' in data_with_indicators.columns:
            features['macd'] = data_with_indicators['MACD']
        
        if 'BB_Position' in data_with_indicators.columns:
            features['bb_position'] = data_with_indicators['BB_Position']
        
        # Lag features
        for lag in [1, 2, 3, 5, 10]:
            features[f'price_lag_{lag}'] = features['price'].shift(lag)
            features[f'volume_lag_{lag}'] = features['volume'].shift(lag)
        
        # Returns
        features['return_1d'] = features['price'].pct_change()
        features['return_5d'] = features['price'].pct_change(5)
        features['return_10d'] = features['price'].pct_change(10)
        
        # Volatility
        features['volatility_5d'] = features['return_1d'].rolling(5).std()
        features['volatility_10d'] = features['return_1d'].rolling(10).std()
        
        # Target variable (next day price change)
        target = features['price'].shift(-1) / features['price'] - 1
        
        # Remove rows with NaN values
        valid_mask = ~(features.isnull().any(axis=1) | target.isnull())
        features = features[valid_mask]
        target = target[valid_mask]
        
        return features, target
        
    except Exception as e:
        logger.error(f"Error preparing features for {symbol}: {str(e)}")
        return None, None

def train_ml_model(symbol, model_type='RF', prediction_horizon='1D'):
    """Train an ML model for stock prediction"""
    try:
        # Get stock data
        stock = Stock.objects.get(symbol=symbol)
        data = fetch_market_data(symbol, period='2y', interval='1d')
        
        if data is None or data.empty:
            return None, "No data available for training"
        
        # Prepare features
        features, target = prepare_features(data, symbol)
        
        if features is None or features.empty:
            return None, "Failed to prepare features"
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == 'RF':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            model = LinearRegression()
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate directional accuracy
        directional_accuracy = np.mean(np.sign(y_pred) == np.sign(y_test)) * 100
        
        return {
            'model': model,
            'scaler': scaler,
            'train_score': train_score,
            'test_score': test_score,
            'directional_accuracy': directional_accuracy,
            'feature_names': features.columns.tolist(),
            'feature_importance': model.feature_importances_ if hasattr(model, 'feature_importances_') else None
        }, None
        
    except Exception as e:
        logger.error(f"Error training model for {symbol}: {str(e)}")
        return None, str(e)

def generate_prediction(symbol, model_type='RF', horizon='1D'):
    """Generate ML prediction for a stock"""
    try:
        # Get recent data
        data = fetch_market_data(symbol, period='6mo', interval='1d')
        
        if data is None or data.empty:
            return None
        
        # Train model (in production, use pre-trained models)
        model_result, error = train_ml_model(symbol, model_type, horizon)
        
        if error:
            return None
        
        model_info = model_result
        model = model_info['model']
        scaler = model_info['scaler']
        
        # Prepare latest features
        features, _ = prepare_features(data, symbol)
        
        if features is None or features.empty:
            return None
        
        # Get latest feature values
        latest_features = features.iloc[-1:].values
        latest_features_scaled = scaler.transform(latest_features)
        
        # Make prediction
        predicted_return = model.predict(latest_features_scaled)[0]
        current_price = data['Close'].iloc[-1]
        predicted_price = current_price * (1 + predicted_return)
        
        # Determine confidence based on model accuracy
        confidence_score = model_info['directional_accuracy']
        
        if confidence_score >= 90:
            confidence = 'VERY_HIGH'
        elif confidence_score >= 80:
            confidence = 'HIGH'
        elif confidence_score >= 70:
            confidence = 'MEDIUM'
        elif confidence_score >= 60:
            confidence = 'LOW'
        else:
            confidence = 'VERY_LOW'
        
        # Determine trend
        if predicted_return > 0.02:
            trend = 'STRONG_UP'
        elif predicted_return > 0.005:
            trend = 'UP'
        elif predicted_return < -0.02:
            trend = 'STRONG_DOWN'
        elif predicted_return < -0.005:
            trend = 'DOWN'
        else:
            trend = 'SIDEWAYS'
        
        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'predicted_price': float(predicted_price),
            'predicted_return': float(predicted_return),
            'predicted_trend': trend,
            'confidence': confidence,
            'confidence_score': float(confidence_score),
            'model_type': model_type,
            'horizon': horizon,
            'feature_importance': dict(zip(
                model_info['feature_names'],
                model_info['feature_importance']
            )) if model_info['feature_importance'] is not None else {},
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating prediction for {symbol}: {str(e)}")
        return None

# API Endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def get_ml_prediction(request, symbol):
    """Get ML prediction for a specific symbol"""
    try:
        model_type = request.GET.get('model_type', 'RF')
        horizon = request.GET.get('horizon', '1D')
        
        prediction = generate_prediction(symbol, model_type, horizon)
        
        if prediction is None:
            return Response(
                {'error': f'Failed to generate prediction for {symbol}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(prediction)
        
    except Exception as e:
        logger.error(f"Error in get_ml_prediction for {symbol}: {str(e)}")
        return Response(
            {'error': f'Failed to get prediction for {symbol}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_trading_signals(request):
    """Get trading signals for multiple stocks"""
    try:
        # Default symbols to analyze
        symbols = request.GET.get('symbols', '').split(',') if request.GET.get('symbols') else [
            'AAPL', 'MSFT', 'GOOGL', 'TSLA', '2222.SR', '1120.SR', 'BTC-USD', 'ETH-USD'
        ]
        
        signals = []
        
        for symbol in symbols[:10]:  # Limit to 10 symbols to avoid timeout
            try:
                prediction = generate_prediction(symbol.strip())
                if prediction:
                    signals.append(prediction)
            except Exception as e:
                logger.warning(f"Failed to get signal for {symbol}: {str(e)}")
                continue
        
        return Response({
            'timestamp': datetime.now().isoformat(),
            'signals': signals,
            'total_signals': len(signals)
        })
        
    except Exception as e:
        logger.error(f"Error in get_trading_signals: {str(e)}")
        return Response(
            {'error': 'Failed to generate trading signals'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def train_model_api(request):
    """Train a new ML model via API"""
    try:
        symbol = request.data.get('symbol')
        model_type = request.data.get('model_type', 'RF')
        
        if not symbol:
            return Response(
                {'error': 'Symbol is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Train model
        model_result, error = train_ml_model(symbol, model_type)
        
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': f'Model trained successfully for {symbol}',
            'model_type': model_type,
            'train_score': model_result['train_score'],
            'test_score': model_result['test_score'],
            'directional_accuracy': model_result['directional_accuracy'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in train_model_api: {str(e)}")
        return Response(
            {'error': 'Failed to train model'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_model_performance(request):
    """Get performance metrics for all ML models"""
    try:
        models = MLModel.objects.filter(is_active=True)
        
        performance_data = []
        
        for model in models:
            recent_predictions = model.predictions.filter(
                status='VALIDATED',
                validated_at__gte=datetime.now() - timedelta(days=30)
            )
            
            if recent_predictions.exists():
                avg_accuracy = recent_predictions.aggregate(
                    avg=models.Avg('accuracy_percentage')
                )['avg'] or 0
                
                total_predictions = recent_predictions.count()
                accurate_predictions = recent_predictions.filter(is_accurate=True).count()
                
                performance_data.append({
                    'model_id': model.id,
                    'model_name': model.name,
                    'model_type': model.model_type,
                    'prediction_type': model.prediction_type,
                    'accuracy': float(model.accuracy or 0),
                    'recent_accuracy': float(avg_accuracy),
                    'total_predictions': total_predictions,
                    'accurate_predictions': accurate_predictions,
                    'created_at': model.created_at.isoformat()
                })
        
        return Response({
            'timestamp': datetime.now().isoformat(),
            'models': performance_data,
            'total_models': len(performance_data)
        })
        
    except Exception as e:
        logger.error(f"Error in get_model_performance: {str(e)}")
        return Response(
            {'error': 'Failed to get model performance'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_market_analysis(request):
    """Get comprehensive market analysis using ML"""
    try:
        # Analyze different market segments
        markets = {
            'TASI': ['2222.SR', '1120.SR', '2030.SR'],
            'USA': ['AAPL', 'MSFT', 'GOOGL', 'TSLA'],
            'CRYPTO': ['BTC-USD', 'ETH-USD', 'BNB-USD']
        }
        
        market_analysis = {}
        
        for market_name, symbols in markets.items():
            market_signals = []
            
            for symbol in symbols:
                prediction = generate_prediction(symbol)
                if prediction:
                    market_signals.append(prediction)
            
            if market_signals:
                # Calculate market sentiment
                bullish_signals = sum(1 for s in market_signals if s['predicted_trend'] in ['UP', 'STRONG_UP'])
                bearish_signals = sum(1 for s in market_signals if s['predicted_trend'] in ['DOWN', 'STRONG_DOWN'])
                neutral_signals = len(market_signals) - bullish_signals - bearish_signals
                
                avg_confidence = np.mean([s['confidence_score'] for s in market_signals])
                avg_return = np.mean([s['predicted_return'] for s in market_signals])
                
                market_analysis[market_name] = {
                    'total_signals': len(market_signals),
                    'bullish_signals': bullish_signals,
                    'bearish_signals': bearish_signals,
                    'neutral_signals': neutral_signals,
                    'sentiment': 'BULLISH' if bullish_signals > bearish_signals else 'BEARISH' if bearish_signals > bullish_signals else 'NEUTRAL',
                    'avg_confidence': float(avg_confidence),
                    'avg_predicted_return': float(avg_return),
                    'signals': market_signals
                }
        
        return Response({
            'timestamp': datetime.now().isoformat(),
            'market_analysis': market_analysis
        })
        
    except Exception as e:
        logger.error(f"Error in get_market_analysis: {str(e)}")
        return Response(
            {'error': 'Failed to generate market analysis'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )