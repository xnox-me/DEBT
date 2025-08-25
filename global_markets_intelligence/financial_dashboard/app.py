#!/usr/bin/env python3
"""
Global Markets & Crypto Intelligence Dashboard
Comprehensive International Market Analysis with Cryptocurrency, Major Economies, and Precious Metals
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="Global Markets & Crypto Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every minute for real-time updates
import time
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Check if a minute has passed
current_time = time.time()
if current_time - st.session_state.last_update >= 60:  # 60 seconds = 1 minute
    st.session_state.last_update = current_time
    st.rerun()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .country-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 1rem;
    }
    .crypto-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class GlobalMarketsAnalyzer:
    """Advanced global markets and cryptocurrency analysis."""
    
    def __init__(self):
        self.cache_duration = 60  # 1 minute cache for real-time updates
        
        # Global market symbols
        self.market_symbols = {
            # Cryptocurrencies
            "BTC-USD": {"name": "Bitcoin", "type": "crypto", "country": "Global"},
            "ETH-USD": {"name": "Ethereum", "type": "crypto", "country": "Global"},
            "BNB-USD": {"name": "Binance Coin", "type": "crypto", "country": "Global"},
            "XRP-USD": {"name": "Ripple", "type": "crypto", "country": "Global"},
            "ADA-USD": {"name": "Cardano", "type": "crypto", "country": "Global"},
            
            # US Market
            "^GSPC": {"name": "S&P 500", "type": "index", "country": "USA"},
            "AAPL": {"name": "Apple Inc", "type": "stock", "country": "USA"},
            "MSFT": {"name": "Microsoft", "type": "stock", "country": "USA"},
            "TSLA": {"name": "Tesla", "type": "stock", "country": "USA"},
            
            # China Market
            "000001.SS": {"name": "SSE Composite", "type": "index", "country": "China"},
            "BABA": {"name": "Alibaba", "type": "stock", "country": "China"},
            "BIDU": {"name": "Baidu", "type": "stock", "country": "China"},
            
            # Japan Market
            "^N225": {"name": "Nikkei 225", "type": "index", "country": "Japan"},
            "7203.T": {"name": "Toyota", "type": "stock", "country": "Japan"},
            "6758.T": {"name": "Sony", "type": "stock", "country": "Japan"},
            
            # Brazil Market
            "^BVSP": {"name": "Bovespa", "type": "index", "country": "Brazil"},
            "VALE": {"name": "Vale SA", "type": "stock", "country": "Brazil"},
            "ITUB": {"name": "Itau Unibanco", "type": "stock", "country": "Brazil"},
            
            # UK Market
            "^FTSE": {"name": "FTSE 100", "type": "index", "country": "UK"},
            "SHEL": {"name": "Shell", "type": "stock", "country": "UK"},
            "BP": {"name": "BP", "type": "stock", "country": "UK"},
            
            # France Market
            "^FCHI": {"name": "CAC 40", "type": "index", "country": "France"},
            "MC.PA": {"name": "LVMH", "type": "stock", "country": "France"},
            
            # Italy Market
            "FTSEMIB.MI": {"name": "FTSE MIB", "type": "index", "country": "Italy"},
            
            # Russia Market
            "IMOEX.ME": {"name": "MOEX", "type": "index", "country": "Russia"},
            
            # South Korea Market
            "^KS11": {"name": "KOSPI", "type": "index", "country": "Korea"},
            "005930.KS": {"name": "Samsung", "type": "stock", "country": "Korea"},
            
            # Precious Metals
            "GC=F": {"name": "Gold Futures", "type": "commodity", "country": "Global"},
            "SI=F": {"name": "Silver Futures", "type": "commodity", "country": "Global"},
        }
    
    @st.cache_data(ttl=60)  # Cache for 1 minute for real-time crypto/market updates
    def fetch_global_data(_self, symbols, period="1y"):
        """Fetch global market data."""
        data = {}
        for symbol, info in symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    data[symbol] = {
                        'info': info,
                        'history': hist,
                        'current_price': hist['Close'].iloc[-1],
                        'change_pct': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
                    }
            except Exception as e:
                st.warning(f"Could not fetch {symbol}: {str(e)}")
                continue
        return data
    
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators."""
        if df.empty:
            return df
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        return df

def main():
    """Main Global Markets Intelligence dashboard."""
    
    # Header
    st.markdown('<h1 class="main-header">🌍 Global Markets & Crypto Intelligence</h1>', unsafe_allow_html=True)
    st.markdown("**Real-time Analysis • Cryptocurrency • Major Economies • Precious Metals**")
    
    # Real-time update controls
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.info(f"🔄 **Live Global Markets**: Updated at {current_time} • Auto-refresh every 60 seconds")
    with col2:
        if st.button("🔄 Refresh Now", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        st.success("🟢 **LIVE** Data")
    with col4:
        if st.checkbox("⏱️ Real-time", value=True, help="Auto-refresh every minute"):
            pass  # Auto-refresh is always enabled
    
    # Initialize analyzer
    analyzer = GlobalMarketsAnalyzer()
    
    # Sidebar configuration
    st.sidebar.header("🌐 Global Markets Configuration")
    
    # Market type selection
    market_types = st.sidebar.multiselect(
        "Select Market Types:",
        options=["crypto", "stock", "index", "commodity"],
        default=["crypto", "stock", "index", "commodity"],
        help="Choose types of markets to analyze"
    )
    
    # Country selection
    countries = st.sidebar.multiselect(
        "Select Countries/Regions:",
        options=["USA", "China", "Japan", "Brazil", "UK", "France", "Italy", "Russia", "Korea", "Global"],
        default=["USA", "China", "Japan", "Global"],
        help="Choose countries for analysis"
    )
    
    analysis_period = st.sidebar.selectbox(
        "Analysis Period:",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=3
    )
    
    # Filter symbols based on selection
    filtered_symbols = {
        symbol: info for symbol, info in analyzer.market_symbols.items()
        if info['type'] in market_types and info['country'] in countries
    }
    
    if not filtered_symbols:
        st.warning("⚠️ Please select market types and countries.")
        return
    
    # Fetch data
    with st.spinner("🔄 Fetching global market data..."):
        market_data = analyzer.fetch_global_data(filtered_symbols, analysis_period)
    
    if not market_data:
        st.error("❌ Unable to fetch market data.")
        return
    
    # Global Market Overview
    st.header("📊 Global Market Overview")
    
    # Group by type
    crypto_data = {k: v for k, v in market_data.items() if v['info']['type'] == 'crypto'}
    stock_data = {k: v for k, v in market_data.items() if v['info']['type'] == 'stock'}
    index_data = {k: v for k, v in market_data.items() if v['info']['type'] == 'index'}
    commodity_data = {k: v for k, v in market_data.items() if v['info']['type'] == 'commodity'}
    
    # Display by categories
    if crypto_data:
        st.subheader("💰 Cryptocurrency Markets")
        crypto_cols = st.columns(len(crypto_data))
        for i, (symbol, data) in enumerate(crypto_data.items()):
            with crypto_cols[i % len(crypto_cols)]:
                price = data['current_price']
                change = data['change_pct']
                name = data['info']['name']
                st.metric(f"**{name}**", f"${price:,.2f}", f"{change:+.2f}%")
    
    if stock_data:
        st.subheader("📈 International Stocks")
        stock_cols = st.columns(min(len(stock_data), 4))
        for i, (symbol, data) in enumerate(stock_data.items()):
            with stock_cols[i % len(stock_cols)]:
                price = data['current_price']
                change = data['change_pct']
                name = data['info']['name']
                country = data['info']['country']
                st.metric(f"**{name}** ({country})", f"${price:.2f}", f"{change:+.2f}%")
    
    if index_data:
        st.subheader("📊 Global Indices")
        index_cols = st.columns(min(len(index_data), 4))
        for i, (symbol, data) in enumerate(index_data.items()):
            with index_cols[i % len(index_cols)]:
                price = data['current_price']
                change = data['change_pct']
                name = data['info']['name']
                country = data['info']['country']
                st.metric(f"**{name}** ({country})", f"{price:,.0f}", f"{change:+.2f}%")
    
    if commodity_data:
        st.subheader("🥇 Precious Metals")
        commodity_cols = st.columns(len(commodity_data))
        for i, (symbol, data) in enumerate(commodity_data.items()):
            with commodity_cols[i % len(commodity_cols)]:
                price = data['current_price']
                change = data['change_pct']
                name = data['info']['name']
                st.metric(f"**{name}**", f"${price:.2f}", f"{change:+.2f}%")
    
    # Detailed Analysis
    st.header("🔍 Detailed Market Analysis")
    
    selected_for_analysis = st.selectbox(
        "Select Asset for Detailed Analysis:",
        options=list(market_data.keys()),
        format_func=lambda x: f"{market_data[x]['info']['name']} ({market_data[x]['info']['country']})"
    )
    
    if selected_for_analysis in market_data:
        asset_data = market_data[selected_for_analysis]
        df = asset_data['history'].copy()
        asset_info = asset_data['info']
        
        if not df.empty:
            # Calculate indicators
            df = analyzer.calculate_technical_indicators(df)
            
            # Create chart
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    f'{asset_info["name"]} ({asset_info["country"]}) - Price Analysis',
                    'MACD',
                    'RSI'
                ),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # Price chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price"
            ), row=1, col=1)
            
            # Moving averages
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='orange')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='red')), row=1, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=2, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='red')), row=2, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            fig.update_layout(
                title=f"Global Markets Intelligence: {asset_info['name']} Technical Analysis",
                height=800,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Global Portfolio Analysis
    st.header("💼 Global Portfolio Analysis")
    
    portfolio_data = []
    total_value = 0
    
    for symbol, data in market_data.items():
        price = data['current_price']
        change = data['change_pct']
        info = data['info']
        shares = 100  # Demo allocation
        value = price * shares
        total_value += value
        
        portfolio_data.append({
            'Asset': info['name'],
            'Country': info['country'],
            'Type': info['type'].title(),
            'Price': price,
            'Shares': shares,
            'Value': value,
            'Change %': change,
            'Day P&L': value * (change / 100)
        })
    
    portfolio_df = pd.DataFrame(portfolio_data)
    
    # Portfolio summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", f"${total_value:,.2f}")
    with col2:
        total_pnl = portfolio_df['Day P&L'].sum()
        st.metric("Day P&L", f"${total_pnl:,.2f}", f"{(total_pnl/total_value)*100:.2f}%")
    with col3:
        avg_change = portfolio_df['Change %'].mean()
        st.metric("Avg Change", f"{avg_change:.2f}%")
    with col4:
        best_performer = portfolio_df.loc[portfolio_df['Change %'].idxmax(), 'Asset']
        best_change = portfolio_df['Change %'].max()
        st.metric("Best Performer", best_performer, f"{best_change:.2f}%")
    
    # Portfolio allocation charts
    col1, col2 = st.columns(2)
    
    with col1:
        # By Type
        type_allocation = portfolio_df.groupby('Type')['Value'].sum()
        fig_type = px.pie(values=type_allocation.values, names=type_allocation.index, title="Allocation by Asset Type")
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        # By Country
        country_allocation = portfolio_df.groupby('Country')['Value'].sum()
        fig_country = px.pie(values=country_allocation.values, names=country_allocation.index, title="Allocation by Country")
        st.plotly_chart(fig_country, use_container_width=True)
    
    # Portfolio performance table
    st.subheader("📋 Detailed Portfolio Performance")
    portfolio_display = portfolio_df.copy()
    portfolio_display['Price'] = portfolio_display['Price'].apply(lambda x: f"${x:.2f}")
    portfolio_display['Value'] = portfolio_display['Value'].apply(lambda x: f"${x:,.2f}")
    portfolio_display['Change %'] = portfolio_display['Change %'].apply(lambda x: f"{x:.2f}%")
    portfolio_display['Day P&L'] = portfolio_display['Day P&L'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(portfolio_display, use_container_width=True)

if __name__ == "__main__":
    main()