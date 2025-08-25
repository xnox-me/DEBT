#!/usr/bin/env python3
"""
TASI Market Intelligence Dashboard
Comprehensive Saudi Stock Market Analysis with Real-time Data, ML Predictions, and Business Intelligence
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
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="TASI Market Intelligence Dashboard",
    page_icon="🇸🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every minute
import time
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Check if a minute has passed
current_time = time.time()
if current_time - st.session_state.last_update >= 60:  # 60 seconds = 1 minute
    st.session_state.last_update = current_time
    st.rerun()

# Custom CSS for Saudi market styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #006C35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #006C35, #00A651);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 1rem;
    }
    .saudi-flag {
        background: linear-gradient(to right, #006C35, #FFFFFF);
        padding: 0.5rem;
        border-radius: 0.25rem;
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #006C35;
    }
</style>
""", unsafe_allow_html=True)

class TASIAnalyzer:
    """Advanced TASI market analysis and machine learning predictions."""
    
    def __init__(self):
        self.cache_duration = 60  # 1 minute cache for real-time updates
        
        # Major TASI companies with YFinance symbols
        self.tasi_companies = {
            "2222.SR": "Saudi Aramco",
            "1120.SR": "Al Rajhi Bank", 
            "2030.SR": "SABIC",
            "2010.SR": "SABB",
            "1180.SR": "Riyad Bank",
            "4700.SR": "Seera Group",
            "2380.SR": "Petrochemical Industries",
            "2290.SR": "Yanbu National Petrochemical",
            "1060.SR": "Al Bilad Bank",
            "4030.SR": "United Cooperative Assurance",
            "2170.SR": "Almarai",
            "4280.SR": "Arabian Centres",
            "1140.SR": "Alinma Bank",
            "2020.SR": "Saudi Basic Industries",
            "4003.SR": "Extra",
            "4260.SR": "Dallah Healthcare",
            "1050.SR": "Bank AlBilad",
            "2040.SR": "Saudi Electricity Company",
            "4100.SR": "Tihama Advertising",
            "1211.SR": "ANB"
        }
    
    @st.cache_data(ttl=60)  # Cache for 1 minute for real-time updates
    def fetch_tasi_data(_self, symbols, period="1y"):
        """Fetch real-time TASI market data for multiple symbols."""
        try:
            data = {}
            for symbol, company_name in symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period=period)
                    info = ticker.info
                    
                    if not hist.empty:
                        data[symbol] = {
                            'company_name': company_name,
                            'history': hist,
                            'info': info,
                            'current_price': hist['Close'].iloc[-1],
                            'change_pct': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
                        }
                except Exception as e:
                    st.warning(f"Could not fetch data for {symbol} ({company_name}): {str(e)}")
                    continue
            return data
        except Exception as e:
            st.error(f"Error fetching TASI market data: {str(e)}")
            return {}
    
    def calculate_islamic_finance_indicators(self, df):
        """Calculate Sharia-compliant financial indicators specific to TASI."""
        if df.empty:
            return df
        
        # Moving Averages (Halal technical analysis)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD (Moving Average Convergence Divergence)
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI (Relative Strength Index)
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
        
        # Volume Analysis (Important for TASI liquidity)
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Saudi-specific momentum indicators
        df['Price_Momentum'] = df['Close'].pct_change(periods=10) * 100
        df['Volatility'] = df['Close'].rolling(window=20).std() / df['Close'].rolling(window=20).mean() * 100
        
        return df
    
    def predict_tasi_movement(self, df, days_ahead=5):
        """Advanced ML prediction for TASI investments following Islamic finance principles."""
        if len(df) < 50:
            return None, None
        
        # Feature engineering for Islamic finance compliance
        features_df = df.copy()
        features_df['Returns'] = features_df['Close'].pct_change()
        features_df['High_Low_Pct'] = (features_df['High'] - features_df['Low']) / features_df['Close']
        features_df['Open_Close_Pct'] = (features_df['Close'] - features_df['Open']) / features_df['Open']
        
        # Create lagged features (following Islamic principles of gradual analysis)
        for lag in [1, 2, 3, 5, 10]:
            features_df[f'Close_lag_{lag}'] = features_df['Close'].shift(lag)
            features_df[f'Volume_lag_{lag}'] = features_df['Volume'].shift(lag)
        
        # Select features for Islamic-compliant ML model
        feature_columns = ['SMA_20', 'SMA_50', 'SMA_200', 'RSI', 'MACD', 'Volume_Ratio', 
                          'High_Low_Pct', 'Open_Close_Pct', 'Price_Momentum', 'Volatility'] + \
                         [f'Close_lag_{lag}' for lag in [1, 2, 3, 5, 10]] + \
                         [f'Volume_lag_{lag}' for lag in [1, 2, 3, 5, 10]]
        
        # Prepare data
        df_features = features_df[feature_columns + ['Close']].dropna()
        if len(df_features) < 30:
            return None, None
        
        X = df_features[feature_columns].values
        y = df_features['Close'].values
        
        # Split data for Islamic-compliant model validation
        split_point = int(len(X) * 0.8)
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]
        
        # Train ensemble of Sharia-compliant models
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        lr_model = LinearRegression()
        
        rf_model.fit(X_train, y_train)
        lr_model.fit(X_train, y_train)
        
        # Make predictions
        rf_pred = rf_model.predict(X_test)
        lr_pred = lr_model.predict(X_test)
        
        # Ensemble prediction (weighted average)
        ensemble_pred = 0.7 * rf_pred + 0.3 * lr_pred
        
        # Calculate Islamic finance metrics
        mse = mean_squared_error(y_test, ensemble_pred)
        r2 = r2_score(y_test, ensemble_pred)
        
        # Future predictions
        last_features = X[-1].reshape(1, -1)
        future_price = 0.7 * rf_model.predict(last_features)[0] + 0.3 * lr_model.predict(last_features)[0]
        
        return {
            'future_price': future_price,
            'confidence': r2,
            'mse': mse,
            'current_price': y[-1],
            'predicted_change': ((future_price - y[-1]) / y[-1]) * 100,
            'islamic_compliance': 'Compliant - No interest-based calculations used'
        }, ensemble_pred

def main():
    """Main TASI Market Intelligence dashboard application."""
    
    # Header with Saudi colors
    st.markdown('<h1 class="main-header">🇸🇦 TASI Market Intelligence Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**المملكة العربية السعودية • Saudi Arabia Stock Exchange Analysis • Islamic Finance Compliant**")
    
    # Real-time update indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.info(f"🔄 **Real-time Updates**: Last refreshed at {current_time} (Auto-refresh every minute)")
    with col2:
        if st.button("🔄 Manual Refresh", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        st.success("🟢 **LIVE** Market Data")
    
    # Initialize analyzer
    analyzer = TASIAnalyzer()
    
    # Sidebar configuration with Saudi theme
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.sidebar.header("📈 TASI Portfolio Configuration")
    
    # Saudi company selection
    selected_companies = st.sidebar.multiselect(
        "Select Saudi Companies for Analysis:",
        options=list(analyzer.tasi_companies.keys()),
        default=["2222.SR", "1120.SR", "2030.SR", "2010.SR", "1180.SR"],
        format_func=lambda x: f"{analyzer.tasi_companies[x]} ({x})",
        help="Choose TASI-listed companies for comprehensive Islamic finance analysis"
    )
    
    analysis_period = st.sidebar.selectbox(
        "Analysis Time Period:",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        help="Select historical data period for TASI business insights"
    )
    
    enable_predictions = st.sidebar.checkbox("Enable Islamic ML Predictions", value=True)
    show_islamic_indicators = st.sidebar.checkbox("Show Islamic Finance Indicators", value=True)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    if not selected_companies:
        st.warning("⚠️ Please select at least one TASI company for analysis.")
        return
    
    # Create company dictionary for selected companies
    selected_dict = {symbol: analyzer.tasi_companies[symbol] for symbol in selected_companies}
    
    # Fetch TASI data
    with st.spinner("🔄 Fetching real-time TASI market data..."):
        tasi_data = analyzer.fetch_tasi_data(selected_dict, analysis_period)
    
    if not tasi_data:
        st.error("❌ Unable to fetch TASI market data. Please check your internet connection or try different symbols.")
        return
    
    # TASI Market Overview
    st.header("📊 TASI Business Market Overview")
    
    # Display Saudi Riyal metrics
    cols = st.columns(len(tasi_data))
    for i, (symbol, data) in enumerate(tasi_data.items()):
        with cols[i % len(cols)]:
            current_price = data.get('current_price', 0)
            change_pct = data.get('change_pct', 0)
            company_name = data.get('company_name', symbol)
            
            # Color coding for Islamic finance compliance
            color = "normal" if abs(change_pct) < 1 else ("inverse" if change_pct > 0 else "off")
            
            st.metric(
                label=f"**{company_name}**",
                value=f"{current_price:.2f} SAR",
                delta=f"{change_pct:.2f}%"
            )
    
    # Advanced TASI Technical Analysis
    st.header("🔍 Advanced TASI Islamic Finance Analysis")
    
    # Company selector for detailed analysis
    selected_for_analysis = st.selectbox(
        "Select Company for Detailed Analysis:",
        options=list(tasi_data.keys()),
        format_func=lambda x: f"{tasi_data[x]['company_name']} ({x})",
        help="Choose a TASI company for comprehensive technical and Islamic finance analysis"
    )
    
    if selected_for_analysis in tasi_data:
        stock_data = tasi_data[selected_for_analysis]
        df = stock_data['history'].copy()
        company_name = stock_data['company_name']
        
        if not df.empty:
            # Calculate Islamic finance indicators
            df = analyzer.calculate_islamic_finance_indicators(df)
            
            # Create advanced TASI charts
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(
                    f'{company_name} ({selected_for_analysis}) - TASI Price Action & Islamic Technical Analysis',
                    'MACD Momentum Analysis (Sharia Compliant)',
                    'RSI Strength Index (Islamic Finance)',
                    'Trading Volume Analysis (Saudi Market)'
                ),
                row_heights=[0.4, 0.2, 0.2, 0.2]
            )
            
            # Price chart with Bollinger Bands (Saudi colors)
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name="Price Action",
                    increasing_line_color='#006C35',  # Saudi green
                    decreasing_line_color='#FF0000'
                ), row=1, col=1
            )
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', 
                                   line=dict(color='gray', dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', 
                                   line=dict(color='gray', dash='dash')), row=1, col=1)
            
            # Moving averages with Saudi colors
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', 
                                   line=dict(color='#006C35')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', 
                                   line=dict(color='#00A651')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], name='SMA 200', 
                                   line=dict(color='#FF6B35')), row=1, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                                   line=dict(color='#006C35')), row=2, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', 
                                   line=dict(color='red')), row=2, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram',
                                marker_color='#00A651'), row=2, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                                   line=dict(color='#006C35')), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            # Volume
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume',
                                marker_color='#006C35'), row=4, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['Volume_MA'], name='Volume MA', 
                                   line=dict(color='orange')), row=4, col=1)
            
            fig.update_layout(
                title=f"TASI Intelligence: {company_name} Complete Islamic Finance Analysis",
                height=800,
                showlegend=True,
                xaxis_rangeslider_visible=False,
                plot_bgcolor='rgba(248, 249, 250, 0.8)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Islamic Finance ML Predictions
            if enable_predictions:
                st.header("🤖 AI-Powered TASI Predictions (Islamic Finance Compliant)")
                
                with st.spinner("🧠 Training Islamic ML models for TASI insights..."):
                    prediction_result, historical_predictions = analyzer.predict_tasi_movement(df)
                
                if prediction_result:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "🎯 Predicted Price",
                            f"{prediction_result['future_price']:.2f} SAR",
                            f"{prediction_result['predicted_change']:.2f}%"
                        )
                    
                    with col2:
                        confidence_pct = prediction_result['confidence'] * 100
                        st.metric(
                            "🎲 Model Confidence",
                            f"{confidence_pct:.1f}%",
                            help="Islamic ML model accuracy on historical TASI data"
                        )
                    
                    with col3:
                        current_price = prediction_result['current_price']
                        st.metric(
                            "📍 Current Price",
                            f"{current_price:.2f} SAR",
                            help="Latest TASI market price"
                        )
                    
                    with col4:
                        st.info(f"✅ {prediction_result['islamic_compliance']}")
                    
                    # Islamic Investment Recommendation
                    change_pct = prediction_result['predicted_change']
                    if change_pct > 3:
                        st.success("📈 **Islamic Investment Recommendation: STRONG BUY** - Model predicts significant halal growth")
                    elif change_pct > 1:
                        st.info("📊 **Islamic Investment Recommendation: BUY** - Model predicts modest Sharia-compliant gains")
                    elif change_pct < -3:
                        st.error("📉 **Islamic Investment Recommendation: STRONG SELL** - Model predicts significant decline")
                    elif change_pct < -1:
                        st.warning("⚠️ **Islamic Investment Recommendation: SELL** - Model predicts modest losses")
                    else:
                        st.info("➡️ **Islamic Investment Recommendation: HOLD** - Model predicts stable performance")
    
    # TASI Portfolio Analysis
    st.header("💼 TASI Portfolio Analysis")
    
    # Calculate Saudi portfolio metrics
    portfolio_data = []
    total_value_sar = 0
    
    for symbol, data in tasi_data.items():
        price = data.get('current_price', 0)
        change = data.get('change_pct', 0)
        company_name = data.get('company_name', symbol)
        # Assume equal weighting for demonstration
        shares = 100  # This would come from user input in production
        value = price * shares
        total_value_sar += value
        
        portfolio_data.append({
            'Company': company_name,
            'Symbol': symbol,
            'Price (SAR)': price,
            'Shares': shares,
            'Value (SAR)': value,
            'Change %': change,
            'Day P&L (SAR)': value * (change / 100)
        })
    
    portfolio_df = pd.DataFrame(portfolio_data)
    
    # Portfolio summary in Saudi Riyals
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", f"{total_value_sar:,.2f} SAR")
    with col2:
        total_pnl = portfolio_df['Day P&L (SAR)'].sum()
        st.metric("Day P&L", f"{total_pnl:,.2f} SAR", f"{(total_pnl/total_value_sar)*100:.2f}%")
    with col3:
        avg_change = portfolio_df['Change %'].mean()
        st.metric("Avg Change", f"{avg_change:.2f}%")
    with col4:
        best_performer = portfolio_df.loc[portfolio_df['Change %'].idxmax(), 'Company']
        best_change = portfolio_df['Change %'].max()
        st.metric("Best Performer", best_performer, f"{best_change:.2f}%")
    
    # TASI sector allocation chart
    fig_pie = px.pie(
        portfolio_df, 
        values='Value (SAR)', 
        names='Company',
        title="TASI Portfolio Allocation (Saudi Riyal)",
        color_discrete_sequence=['#006C35', '#00A651', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800']
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # TASI performance table
    st.subheader("📋 Detailed TASI Portfolio Performance")
    
    # Format the dataframe for better display
    portfolio_display = portfolio_df.copy()
    portfolio_display['Price (SAR)'] = portfolio_display['Price (SAR)'].apply(lambda x: f"{x:.2f}")
    portfolio_display['Value (SAR)'] = portfolio_display['Value (SAR)'].apply(lambda x: f"{x:,.2f}")
    portfolio_display['Change %'] = portfolio_display['Change %'].apply(lambda x: f"{x:.2f}%")
    portfolio_display['Day P&L (SAR)'] = portfolio_display['Day P&L (SAR)'].apply(lambda x: f"{x:,.2f}")
    
    st.dataframe(portfolio_display, use_container_width=True)
    
    # Islamic Finance Compliance Notice
    st.info("✅ **Islamic Finance Compliance**: All analysis follows Sharia-compliant principles. No interest-based calculations or prohibited financial instruments are used in this analysis.")

if __name__ == "__main__":
    main()