#!/usr/bin/env python3
"""
Global Markets & Crypto Intelligence API Services
Real-time API for International Markets, Cryptocurrency, and Precious Metals Analysis
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import asyncio
import aiohttp
import logging
import os
import json
import time

# Real-time cache with 1-minute TTL for crypto and global markets
CACHE_TTL = 60  # 1 minute in seconds
cache_store = {}

def get_cached_data(key):
    """Get data from cache if not expired."""
    if key in cache_store:
        data, timestamp = cache_store[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
    return None

def set_cached_data(key, data):
    """Store data in cache with timestamp."""
    cache_store[key] = (data, time.time())

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class GlobalMarketRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of global market symbols")
    period: str = Field("1d", description="Data period")

class CryptoAnalysisRequest(BaseModel):
    crypto_symbols: List[str] = Field(..., description="List of crypto symbols")
    vs_currency: str = Field("USD", description="Base currency for comparison")

class GlobalPortfolioRequest(BaseModel):
    stocks: List[str] = Field([], description="Stock symbols")
    crypto: List[str] = Field([], description="Crypto symbols") 
    commodities: List[str] = Field([], description="Commodity symbols")
    allocation_method: str = Field("equal_weight", description="Allocation strategy")

class GlobalMarketsAPI:
    """Main Global Markets API service class."""
    
    def __init__(self):
        self.app = FastAPI(
            title="Global Markets & Crypto Intelligence API",
            description="Real-time API for International Markets, Cryptocurrency, and Precious Metals",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Global market symbols with real-time support
        self.market_symbols = {
            # Cryptocurrencies (Real-time)
            "BTC-USD": {"name": "Bitcoin", "type": "crypto", "country": "Global", "currency": "USD"},
            "ETH-USD": {"name": "Ethereum", "type": "crypto", "country": "Global", "currency": "USD"},
            "BNB-USD": {"name": "Binance Coin", "type": "crypto", "country": "Global", "currency": "USD"},
            "XRP-USD": {"name": "Ripple", "type": "crypto", "country": "Global", "currency": "USD"},
            "ADA-USD": {"name": "Cardano", "type": "crypto", "country": "Global", "currency": "USD"},
            
            # US Market
            "^GSPC": {"name": "S&P 500", "type": "index", "country": "USA", "currency": "USD"},
            "AAPL": {"name": "Apple Inc", "type": "stock", "country": "USA", "currency": "USD"},
            "MSFT": {"name": "Microsoft", "type": "stock", "country": "USA", "currency": "USD"},
            "TSLA": {"name": "Tesla", "type": "stock", "country": "USA", "currency": "USD"},
            "NVDA": {"name": "NVIDIA", "type": "stock", "country": "USA", "currency": "USD"},
            
            # China Market
            "000001.SS": {"name": "SSE Composite", "type": "index", "country": "China", "currency": "CNY"},
            "BABA": {"name": "Alibaba", "type": "stock", "country": "China", "currency": "USD"},
            "BIDU": {"name": "Baidu", "type": "stock", "country": "China", "currency": "USD"},
            
            # Japan Market
            "^N225": {"name": "Nikkei 225", "type": "index", "country": "Japan", "currency": "JPY"},
            "7203.T": {"name": "Toyota", "type": "stock", "country": "Japan", "currency": "JPY"},
            "6758.T": {"name": "Sony", "type": "stock", "country": "Japan", "currency": "JPY"},
            
            # Brazil Market
            "^BVSP": {"name": "Bovespa", "type": "index", "country": "Brazil", "currency": "BRL"},
            "VALE": {"name": "Vale SA", "type": "stock", "country": "Brazil", "currency": "USD"},
            "ITUB": {"name": "Itau Unibanco", "type": "stock", "country": "Brazil", "currency": "USD"},
            
            # UK Market
            "^FTSE": {"name": "FTSE 100", "type": "index", "country": "UK", "currency": "GBP"},
            "SHEL": {"name": "Shell", "type": "stock", "country": "UK", "currency": "USD"},
            "BP": {"name": "BP", "type": "stock", "country": "UK", "currency": "USD"},
            
            # Precious Metals (Real-time)
            "GC=F": {"name": "Gold Futures", "type": "commodity", "country": "Global", "currency": "USD"},
            "SI=F": {"name": "Silver Futures", "type": "commodity", "country": "Global", "currency": "USD"},
        }
        
        # Initialize routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup all API routes for global markets."""
        
        @self.app.get("/")
        async def root():
            """API root with global markets service overview."""
            return {
                "service": "Global Markets & Crypto Intelligence API",
                "version": "1.0.0",
                "description": "Real-time International Markets, Cryptocurrency, and Precious Metals Analysis",
                "real_time_updates": "Every 60 seconds",
                "coverage": {
                    "countries": ["USA", "China", "Japan", "Brazil", "UK", "France", "Italy", "Russia", "Korea"],
                    "cryptocurrencies": ["Bitcoin", "Ethereum", "Binance Coin", "Ripple", "Cardano"],
                    "precious_metals": ["Gold", "Silver"],
                    "total_assets": len(self.market_symbols)
                },
                "endpoints": {
                    "/docs": "Interactive API documentation",
                    "/health": "Service health check",
                    "/global/markets": "All global markets overview",
                    "/global/market/{symbol}": "Specific asset data",
                    "/crypto/overview": "Cryptocurrency market summary",
                    "/global/realtime/status": "Real-time update status",
                    "/global/portfolio/analyze": "Global portfolio analysis"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check for Global Markets API."""
            return {
                "status": "healthy",
                "service": "Global Markets & Crypto Intelligence API",
                "timestamp": datetime.now().isoformat(),
                "real_time_cache": f"{len(cache_store)} entries",
                "cache_ttl": f"{CACHE_TTL} seconds",
                "markets_available": len(self.market_symbols)
            }
        
        @self.app.get("/global/markets")
        async def get_all_global_markets():
            """Get overview of all global markets with real-time data."""
            try:
                # Check cache first
                cache_key = "all_global_markets"
                cached_data = get_cached_data(cache_key)
                if cached_data:
                    return cached_data
                
                markets_data = []
                
                for symbol, info in self.market_symbols.items():
                    try:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1d")
                        
                        if not hist.empty:
                            current_price = float(hist['Close'].iloc[-1])
                            change_pct = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
                            
                            markets_data.append({
                                "symbol": symbol,
                                "name": info["name"],
                                "type": info["type"],
                                "country": info["country"],
                                "currency": info["currency"],
                                "current_price": current_price,
                                "change_percent": change_pct,
                                "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
                            })
                    except Exception as e:
                        logger.warning(f"Could not fetch data for {symbol}: {str(e)}")
                        continue
                
                result = {
                    "total_markets": len(markets_data),
                    "markets_by_type": {
                        "cryptocurrencies": len([m for m in markets_data if m["type"] == "crypto"]),
                        "stocks": len([m for m in markets_data if m["type"] == "stock"]),
                        "indices": len([m for m in markets_data if m["type"] == "index"]),
                        "commodities": len([m for m in markets_data if m["type"] == "commodity"])
                    },
                    "markets": markets_data,
                    "timestamp": datetime.now().isoformat(),
                    "real_time_update": "Data refreshed every minute",
                    "cache_ttl": CACHE_TTL
                }
                
                # Cache the result
                set_cached_data(cache_key, result)
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching global markets: {str(e)}")
        
        @self.app.get("/global/market/{symbol}")
        async def get_specific_market(symbol: str, period: str = "1d"):
            """Get detailed real-time data for a specific global market asset."""
            try:
                # Check cache first
                cache_key = f"market_{symbol}_{period}"
                cached_data = get_cached_data(cache_key)
                if cached_data:
                    return cached_data
                
                if symbol not in self.market_symbols:
                    raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                info = ticker.info
                
                if hist.empty:
                    raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
                
                current_price = float(hist['Close'].iloc[-1])
                previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
                change = current_price - previous_close
                change_pct = (change / previous_close * 100) if previous_close else 0
                
                asset_info = self.market_symbols[symbol]
                
                result = {
                    "symbol": symbol,
                    "name": asset_info["name"],
                    "type": asset_info["type"],
                    "country": asset_info["country"],
                    "currency": asset_info["currency"],
                    "current_price": current_price,
                    "previous_close": previous_close,
                    "change": change,
                    "change_percent": change_pct,
                    "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    "high_52_week": info.get('fiftyTwoWeekHigh'),
                    "low_52_week": info.get('fiftyTwoWeekLow'),
                    "market_cap": info.get('marketCap'),
                    "timestamp": datetime.now().isoformat(),
                    "real_time_update": "Data refreshed every minute",
                    "cache_ttl": CACHE_TTL
                }
                
                # Cache the result
                set_cached_data(cache_key, result)
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")
        
        @self.app.get("/crypto/overview")
        async def get_crypto_overview():
            """Get real-time cryptocurrency market overview."""
            try:
                # Check cache first
                cache_key = "crypto_overview"
                cached_data = get_cached_data(cache_key)
                if cached_data:
                    return cached_data
                
                crypto_symbols = {k: v for k, v in self.market_symbols.items() if v["type"] == "crypto"}
                crypto_data = []
                total_market_cap = 0
                
                for symbol, info in crypto_symbols.items():
                    try:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1d")
                        ticker_info = ticker.info
                        
                        if not hist.empty:
                            current_price = float(hist['Close'].iloc[-1])
                            change_pct = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
                            market_cap = ticker_info.get('marketCap', 0)
                            total_market_cap += market_cap if market_cap else 0
                            
                            crypto_data.append({
                                "symbol": symbol,
                                "name": info["name"],
                                "current_price": current_price,
                                "change_percent": change_pct,
                                "market_cap": market_cap,
                                "volume_24h": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
                            })
                    except Exception as e:
                        logger.warning(f"Could not fetch crypto data for {symbol}: {str(e)}")
                        continue
                
                result = {
                    "total_cryptocurrencies": len(crypto_data),
                    "total_market_cap_usd": total_market_cap,
                    "cryptocurrencies": crypto_data,
                    "market_sentiment": "Bullish" if sum(c["change_percent"] for c in crypto_data) > 0 else "Bearish",
                    "timestamp": datetime.now().isoformat(),
                    "real_time_update": "Crypto data refreshed every minute",
                    "cache_ttl": CACHE_TTL
                }
                
                # Cache the result
                set_cached_data(cache_key, result)
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching crypto overview: {str(e)}")
        
        @self.app.get("/global/realtime/status")
        async def get_realtime_status():
            """Get real-time update status and performance metrics."""
            return {
                "real_time_updates": "Enabled",
                "cache_ttl_seconds": CACHE_TTL,
                "update_frequency": "Every 60 seconds",
                "cache_entries": len(cache_store),
                "supported_assets": len(self.market_symbols),
                "asset_breakdown": {
                    "cryptocurrencies": len([s for s in self.market_symbols.values() if s["type"] == "crypto"]),
                    "stocks": len([s for s in self.market_symbols.values() if s["type"] == "stock"]),
                    "indices": len([s for s in self.market_symbols.values() if s["type"] == "index"]),
                    "commodities": len([s for s in self.market_symbols.values() if s["type"] == "commodity"])
                },
                "performance": {
                    "cache_hit_ratio": "Optimized for 1-minute intervals",
                    "data_freshness": "Real-time with 60-second maximum delay"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/global/portfolio/analyze")
        async def analyze_global_portfolio(request: GlobalPortfolioRequest):
            """Analyze a diversified global portfolio with real-time data."""
            try:
                all_symbols = request.stocks + request.crypto + request.commodities
                
                if not all_symbols:
                    raise HTTPException(status_code=400, detail="No symbols provided for analysis")
                
                portfolio_data = []
                total_value = 0
                
                for symbol in all_symbols:
                    if symbol in self.market_symbols:
                        try:
                            ticker = yf.Ticker(symbol)
                            hist = ticker.history(period="1y")
                            
                            if not hist.empty:
                                current_price = float(hist['Close'].iloc[-1])
                                returns = hist['Close'].pct_change().dropna()
                                volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
                                
                                asset_info = self.market_symbols[symbol]
                                shares = 100  # Demo allocation
                                value = current_price * shares
                                total_value += value
                                
                                portfolio_data.append({
                                    "symbol": symbol,
                                    "name": asset_info["name"],
                                    "type": asset_info["type"],
                                    "country": asset_info["country"],
                                    "currency": asset_info["currency"],
                                    "current_price": current_price,
                                    "shares": shares,
                                    "value": value,
                                    "annual_volatility": volatility
                                })
                        except Exception as e:
                            logger.warning(f"Could not analyze {symbol}: {str(e)}")
                            continue
                
                # Calculate portfolio metrics
                for item in portfolio_data:
                    item["weight_percent"] = (item["value"] / total_value) * 100
                
                # Geographic diversification
                country_allocation = {}
                type_allocation = {}
                
                for item in portfolio_data:
                    country = item["country"]
                    asset_type = item["type"]
                    
                    country_allocation[country] = country_allocation.get(country, 0) + item["weight_percent"]
                    type_allocation[asset_type] = type_allocation.get(asset_type, 0) + item["weight_percent"]
                
                return {
                    "portfolio_value": total_value,
                    "number_of_assets": len(portfolio_data),
                    "geographic_diversification": country_allocation,
                    "asset_type_diversification": type_allocation,
                    "portfolio_details": portfolio_data,
                    "risk_assessment": {
                        "diversification_score": len(set(item["country"] for item in portfolio_data)),
                        "crypto_exposure": type_allocation.get("crypto", 0),
                        "international_exposure": 100 - country_allocation.get("USA", 0)
                    },
                    "timestamp": datetime.now().isoformat(),
                    "real_time_analysis": "Portfolio analyzed with minute-fresh data"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")

# Create the FastAPI application
global_markets_api = GlobalMarketsAPI()
app = global_markets_api.app

if __name__ == "__main__":
    import uvicorn
    
    print("🌍 Starting Global Markets & Crypto Intelligence API...")
    print("=" * 60)
    print("API: Global Markets & Crypto Intelligence")
    print("Real-time Updates: Every 60 seconds")
    print("Coverage: International Markets + Cryptocurrency + Precious Metals")
    print("Access: http://localhost:8005")
    print("Docs: http://localhost:8005/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
        reload=True
    )