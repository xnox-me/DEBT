#!/usr/bin/env python3
"""
DEBT Business API Services
FastAPI-powered business data integration and services for DEBT platform.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import joblib
from pathlib import Path
import logging
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DEBT Business Intelligence API",
    description="Advanced business data services and ML predictions for DEBT platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class CustomerProfile(BaseModel):
    """Customer profile for churn and sales predictions."""
    age: int = Field(..., ge=18, le=100, description="Customer age")
    income: float = Field(..., ge=0, description="Annual income in USD")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    months_as_customer: int = Field(..., ge=1, description="Months as customer")
    num_products: int = Field(..., ge=1, le=10, description="Number of products")
    monthly_charges: float = Field(..., ge=0, description="Monthly charges in USD")
    satisfaction_score: float = Field(..., ge=1, le=10, description="Satisfaction score (1-10)")
    support_tickets: int = Field(..., ge=0, description="Number of support tickets")

class StockAnalysis(BaseModel):
    """Stock analysis request parameters."""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    period: str = Field(default="1y", description="Analysis period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")

class PredictionResponse(BaseModel):
    """Generic prediction response."""
    prediction: float
    confidence: Optional[float]
    model_name: str
    business_recommendation: str
    risk_factors: List[str]
    timestamp: datetime

class BusinessKPIResponse(BaseModel):
    """Business KPI metrics response."""
    total_customers: int
    monthly_revenue: float
    avg_customer_ltv: float
    churn_rate: float
    satisfaction_score: float
    high_value_customers: int

# Global variables for models and data
ml_models = {}
business_data_cache = {}

# Startup event to load models
@app.on_event("startup")
async def startup_event():
    """Load ML models and initialize business data on startup."""
    logger.info("🚀 Starting DEBT Business API Services...")
    
    # Try to load pre-trained models
    models_dir = Path("../ml_pipeline/models")
    if models_dir.exists():
        try:
            load_ml_models(models_dir)
            logger.info("✅ ML models loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not load ML models: {e}")
    
    # Generate sample business data for API demonstrations
    generate_sample_business_data()
    logger.info("✅ DEBT Business API Services ready")

def load_ml_models(models_dir: Path):
    """Load pre-trained ML models for predictions."""
    global ml_models
    
    for task_dir in models_dir.iterdir():
        if task_dir.is_dir():
            task_name = task_dir.name
            
            # Load metadata
            metadata_file = task_dir / "metadata.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Load model and scaler
                model_file = task_dir / f"best_model_{metadata['best_model_name']}.pkl"
                scaler_file = task_dir / "scaler.pkl"
                
                if model_file.exists() and scaler_file.exists():
                    model = joblib.load(model_file)
                    scaler = joblib.load(scaler_file)
                    
                    ml_models[task_name] = {
                        'model': model,
                        'scaler': scaler,
                        'metadata': metadata
                    }

def generate_sample_business_data():
    """Generate sample business data for API demonstrations."""
    global business_data_cache
    
    np.random.seed(42)
    n_samples = 1000
    
    # Generate sample customer data
    customers = []
    for i in range(n_samples):
        customer = {
            'customer_id': i + 1,
            'age': int(np.random.normal(40, 12, 1)[0]),
            'income': float(np.random.lognormal(10.5, 0.5, 1)[0]),
            'months_as_customer': int(np.random.poisson(18, 1)[0]),
            'monthly_charges': float(np.random.normal(75, 25, 1)[0]),
            'satisfaction_score': float(np.random.normal(7, 2, 1)[0]),
            'lifetime_value': float(np.random.normal(2000, 800, 1)[0])
        }
        customers.append(customer)
    
    business_data_cache['customers'] = customers

# API Endpoints

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API root endpoint with service information."""
    return {
        "service": "DEBT Business Intelligence API",
        "version": "1.0.0",
        "description": "Advanced business data services and ML predictions",
        "endpoints": {
            "/docs": "API documentation",
            "/health": "Service health check",
            "/predict/churn": "Customer churn prediction",
            "/predict/sales": "Sales forecasting",
            "/stock/analyze": "Stock market analysis",
            "/business/kpis": "Business KPI metrics"
        },
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "models_loaded": len(ml_models),
        "api_version": "1.0.0"
    }

@app.post("/predict/churn", response_model=PredictionResponse)
async def predict_customer_churn(customer: CustomerProfile):
    """Predict customer churn probability using advanced ML models."""
    
    try:
        # Calculate total charges
        total_charges = customer.monthly_charges * customer.months_as_customer
        
        # Prepare features for prediction
        features = np.array([
            customer.age,
            customer.income,
            customer.credit_score,
            customer.months_as_customer,
            customer.num_products,
            customer.monthly_charges,
            total_charges,
            customer.satisfaction_score,
            customer.support_tickets
        ])
        
        # Make prediction if model is available
        if 'customer_churn' in ml_models:
            model_info = ml_models['customer_churn']
            scaler = model_info['scaler']
            model = model_info['model']
            
            # Scale features for linear models
            model_name = model_info['metadata']['best_model_name']
            if model_name in ['logistic_regression', 'svm']:
                features_scaled = scaler.transform(features.reshape(1, -1))
                prediction = model.predict(features_scaled)[0]
                if hasattr(model, 'predict_proba'):
                    confidence = model.predict_proba(features_scaled)[0][1]
                else:
                    confidence = 0.5
            else:
                prediction = model.predict(features.reshape(1, -1))[0]
                if hasattr(model, 'predict_proba'):
                    confidence = model.predict_proba(features.reshape(1, -1))[0][1]
                else:
                    confidence = 0.5
        else:
            # Fallback prediction using business rules
            churn_score = (
                -0.1 * (customer.satisfaction_score - 5) / 5 +
                0.15 * (customer.support_tickets - 1) / 3 +
                0.05 * (customer.monthly_charges - 75) / 50 +
                -0.08 * (customer.months_as_customer - 24) / 24
            )
            confidence = max(0, min(1, (churn_score + 1) / 2))
            prediction = 1 if confidence > 0.5 else 0
            model_name = "business_rules"
        
        # Business recommendations based on prediction
        if confidence > 0.7:
            recommendation = "HIGH RISK: Immediate retention intervention required"
            risk_factors = ["Low satisfaction score", "High support tickets", "Payment issues"]
        elif confidence > 0.4:
            recommendation = "MODERATE RISK: Proactive engagement recommended"
            risk_factors = ["Monitor satisfaction", "Improve service quality"]
        else:
            recommendation = "LOW RISK: Customer likely to remain loyal"
            risk_factors = ["Maintain current service level"]
        
        # Add specific risk factors based on customer profile
        if customer.satisfaction_score < 6:
            risk_factors.append("Below average satisfaction score")
        if customer.support_tickets > 3:
            risk_factors.append("High number of support contacts")
        if customer.months_as_customer < 6:
            risk_factors.append("New customer - relationship developing")
        
        return PredictionResponse(
            prediction=float(confidence),
            confidence=float(confidence),
            model_name=model_name,
            business_recommendation=recommendation,
            risk_factors=risk_factors,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Churn prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/sales")
async def predict_sales_forecast(
    age: int = Query(..., description="Customer age"),
    income: float = Query(..., description="Annual income"),
    num_products: int = Query(..., description="Number of products"),
    satisfaction_score: float = Query(..., description="Satisfaction score"),
    months_as_customer: int = Query(..., description="Months as customer")
):
    """Predict customer sales potential using ML models."""
    
    try:
        # Prepare features
        features = np.array([age, income, num_products, satisfaction_score, months_as_customer])
        
        # Make prediction
        if 'sales_forecasting' in ml_models:
            model_info = ml_models['sales_forecasting']
            model = model_info['model']
            scaler = model_info['scaler']
            
            # Use scaler if needed
            model_name = model_info['metadata']['best_model_name']
            if model_name in ['linear_regression', 'elastic_net']:
                features_scaled = scaler.transform(features.reshape(1, -1))
                prediction = model.predict(features_scaled)[0]
            else:
                prediction = model.predict(features.reshape(1, -1))[0]
        else:
            # Fallback business logic prediction
            prediction = (
                num_products * 50 +
                income * 0.001 +
                satisfaction_score * 10 +
                np.random.normal(0, 20)
            )
            model_name = "business_rules"
        
        # Business categorization
        if prediction > 200:
            category = "HIGH VALUE"
            recommendation = "Priority customer - focus on retention and upselling"
        elif prediction > 100:
            category = "MEDIUM VALUE"
            recommendation = "Good customer - maintain engagement and explore growth"
        else:
            category = "LOW VALUE"
            recommendation = "Cost optimization focus - improve efficiency"
        
        return {
            "predicted_monthly_sales": round(prediction, 2),
            "customer_category": category,
            "model_name": model_name,
            "business_recommendation": recommendation,
            "confidence_interval": f"{prediction * 0.85:.2f} - {prediction * 1.15:.2f}",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Sales prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sales prediction failed: {str(e)}")

@app.post("/stock/analyze")
async def analyze_stock(stock: StockAnalysis):
    """Comprehensive stock market analysis with technical indicators."""
    
    try:
        # Fetch stock data
        ticker = yf.Ticker(stock.symbol)
        df = ticker.history(period=stock.period)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {stock.symbol}")
        
        # Calculate technical indicators
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        
        # RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Current metrics
        current_price = float(df['Close'].iloc[-1])
        price_change = float(df['Close'].iloc[-1] - df['Close'].iloc[-2])
        price_change_pct = float(price_change / df['Close'].iloc[-2] * 100)
        current_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50
        
        # Technical signals
        sma_signal = "Bullish" if current_price > df['SMA_20'].iloc[-1] else "Bearish"
        trend = "Uptrend" if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1] else "Downtrend"
        
        # Business recommendation
        if price_change_pct > 2 and current_rsi < 70:
            recommendation = "STRONG BUY - Positive momentum with room for growth"
        elif price_change_pct > 0.5 and current_rsi < 70:
            recommendation = "BUY - Moderate positive signals"
        elif price_change_pct < -2 and current_rsi > 30:
            recommendation = "STRONG SELL - Negative momentum confirmed"
        elif price_change_pct < -0.5:
            recommendation = "SELL - Bearish signals present"
        else:
            recommendation = "HOLD - Mixed signals, monitor closely"
        
        return {
            "symbol": stock.symbol,
            "current_price": current_price,
            "price_change": price_change,
            "price_change_percent": price_change_pct,
            "rsi": current_rsi,
            "sma_20": float(df['SMA_20'].iloc[-1]) if not pd.isna(df['SMA_20'].iloc[-1]) else None,
            "sma_50": float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else None,
            "short_term_signal": sma_signal,
            "trend": trend,
            "business_recommendation": recommendation,
            "volume": int(df['Volume'].iloc[-1]),
            "analysis_period": stock.period,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Stock analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stock analysis failed: {str(e)}")

@app.get("/business/kpis", response_model=BusinessKPIResponse)
async def get_business_kpis():
    """Get current business KPI metrics and performance indicators."""
    
    try:
        # Use cached business data or generate sample
        customers = business_data_cache.get('customers', [])
        
        if not customers:
            generate_sample_business_data()
            customers = business_data_cache['customers']
        
        # Calculate KPIs
        total_customers = len(customers)
        monthly_revenue = sum(c.get('monthly_charges', 75) for c in customers)
        avg_ltv = sum(c.get('lifetime_value', 2000) for c in customers) / len(customers)
        
        # Estimate churn rate and satisfaction
        churn_rate = 0.12  # 12% estimated churn rate
        avg_satisfaction = sum(c.get('satisfaction_score', 7) for c in customers) / len(customers)
        high_value_customers = len([c for c in customers if c.get('lifetime_value', 0) > 3000])
        
        return BusinessKPIResponse(
            total_customers=total_customers,
            monthly_revenue=monthly_revenue,
            avg_customer_ltv=avg_ltv,
            churn_rate=churn_rate,
            satisfaction_score=avg_satisfaction,
            high_value_customers=high_value_customers
        )
        
    except Exception as e:
        logger.error(f"KPIs calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"KPI calculation failed: {str(e)}")

@app.get("/business/customers")
async def get_customer_list(
    limit: int = Query(50, description="Number of customers to return"),
    high_value_only: bool = Query(False, description="Return only high-value customers")
):
    """Get list of customers with business metrics."""
    
    try:
        customers = business_data_cache.get('customers', [])
        
        if high_value_only:
            customers = [c for c in customers if c.get('lifetime_value', 0) > 3000]
        
        return {
            "customers": customers[:limit],
            "total_count": len(customers),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Customer list error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get customer list: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )