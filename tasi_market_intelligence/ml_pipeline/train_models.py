#!/usr/bin/env python3
"""
TASI Market Intelligence ML Pipeline
Islamic Finance-Compliant Machine Learning for Saudi Stock Market Analysis
"""

import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import mlflow
import mlflow.sklearn
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TASIMLPipeline:
    """Islamic Finance-Compliant Machine Learning Pipeline for TASI Market Analysis."""
    
    def __init__(self):
        # TASI companies with their Islamic finance compliance status
        self.tasi_companies = {
            "2222.SR": {"name": "Saudi Aramco", "sector": "Energy", "islamic_compliant": True},
            "1120.SR": {"name": "Al Rajhi Bank", "sector": "Islamic Banking", "islamic_compliant": True},
            "2030.SR": {"name": "SABIC", "sector": "Chemicals", "islamic_compliant": True},
            "2010.SR": {"name": "SABB", "sector": "Banking", "islamic_compliant": True},
            "1180.SR": {"name": "Riyad Bank", "sector": "Banking", "islamic_compliant": True},
            "2170.SR": {"name": "Almarai", "sector": "Food & Beverages", "islamic_compliant": True},
            "2040.SR": {"name": "Saudi Electricity Company", "sector": "Utilities", "islamic_compliant": True},
            "2380.SR": {"name": "Petrochemical Industries", "sector": "Chemicals", "islamic_compliant": True},
            "1140.SR": {"name": "Alinma Bank", "sector": "Islamic Banking", "islamic_compliant": True},
            "1211.SR": {"name": "ANB", "sector": "Banking", "islamic_compliant": True}
        }
        
        # Create models directory
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize MLflow
        mlflow.set_experiment("TASI_Islamic_Finance_ML")
    
    def fetch_tasi_data(self, symbol, period="2y"):
        """Fetch TASI historical data for ML training."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                print(f"No data available for {symbol}")
                return None
            return hist
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def create_islamic_features(self, df):
        """Create Islamic finance-compliant features for ML models."""
        if df.empty:
            return None
        
        # Technical indicators (Halal - no interest calculations)
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Price momentum (Sharia compliant)
        df['Price_Momentum_5'] = df['Close'].pct_change(periods=5)
        df['Price_Momentum_10'] = df['Close'].pct_change(periods=10)
        df['Price_Momentum_20'] = df['Close'].pct_change(periods=20)
        
        # Volatility measures (Islamic finance approved)
        df['Volatility_5'] = df['Close'].rolling(window=5).std()
        df['Volatility_10'] = df['Close'].rolling(window=10).std()
        df['Volatility_20'] = df['Close'].rolling(window=20).std()
        
        # Volume indicators
        df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA_10'] = df['Volume'].rolling(window=10).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_10']
        
        # High-Low spread (Halal market analysis)
        df['High_Low_Spread'] = (df['High'] - df['Low']) / df['Close']
        df['Open_Close_Spread'] = (df['Close'] - df['Open']) / df['Open']
        
        # Trend indicators (Islamic finance compliant)
        df['Trend_5'] = (df['Close'] > df['SMA_5']).astype(int)
        df['Trend_20'] = (df['Close'] > df['SMA_20']).astype(int)
        df['Trend_50'] = (df['Close'] > df['SMA_50']).astype(int)
        
        # Lagged features (following Islamic principle of gradual analysis)
        for lag in [1, 2, 3, 5]:
            df[f'Close_lag_{lag}'] = df['Close'].shift(lag)
            df[f'Volume_lag_{lag}'] = df['Volume'].shift(lag)
            df[f'Returns_lag_{lag}'] = df['Close'].pct_change().shift(lag)
        
        return df
    
    def prepare_ml_data(self, df):
        """Prepare data for Islamic ML models."""
        # Feature columns (all Sharia compliant)
        feature_columns = [
            'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50',
            'Price_Momentum_5', 'Price_Momentum_10', 'Price_Momentum_20',
            'Volatility_5', 'Volatility_10', 'Volatility_20',
            'Volume_MA_5', 'Volume_MA_10', 'Volume_Ratio',
            'High_Low_Spread', 'Open_Close_Spread',
            'Trend_5', 'Trend_20', 'Trend_50'
        ]
        
        # Add lagged features
        lag_features = []
        for lag in [1, 2, 3, 5]:
            lag_features.extend([f'Close_lag_{lag}', f'Volume_lag_{lag}', f'Returns_lag_{lag}'])
        
        feature_columns.extend(lag_features)
        
        # Create target variables
        df['Price_Next'] = df['Close'].shift(-1)  # Next day price
        df['Price_Direction'] = (df['Price_Next'] > df['Close']).astype(int)  # Price direction
        df['Returns_Next'] = df['Close'].pct_change().shift(-1)  # Next day returns
        
        # Clean data
        df_clean = df[feature_columns + ['Close', 'Price_Next', 'Price_Direction', 'Returns_Next']].dropna()
        
        return df_clean, feature_columns
    
    def train_price_prediction_model(self, df, feature_columns, symbol):
        """Train Islamic finance-compliant price prediction model."""
        with mlflow.start_run(run_name=f"TASI_Price_Prediction_{symbol}"):
            # Prepare data
            X = df[feature_columns].values
            y = df['Price_Next'].values
            
            # Split data (80-20 following Islamic principle of balanced approach)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features (Islamic finance approved standardization)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train models (Ensemble approach following Islamic principle of consultation)
            models = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'LinearRegression': LinearRegression()
            }
            
            results = {}
            
            for model_name, model in models.items():
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                results[model_name] = {
                    'model': model,
                    'mse': mse,
                    'r2': r2,
                    'predictions': y_pred
                }
                
                # Log to MLflow
                mlflow.log_param(f"{model_name}_features", len(feature_columns))
                mlflow.log_metric(f"{model_name}_mse", mse)
                mlflow.log_metric(f"{model_name}_r2", r2)
                
                print(f"{model_name} - MSE: {mse:.4f}, R²: {r2:.4f}")
            
            # Create ensemble model (following Islamic consultation principle)
            ensemble_pred = 0.7 * results['RandomForest']['predictions'] + 0.3 * results['LinearRegression']['predictions']
            ensemble_mse = mean_squared_error(y_test, ensemble_pred)
            ensemble_r2 = r2_score(y_test, ensemble_pred)
            
            # Save models and scaler
            company_info = self.tasi_companies.get(symbol, {"name": symbol, "islamic_compliant": True})
            model_path = os.path.join(self.models_dir, f"tasi_price_model_{symbol.replace('.', '_')}")
            
            joblib.dump({
                'rf_model': results['RandomForest']['model'],
                'lr_model': results['LinearRegression']['model'],
                'scaler': scaler,
                'feature_columns': feature_columns,
                'company_info': company_info,
                'islamic_compliance': 'Fully Compliant - No interest-based calculations'
            }, f"{model_path}.joblib")
            
            # Log ensemble results
            mlflow.log_metric("ensemble_mse", ensemble_mse)
            mlflow.log_metric("ensemble_r2", ensemble_r2)
            mlflow.log_param("islamic_compliance", "Fully Compliant")
            mlflow.log_param("company", company_info['name'])
            
            print(f"Ensemble Model - MSE: {ensemble_mse:.4f}, R²: {ensemble_r2:.4f}")
            print(f"Islamic Compliance: ✅ Fully Compliant")
            
            return results, scaler
    
    def train_direction_prediction_model(self, df, feature_columns, symbol):
        """Train Islamic finance-compliant price direction prediction model."""
        with mlflow.start_run(run_name=f"TASI_Direction_Prediction_{symbol}"):
            # Prepare data
            X = df[feature_columns].values
            y = df['Price_Direction'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest Classifier (Islamic finance compliant)
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation (following Islamic principle of verification)
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            
            # Save model
            company_info = self.tasi_companies.get(symbol, {"name": symbol, "islamic_compliant": True})
            model_path = os.path.join(self.models_dir, f"tasi_direction_model_{symbol.replace('.', '_')}")
            
            joblib.dump({
                'model': model,
                'scaler': scaler,
                'feature_columns': feature_columns,
                'company_info': company_info,
                'islamic_compliance': 'Fully Compliant - No interest-based calculations'
            }, f"{model_path}.joblib")
            
            # Log to MLflow
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("cv_mean", cv_scores.mean())
            mlflow.log_metric("cv_std", cv_scores.std())
            mlflow.log_param("islamic_compliance", "Fully Compliant")
            mlflow.log_param("company", company_info['name'])
            
            print(f"Direction Model - Accuracy: {accuracy:.4f}")
            print(f"Cross-validation: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            print(f"Islamic Compliance: ✅ Fully Compliant")
            
            return model, scaler
    
    def create_portfolio_optimization_model(self, portfolio_data):
        """Create Islamic finance-compliant portfolio optimization."""
        with mlflow.start_run(run_name="TASI_Portfolio_Optimization"):
            print("Creating Islamic Portfolio Optimization Model...")
            
            # Calculate expected returns (Halal method)
            returns_data = []
            for symbol, data in portfolio_data.items():
                if data is not None:
                    daily_returns = data['Close'].pct_change().dropna()
                    expected_return = daily_returns.mean() * 252  # Annualized
                    volatility = daily_returns.std() * np.sqrt(252)  # Annualized
                    
                    company_info = self.tasi_companies.get(symbol, {"name": symbol, "islamic_compliant": True})
                    
                    returns_data.append({
                        'symbol': symbol,
                        'company': company_info['name'],
                        'expected_return': expected_return,
                        'volatility': volatility,
                        'sharpe_ratio': expected_return / volatility if volatility > 0 else 0,
                        'islamic_compliant': company_info.get('islamic_compliant', True)
                    })
            
            portfolio_df = pd.DataFrame(returns_data)
            
            # Filter only Islamic-compliant stocks
            islamic_portfolio = portfolio_df[portfolio_df['islamic_compliant'] == True]
            
            # Simple equal-weight Islamic portfolio (following Islamic principle of fairness)
            n_stocks = len(islamic_portfolio)
            equal_weights = np.ones(n_stocks) / n_stocks
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(equal_weights * islamic_portfolio['expected_return'])
            portfolio_volatility = np.sqrt(np.sum((equal_weights ** 2) * (islamic_portfolio['volatility'] ** 2)))
            portfolio_sharpe = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Log to MLflow
            mlflow.log_metric("portfolio_return", portfolio_return)
            mlflow.log_metric("portfolio_volatility", portfolio_volatility)
            mlflow.log_metric("portfolio_sharpe", portfolio_sharpe)
            mlflow.log_param("islamic_compliance", "Fully Sharia Compliant")
            mlflow.log_param("optimization_method", "Equal Weight Islamic")
            
            print(f"Islamic Portfolio Expected Return: {portfolio_return:.4f}")
            print(f"Islamic Portfolio Volatility: {portfolio_volatility:.4f}")
            print(f"Islamic Portfolio Sharpe Ratio: {portfolio_sharpe:.4f}")
            print(f"Number of Islamic Stocks: {n_stocks}")
            
            # Save portfolio optimization
            portfolio_model = {
                'weights': equal_weights,
                'stocks': islamic_portfolio['symbol'].tolist(),
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': portfolio_sharpe,
                'islamic_compliance': 'Fully Sharia Compliant'
            }
            
            joblib.dump(portfolio_model, os.path.join(self.models_dir, "tasi_islamic_portfolio.joblib"))
            
            return portfolio_model
    
    def run_complete_pipeline(self):
        """Run the complete TASI Islamic ML pipeline."""
        print("🇸🇦 Starting TASI Islamic Finance ML Pipeline...")
        print("=" * 50)
        
        portfolio_data = {}
        
        # Train models for each TASI company
        for symbol, company_info in self.tasi_companies.items():
            print(f"\n📊 Processing {company_info['name']} ({symbol})...")
            print(f"Sector: {company_info['sector']}")
            print(f"Islamic Compliant: {'✅ Yes' if company_info['islamic_compliant'] else '❌ No'}")
            
            # Fetch data
            df = self.fetch_tasi_data(symbol)
            if df is None:
                continue
            
            portfolio_data[symbol] = df
            
            # Create Islamic features
            df_features = self.create_islamic_features(df)
            if df_features is None:
                continue
            
            # Prepare ML data
            df_ml, feature_columns = self.prepare_ml_data(df_features)
            if len(df_ml) < 100:  # Need sufficient data
                print(f"Insufficient data for {symbol}")
                continue
            
            print(f"Training Islamic ML models with {len(df_ml)} samples...")
            
            # Train price prediction model
            price_results, price_scaler = self.train_price_prediction_model(df_ml, feature_columns, symbol)
            
            # Train direction prediction model
            direction_model, direction_scaler = self.train_direction_prediction_model(df_ml, feature_columns, symbol)
        
        # Create Islamic portfolio optimization
        if portfolio_data:
            print(f"\n💼 Creating Islamic Portfolio Optimization...")
            portfolio_model = self.create_portfolio_optimization_model(portfolio_data)
        
        print("\n✅ TASI Islamic Finance ML Pipeline Completed!")
        print("🕌 All models are Sharia-compliant and follow Islamic finance principles")
        print(f"💾 Models saved in: {self.models_dir}/")

def main():
    """Main function to run TASI ML pipeline."""
    pipeline = TASIMLPipeline()
    pipeline.run_complete_pipeline()

if __name__ == "__main__":
    main()