from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MLModel, Prediction, TradingStrategy, BacktestResult, ModelTraining, PredictionDashboard
from markets.models import Stock, Market

class MLModelSerializer(serializers.ModelSerializer):
    predictions_count = serializers.SerializerMethodField()
    recent_accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = MLModel
        fields = ['id', 'name', 'model_type', 'prediction_type', 'description',
                 'accuracy', 'precision', 'recall', 'f1_score', 'parameters',
                 'training_data_period', 'is_active', 'created_at', 'updated_at',
                 'predictions_count', 'recent_accuracy']
    
    def get_predictions_count(self, obj):
        return obj.predictions.count()
    
    def get_recent_accuracy(self, obj):
        from datetime import datetime, timedelta
        recent_predictions = obj.predictions.filter(
            validated_at__gte=datetime.now() - timedelta(days=30),
            is_accurate__isnull=False
        )
        if recent_predictions.exists():
            accurate_count = recent_predictions.filter(is_accurate=True).count()
            return (accurate_count / recent_predictions.count()) * 100
        return None

class PredictionSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_type = serializers.CharField(source='model.model_type', read_only=True)
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    market_code = serializers.CharField(source='stock.market.code', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Prediction
        fields = ['id', 'model_name', 'model_type', 'stock_symbol', 'stock_name',
                 'market_code', 'predicted_price', 'predicted_trend', 'predicted_volatility',
                 'confidence', 'confidence_score', 'probability_up', 'probability_down',
                 'prediction_horizon', 'target_date', 'input_features', 'feature_importance',
                 'actual_price', 'actual_trend', 'is_accurate', 'accuracy_percentage',
                 'status', 'time_remaining', 'created_at', 'validated_at']
    
    def get_time_remaining(self, obj):
        from datetime import datetime
        if obj.target_date:
            delta = obj.target_date - datetime.now(obj.target_date.tzinfo)
            if delta.total_seconds() > 0:
                return {
                    'days': delta.days,
                    'hours': delta.seconds // 3600,
                    'total_hours': delta.total_seconds() / 3600
                }
        return None

class TradingStrategySerializer(serializers.ModelSerializer):
    models_used_names = serializers.SerializerMethodField()
    markets_names = serializers.SerializerMethodField()
    backtest_count = serializers.SerializerMethodField()
    best_backtest = serializers.SerializerMethodField()
    
    class Meta:
        model = TradingStrategy
        fields = ['id', 'name', 'strategy_type', 'description', 'entry_conditions',
                 'exit_conditions', 'risk_management', 'total_return', 'sharpe_ratio',
                 'max_drawdown', 'win_rate', 'models_used_names', 'markets_names',
                 'backtest_count', 'best_backtest', 'is_active', 'created_at', 'updated_at']
    
    def get_models_used_names(self, obj):
        return [model.name for model in obj.models_used.all()]
    
    def get_markets_names(self, obj):
        return [market.name for market in obj.markets.all()]
    
    def get_backtest_count(self, obj):
        return obj.backtest_results.count()
    
    def get_best_backtest(self, obj):
        best = obj.backtest_results.order_by('-sharpe_ratio').first()
        if best:
            return {
                'id': best.id,
                'period': f"{best.start_date} to {best.end_date}",
                'total_return': float(best.total_return),
                'sharpe_ratio': float(best.sharpe_ratio),
                'max_drawdown': float(best.max_drawdown)
            }
        return None

class BacktestResultSerializer(serializers.ModelSerializer):
    strategy_name = serializers.CharField(source='strategy.name', read_only=True)
    strategy_type = serializers.CharField(source='strategy.strategy_type', read_only=True)
    test_duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = BacktestResult
        fields = ['id', 'strategy_name', 'strategy_type', 'start_date', 'end_date',
                 'initial_capital', 'final_capital', 'total_return', 'annualized_return',
                 'volatility', 'sharpe_ratio', 'max_drawdown', 'total_trades',
                 'winning_trades', 'losing_trades', 'win_rate', 'avg_win', 'avg_loss',
                 'profit_factor', 'test_duration_days', 'created_at']
    
    def get_test_duration_days(self, obj):
        return (obj.end_date - obj.start_date).days

class ModelTrainingSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    training_duration = serializers.SerializerMethodField()
    data_quality_score = serializers.SerializerMethodField()
    
    class Meta:
        model = ModelTraining
        fields = ['id', 'model_name', 'training_data_start', 'training_data_end',
                 'validation_split', 'hyperparameters', 'feature_columns', 'target_column',
                 'training_accuracy', 'validation_accuracy', 'training_loss', 'validation_loss',
                 'training_time_seconds', 'data_points_used', 'feature_importance',
                 'status', 'error_message', 'training_duration', 'data_quality_score',
                 'started_at', 'completed_at']
    
    def get_training_duration(self, obj):
        if obj.completed_at and obj.started_at:
            delta = obj.completed_at - obj.started_at
            return {
                'seconds': delta.total_seconds(),
                'formatted': str(delta)
            }
        return None
    
    def get_data_quality_score(self, obj):
        # Simple data quality score based on data points and validation accuracy
        if obj.data_points_used and obj.validation_accuracy:
            data_score = min(100, (obj.data_points_used / 1000) * 50)  # More data = better
            accuracy_score = float(obj.validation_accuracy)
            return (data_score + accuracy_score) / 2
        return None

class PredictionDashboardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    models_count = serializers.SerializerMethodField()
    stocks_count = serializers.SerializerMethodField()
    models_display = serializers.SerializerMethodField()
    stocks_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionDashboard
        fields = ['id', 'name', 'description', 'models_count', 'stocks_count',
                 'models_display', 'stocks_display', 'prediction_types', 'time_horizons',
                 'layout_config', 'refresh_interval', 'is_public', 'is_default',
                 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user']
    
    def get_models_count(self, obj):
        return obj.models_displayed.count()
    
    def get_stocks_count(self, obj):
        return obj.stocks_tracked.count()
    
    def get_models_display(self, obj):
        return [
            {
                'id': model.id,
                'name': model.name,
                'model_type': model.model_type,
                'accuracy': float(model.accuracy or 0)
            }
            for model in obj.models_displayed.all()
        ]
    
    def get_stocks_display(self, obj):
        return [
            {
                'id': stock.id,
                'symbol': stock.symbol,
                'name': stock.name,
                'market': stock.market.code
            }
            for stock in obj.stocks_tracked.all()
        ]

class MLPredictionSummarySerializer(serializers.Serializer):
    """Serializer for ML prediction summary data"""
    symbol = serializers.CharField()
    current_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    predicted_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    predicted_return = serializers.DecimalField(max_digits=8, decimal_places=4)
    predicted_trend = serializers.CharField()
    confidence = serializers.CharField()
    confidence_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    model_type = serializers.CharField()
    horizon = serializers.CharField()
    feature_importance = serializers.DictField()
    timestamp = serializers.DateTimeField()

class TradingSignalSerializer(serializers.Serializer):
    """Serializer for trading signal data"""
    symbol = serializers.CharField()
    signal_type = serializers.CharField()
    confidence = serializers.CharField()
    confidence_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    predicted_price = serializers.DecimalField(max_digits=15, decimal_places=4)
    target_price = serializers.DecimalField(max_digits=15, decimal_places=4, required=False)
    stop_loss = serializers.DecimalField(max_digits=15, decimal_places=4, required=False)
    time_horizon = serializers.CharField()
    reasoning = serializers.ListField(child=serializers.CharField())
    model_consensus = serializers.DictField()
    timestamp = serializers.DateTimeField()

class MarketAnalysisSerializer(serializers.Serializer):
    """Serializer for comprehensive market analysis"""
    market_name = serializers.CharField()
    total_signals = serializers.IntegerField()
    bullish_signals = serializers.IntegerField()
    bearish_signals = serializers.IntegerField()
    neutral_signals = serializers.IntegerField()
    sentiment = serializers.CharField()
    avg_confidence = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_predicted_return = serializers.DecimalField(max_digits=8, decimal_places=4)
    signals = MLPredictionSummarySerializer(many=True)

class ModelPerformanceSerializer(serializers.Serializer):
    """Serializer for model performance metrics"""
    model_id = serializers.IntegerField()
    model_name = serializers.CharField()
    model_type = serializers.CharField()
    prediction_type = serializers.CharField()
    accuracy = serializers.DecimalField(max_digits=5, decimal_places=2)
    recent_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_predictions = serializers.IntegerField()
    accurate_predictions = serializers.IntegerField()
    created_at = serializers.DateTimeField()