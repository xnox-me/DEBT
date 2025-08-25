#!/usr/bin/env python3
"""
DEBT Sophisticated ML Pipeline
Advanced machine learning pipeline with MLflow tracking, business intelligence,
and comprehensive model management for financial and business predictions.
"""

import os
import sys
import pickle
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional, Any

# ML and Data Science
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression, ElasticNet
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import xgboost as xgb
import lightgbm as lgb

# MLflow for experiment tracking
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.lightgbm
from mlflow.tracking import MlflowClient

# Financial data
import yfinance as yf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessMLPipeline:
    """Comprehensive ML pipeline for business intelligence and financial predictions."""
    
    def __init__(self, experiment_name: str = "DEBT_Business_Intelligence"):
        """Initialize the ML pipeline with MLflow tracking."""
        
        # Set up MLflow
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        self.client = MlflowClient()
        
        # Initialize model registry
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # Business model configurations
        self.model_configs = {
            'stock_prediction': {
                'type': 'regression',
                'models': ['random_forest', 'xgboost', 'lightgbm', 'linear_regression'],
                'metrics': ['mse', 'r2', 'mae']
            },
            'customer_churn': {
                'type': 'classification',
                'models': ['random_forest', 'xgboost', 'logistic_regression'],
                'metrics': ['accuracy', 'precision', 'recall', 'f1']
            },
            'sales_forecasting': {
                'type': 'regression',
                'models': ['gradient_boosting', 'xgboost', 'random_forest'],
                'metrics': ['mse', 'mape', 'r2']
            },
            'risk_assessment': {
                'type': 'classification',
                'models': ['svm', 'random_forest', 'xgboost'],
                'metrics': ['accuracy', 'roc_auc', 'precision']
            }
        }
        
        logger.info(f"Initialized BusinessMLPipeline with experiment: {experiment_name}")
    
    def create_stock_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive features for stock prediction."""
        
        features_df = df.copy()
        
        # Price-based features
        features_df['returns'] = features_df['Close'].pct_change()
        features_df['log_returns'] = np.log(features_df['Close'] / features_df['Close'].shift(1))
        features_df['high_low_pct'] = (features_df['High'] - features_df['Low']) / features_df['Close']
        features_df['open_close_pct'] = (features_df['Close'] - features_df['Open']) / features_df['Open']
        
        # Technical indicators
        # Moving averages
        for window in [5, 10, 20, 50]:
            features_df[f'sma_{window}'] = features_df['Close'].rolling(window).mean()
            features_df[f'ema_{window}'] = features_df['Close'].ewm(span=window).mean()
            features_df[f'price_to_sma_{window}'] = features_df['Close'] / features_df[f'sma_{window}']
        
        # Volatility measures
        features_df['volatility_10'] = features_df['returns'].rolling(10).std()
        features_df['volatility_30'] = features_df['returns'].rolling(30).std()
        
        # Volume indicators
        features_df['volume_sma_10'] = features_df['Volume'].rolling(10).mean()
        features_df['volume_ratio'] = features_df['Volume'] / features_df['volume_sma_10']
        
        # RSI
        delta = features_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features_df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = features_df['Close'].ewm(span=12).mean()
        ema_26 = features_df['Close'].ewm(span=26).mean()
        features_df['macd'] = ema_12 - ema_26
        features_df['macd_signal'] = features_df['macd'].ewm(span=9).mean()
        
        # Lagged features
        for lag in [1, 2, 3, 5, 10]:
            features_df[f'close_lag_{lag}'] = features_df['Close'].shift(lag)
            features_df[f'volume_lag_{lag}'] = features_df['Volume'].shift(lag)
            features_df[f'returns_lag_{lag}'] = features_df['returns'].shift(lag)
        
        # Time-based features
        features_df['day_of_week'] = features_df.index.dayofweek
        features_df['month'] = features_df.index.month
        features_df['quarter'] = features_df.index.quarter
        
        return features_df
    
    def prepare_stock_data(self, symbol: str, period: str = "2y") -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare stock data for ML training."""
        
        logger.info(f"Preparing data for {symbol}")
        
        # Fetch stock data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Create features
        features_df = self.create_stock_features(df)
        
        # Select feature columns (excluding target and non-numeric)
        feature_cols = [col for col in features_df.columns if col not in [
            'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'
        ]]
        
        # Remove non-numeric columns
        numeric_cols = features_df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        # Prepare data
        X = features_df[numeric_cols].dropna()
        y = features_df.loc[X.index, 'Close'].shift(-1).dropna()  # Predict next day's close
        
        # Align X and y
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len].values
        y = y.iloc[:min_len].values
        
        return X, y, numeric_cols
    
    def train_regression_models(self, X: np.ndarray, y: np.ndarray, 
                               feature_names: List[str], task_name: str) -> Dict[str, Any]:
        """Train multiple regression models and track with MLflow."""
        
        results = {}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[task_name] = scaler
        
        # Define models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBRegressor(random_state=42),
            'lightgbm': lgb.LGBMRegressor(random_state=42, verbose=-1),
            'linear_regression': LinearRegression(),
            'gradient_boosting': GradientBoostingRegressor(random_state=42),
            'elastic_net': ElasticNet(random_state=42)
        }
        
        # Train and evaluate each model
        for model_name, model in models.items():
            with mlflow.start_run(run_name=f"{task_name}_{model_name}"):
                
                logger.info(f"Training {model_name} for {task_name}")
                
                # Use scaled data for linear models
                if model_name in ['linear_regression', 'elastic_net']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                mae = np.mean(np.abs(y_test - y_pred))
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()
                
                # Log parameters and metrics
                mlflow.log_params({
                    'model_type': model_name,
                    'task_name': task_name,
                    'n_features': X_train.shape[1],
                    'train_size': X_train.shape[0],
                    'test_size': X_test.shape[0]
                })
                
                mlflow.log_metrics({
                    'mse': mse,
                    'rmse': rmse,
                    'r2_score': r2,
                    'mae': mae,
                    'cv_r2_mean': cv_mean,
                    'cv_r2_std': cv_std
                })
                
                # Log model
                if model_name == 'xgboost':
                    mlflow.xgboost.log_model(model, "model")
                elif model_name == 'lightgbm':
                    mlflow.lightgbm.log_model(model, "model")
                else:
                    mlflow.sklearn.log_model(model, "model")
                
                # Store results
                results[model_name] = {
                    'model': model,
                    'metrics': {
                        'mse': mse,
                        'rmse': rmse,
                        'r2_score': r2,
                        'mae': mae,
                        'cv_r2_mean': cv_mean,
                        'cv_r2_std': cv_std
                    },
                    'predictions': y_pred,
                    'run_id': mlflow.active_run().info.run_id
                }
        
        # Find best model
        best_model_name = min(results.keys(), key=lambda k: results[k]['metrics']['mse'])
        best_model = results[best_model_name]['model']
        
        self.models[task_name] = {
            'best_model': best_model,
            'best_model_name': best_model_name,
            'all_results': results,
            'feature_names': feature_names,
            'scaler': scaler
        }
        
        logger.info(f"Best model for {task_name}: {best_model_name} (R² = {results[best_model_name]['metrics']['r2_score']:.4f})")
        
        return results
    
    def generate_synthetic_business_data(self) -> pd.DataFrame:
        """Generate synthetic business data for demonstration."""
        
        np.random.seed(42)
        n_samples = 1000
        
        # Customer data
        data = {
            'customer_age': np.random.normal(40, 15, n_samples).clip(18, 80),
            'income': np.random.lognormal(10.5, 0.5, n_samples).clip(20000, 200000),
            'credit_score': np.random.normal(650, 100, n_samples).clip(300, 850),
            'months_as_customer': np.random.poisson(24, n_samples),
            'num_products': np.random.poisson(2, n_samples).clip(1, 5),
            'monthly_charges': np.random.normal(75, 25, n_samples).clip(20, 200),
            'total_charges': None,  # Will be calculated
            'satisfaction_score': np.random.normal(7, 2, n_samples).clip(1, 10),
            'support_tickets': np.random.poisson(1.5, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Calculate total charges
        df['total_charges'] = df['monthly_charges'] * df['months_as_customer']
        
        # Create churn probability based on business logic
        churn_prob = (
            -0.1 * (df['satisfaction_score'] - 5) / 5 +
            0.15 * (df['support_tickets'] - 1) / 3 +
            0.05 * (df['monthly_charges'] - 75) / 50 +
            -0.08 * (df['months_as_customer'] - 24) / 24 +
            np.random.normal(0, 0.1, n_samples)
        ).clip(0, 1)
        
        df['churn'] = (churn_prob > 0.3).astype(int)
        
        # Sales data
        df['monthly_sales'] = (
            df['num_products'] * 50 +
            df['income'] * 0.001 +
            df['satisfaction_score'] * 10 +
            np.random.normal(0, 20, n_samples)
        ).clip(0, None)
        
        return df
    
    def train_business_models(self) -> Dict[str, Any]:
        """Train comprehensive business intelligence models."""
        
        logger.info("Training business intelligence models")
        
        # Generate business data
        business_data = self.generate_synthetic_business_data()
        
        results = {}
        
        # 1. Customer Churn Prediction
        logger.info("Training customer churn prediction model")
        
        churn_features = ['customer_age', 'income', 'credit_score', 'months_as_customer',
                         'num_products', 'monthly_charges', 'total_charges', 
                         'satisfaction_score', 'support_tickets']
        
        X_churn = business_data[churn_features].values
        y_churn = business_data['churn'].values
        
        # Train classification models
        churn_results = self.train_classification_models(
            X_churn, y_churn, churn_features, 'customer_churn'
        )
        results['customer_churn'] = churn_results
        
        # 2. Sales Forecasting
        logger.info("Training sales forecasting model")
        
        sales_features = ['customer_age', 'income', 'num_products', 'satisfaction_score', 'months_as_customer']
        X_sales = business_data[sales_features].values
        y_sales = business_data['monthly_sales'].values
        
        sales_results = self.train_regression_models(
            X_sales, y_sales, sales_features, 'sales_forecasting'
        )
        results['sales_forecasting'] = sales_results
        
        return results
    
    def train_classification_models(self, X: np.ndarray, y: np.ndarray, 
                                  feature_names: List[str], task_name: str) -> Dict[str, Any]:
        """Train classification models with MLflow tracking."""
        
        results = {}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[task_name] = scaler
        
        # Define models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'svm': SVC(random_state=42, probability=True)
        }
        
        # Train and evaluate each model
        for model_name, model in models.items():
            with mlflow.start_run(run_name=f"{task_name}_{model_name}"):
                
                logger.info(f"Training {model_name} for {task_name}")
                
                # Use scaled data for linear models
                if model_name in ['logistic_regression', 'svm']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    y_prob = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                
                from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                # ROC AUC if probabilities available
                roc_auc = roc_auc_score(y_test, y_prob) if y_prob is not None else None
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()
                
                # Log parameters and metrics
                mlflow.log_params({
                    'model_type': model_name,
                    'task_name': task_name,
                    'n_features': X_train.shape[1],
                    'train_size': X_train.shape[0],
                    'test_size': X_test.shape[0]
                })
                
                metrics_to_log = {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'cv_accuracy_mean': cv_mean,
                    'cv_accuracy_std': cv_std
                }
                
                if roc_auc is not None:
                    metrics_to_log['roc_auc'] = roc_auc
                
                mlflow.log_metrics(metrics_to_log)
                
                # Log model
                if model_name == 'xgboost':
                    mlflow.xgboost.log_model(model, "model")
                else:
                    mlflow.sklearn.log_model(model, "model")
                
                # Store results
                results[model_name] = {
                    'model': model,
                    'metrics': metrics_to_log,
                    'predictions': y_pred,
                    'probabilities': y_prob,
                    'run_id': mlflow.active_run().info.run_id
                }
        
        # Find best model based on F1 score
        best_model_name = max(results.keys(), key=lambda k: results[k]['metrics']['f1_score'])
        best_model = results[best_model_name]['model']
        
        self.models[task_name] = {
            'best_model': best_model,
            'best_model_name': best_model_name,
            'all_results': results,
            'feature_names': feature_names,
            'scaler': scaler
        }
        
        logger.info(f"Best model for {task_name}: {best_model_name} (F1 = {results[best_model_name]['metrics']['f1_score']:.4f})")
        
        return results
    
    def predict(self, task_name: str, features: np.ndarray) -> Dict[str, Any]:
        """Make predictions using trained models."""
        
        if task_name not in self.models:
            raise ValueError(f"No trained model found for task: {task_name}")
        
        model_info = self.models[task_name]
        model = model_info['best_model']
        scaler = model_info['scaler']
        
        # Scale features if needed
        model_name = model_info['best_model_name']
        if model_name in ['linear_regression', 'elastic_net', 'logistic_regression', 'svm']:
            features_scaled = scaler.transform(features.reshape(1, -1))
            prediction = model.predict(features_scaled)
        else:
            prediction = model.predict(features.reshape(1, -1))
        
        # Get probability for classification tasks
        probability = None
        if hasattr(model, 'predict_proba'):
            if model_name in ['logistic_regression', 'svm']:
                probability = model.predict_proba(features_scaled)[0]
            else:
                probability = model.predict_proba(features.reshape(1, -1))[0]
        
        return {
            'prediction': prediction[0],
            'probability': probability,
            'model_name': model_name,
            'task_name': task_name
        }
    
    def save_models(self, save_dir: str = "models") -> None:
        """Save all trained models to disk."""
        
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        for task_name, model_info in self.models.items():
            task_dir = save_path / task_name
            task_dir.mkdir(exist_ok=True)
            
            # Save best model
            joblib.dump(model_info['best_model'], task_dir / f"best_model_{model_info['best_model_name']}.pkl")
            
            # Save scaler
            joblib.dump(model_info['scaler'], task_dir / "scaler.pkl")
            
            # Save metadata
            metadata = {
                'best_model_name': model_info['best_model_name'],
                'feature_names': model_info['feature_names'],
                'task_type': self.model_configs.get(task_name, {}).get('type', 'unknown')
            }
            
            with open(task_dir / "metadata.json", 'w') as f:
                import json
                json.dump(metadata, f, indent=2)
        
        logger.info(f"Models saved to {save_path}")
    
    def load_models(self, load_dir: str = "models") -> None:
        """Load trained models from disk."""
        
        load_path = Path(load_dir)
        if not load_path.exists():
            raise FileNotFoundError(f"Models directory not found: {load_path}")
        
        for task_dir in load_path.iterdir():
            if task_dir.is_dir():
                task_name = task_dir.name
                
                # Load metadata
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        import json
                        metadata = json.load(f)
                    
                    # Load best model
                    model_file = task_dir / f"best_model_{metadata['best_model_name']}.pkl"
                    if model_file.exists():
                        best_model = joblib.load(model_file)
                        
                        # Load scaler
                        scaler_file = task_dir / "scaler.pkl"
                        scaler = joblib.load(scaler_file) if scaler_file.exists() else None
                        
                        self.models[task_name] = {
                            'best_model': best_model,
                            'best_model_name': metadata['best_model_name'],
                            'feature_names': metadata['feature_names'],
                            'scaler': scaler
                        }
        
        logger.info(f"Loaded {len(self.models)} models from {load_path}")

def main():
    """Main execution function for ML pipeline demonstration."""
    
    print("🤖 DEBT Sophisticated ML Pipeline")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = BusinessMLPipeline("DEBT_Sophisticated_Example")
    
    # Train business models
    print("\n📊 Training Business Intelligence Models...")
    business_results = pipeline.train_business_models()
    
    # Train stock prediction model
    print("\n📈 Training Stock Prediction Model...")
    try:
        X_stock, y_stock, feature_names = pipeline.prepare_stock_data("AAPL", "1y")
        stock_results = pipeline.train_regression_models(X_stock, y_stock, feature_names, "stock_prediction")
    except Exception as e:
        print(f"❌ Stock prediction training failed: {e}")
        stock_results = None
    
    # Save models
    print("\n💾 Saving Models...")
    pipeline.save_models("sophisticated_example/ml_pipeline/models")
    
    # Print summary
    print("\n📋 Training Summary:")
    print("-" * 30)
    
    for task_name, results in business_results.items():
        best_model = min(results.keys(), key=lambda k: results[k]['metrics'].get('mse', float('inf')))
        if 'f1_score' in results[best_model]['metrics']:
            score = results[best_model]['metrics']['f1_score']
            print(f"  {task_name}: {best_model} (F1: {score:.4f})")
        else:
            score = results[best_model]['metrics']['r2_score']
            print(f"  {task_name}: {best_model} (R²: {score:.4f})")
    
    if stock_results:
        best_stock_model = min(stock_results.keys(), key=lambda k: stock_results[k]['metrics']['mse'])
        r2_score = stock_results[best_stock_model]['metrics']['r2_score']
        print(f"  stock_prediction: {best_stock_model} (R²: {r2_score:.4f})")
    
    print("\n✅ ML Pipeline Training Complete!")
    print(f"🔬 View experiments at: http://localhost:5000")

if __name__ == "__main__":
    main()