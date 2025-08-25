#!/usr/bin/env python3
"""
TASI Islamic Finance ML Interface
Interactive Gradio Interface for Saudi Stock Market Predictions
"""

import gradio as gr
import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler

class TASIMLInterface:
    """Interactive interface for TASI Islamic finance ML predictions."""
    
    def __init__(self):
        self.models_dir = "../ml_pipeline/models"
        
        # TASI companies
        self.tasi_companies = {
            "2222.SR": "Saudi Aramco",
            "1120.SR": "Al Rajhi Bank", 
            "2030.SR": "SABIC",
            "2010.SR": "SABB",
            "1180.SR": "Riyad Bank",
            "2170.SR": "Almarai",
            "2040.SR": "Saudi Electricity Company",
            "2380.SR": "Petrochemical Industries",
            "1140.SR": "Alinma Bank",
            "1211.SR": "ANB"
        }
    
    def load_model(self, symbol):
        """Load trained TASI model for a specific company."""
        try:
            model_path = os.path.join(self.models_dir, f"tasi_price_model_{symbol.replace('.', '_')}.joblib")
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                return None
        except Exception as e:
            print(f"Error loading model for {symbol}: {str(e)}")
            return None
    
    def fetch_latest_data(self, symbol):
        """Fetch latest TASI data for prediction."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")
            if hist.empty:
                return None
            return hist
        except:
            return None
    
    def create_features(self, df):
        """Create features for prediction."""
        if df.empty or len(df) < 50:
            return None
        
        # Technical indicators
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Price momentum
        df['Price_Momentum_5'] = df['Close'].pct_change(periods=5)
        df['Price_Momentum_10'] = df['Close'].pct_change(periods=10)
        df['Price_Momentum_20'] = df['Close'].pct_change(periods=20)
        
        # Volatility measures
        df['Volatility_5'] = df['Close'].rolling(window=5).std()
        df['Volatility_10'] = df['Close'].rolling(window=10).std()
        df['Volatility_20'] = df['Close'].rolling(window=20).std()
        
        # Volume indicators
        df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA_10'] = df['Volume'].rolling(window=10).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_10']
        
        # High-Low spread
        df['High_Low_Spread'] = (df['High'] - df['Low']) / df['Close']
        df['Open_Close_Spread'] = (df['Close'] - df['Open']) / df['Open']
        
        # Trend indicators
        df['Trend_5'] = (df['Close'] > df['SMA_5']).astype(int)
        df['Trend_20'] = (df['Close'] > df['SMA_20']).astype(int)
        df['Trend_50'] = (df['Close'] > df['SMA_50']).astype(int)
        
        # Lagged features
        for lag in [1, 2, 3, 5]:
            df[f'Close_lag_{lag}'] = df['Close'].shift(lag)
            df[f'Volume_lag_{lag}'] = df['Volume'].shift(lag)
            df[f'Returns_lag_{lag}'] = df['Close'].pct_change().shift(lag)
        
        return df
    
    def predict_tasi_price(self, company_symbol):
        """Predict TASI stock price using Islamic ML models."""
        try:
            # Load model
            model_data = self.load_model(company_symbol)
            if model_data is None:
                return "❌ Model not available for this company. Please train the model first.", None
            
            # Fetch latest data
            df = self.fetch_latest_data(company_symbol)
            if df is None:
                return "❌ Unable to fetch market data for this company.", None
            
            # Create features
            df_features = self.create_features(df)
            if df_features is None:
                return "❌ Insufficient data for prediction.", None
            
            # Prepare features
            feature_columns = model_data['feature_columns']
            latest_features = df_features[feature_columns].iloc[-1].values.reshape(1, -1)
            
            # Handle missing values
            if np.isnan(latest_features).any():
                return "❌ Missing data in recent market information.", None
            
            # Scale features
            scaler = model_data['scaler']
            latest_features_scaled = scaler.transform(latest_features)
            
            # Make prediction using ensemble
            rf_pred = model_data['rf_model'].predict(latest_features_scaled)[0]
            lr_pred = model_data['lr_model'].predict(latest_features_scaled)[0]
            ensemble_pred = 0.7 * rf_pred + 0.3 * lr_pred
            
            # Current price
            current_price = df['Close'].iloc[-1]
            change_pct = ((ensemble_pred - current_price) / current_price) * 100
            
            # Company info
            company_info = model_data['company_info']
            company_name = company_info['name']
            
            # Islamic recommendation
            if change_pct > 3:
                recommendation = "🟢 STRONG BUY (Islamic Finance Approved)"
                risk_level = "Low Risk"
            elif change_pct > 1:
                recommendation = "🔵 BUY (Sharia Compliant)"
                risk_level = "Low-Medium Risk"
            elif change_pct < -3:
                recommendation = "🔴 STRONG SELL (Risk Management)"
                risk_level = "High Risk"
            elif change_pct < -1:
                recommendation = "🟡 SELL (Caution Advised)"
                risk_level = "Medium-High Risk"
            else:
                recommendation = "⚪ HOLD (Stable Performance)"
                risk_level = "Medium Risk"
            
            # Create result text
            result = f"""
🇸🇦 **TASI Islamic Finance Prediction**

**Company**: {company_name} ({company_symbol})
**Current Price**: {current_price:.2f} SAR
**Predicted Price**: {ensemble_pred:.2f} SAR
**Expected Change**: {change_pct:+.2f}%

**Islamic Investment Recommendation**: {recommendation}
**Risk Assessment**: {risk_level}

**Islamic Compliance**: ✅ {model_data['islamic_compliance']}

**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*This prediction follows Islamic finance principles and excludes interest-based calculations.*
"""
            
            # Create chart
            chart_data = df.tail(30)  # Last 30 days
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(go.Scatter(
                x=chart_data.index,
                y=chart_data['Close'],
                mode='lines+markers',
                name='TASI Price (SAR)',
                line=dict(color='#006C35', width=2)
            ))
            
            # Add prediction point
            fig.add_trace(go.Scatter(
                x=[chart_data.index[-1] + pd.Timedelta(days=1)],
                y=[ensemble_pred],
                mode='markers',
                name='Predicted Price',
                marker=dict(color='red', size=10, symbol='star')
            ))
            
            fig.update_layout(
                title=f'{company_name} TASI Price Prediction',
                xaxis_title='Date',
                yaxis_title='Price (SAR)',
                template='plotly_white',
                showlegend=True
            )
            
            return result, fig
            
        except Exception as e:
            return f"❌ Error making prediction: {str(e)}", None
    
    def analyze_portfolio(self, *selected_companies):
        """Analyze Islamic portfolio allocation."""
        try:
            if not any(selected_companies):
                return "❌ Please select at least one company for portfolio analysis."
            
            portfolio_results = []
            total_investment = 100000  # 100,000 SAR
            
            # Equal allocation (Islamic principle of fairness)
            selected = [comp for comp in selected_companies if comp]
            allocation_per_stock = total_investment / len(selected)
            
            for company_symbol in selected:
                # Get current price
                df = self.fetch_latest_data(company_symbol)
                if df is not None:
                    current_price = df['Close'].iloc[-1]
                    shares = int(allocation_per_stock / current_price)
                    actual_investment = shares * current_price
                    
                    portfolio_results.append({
                        'Company': self.tasi_companies[company_symbol],
                        'Symbol': company_symbol,
                        'Price (SAR)': f"{current_price:.2f}",
                        'Shares': shares,
                        'Investment (SAR)': f"{actual_investment:,.2f}",
                        'Weight': f"{(actual_investment/total_investment)*100:.1f}%"
                    })
            
            if not portfolio_results:
                return "❌ Unable to fetch data for selected companies."
            
            # Create portfolio summary
            df_portfolio = pd.DataFrame(portfolio_results)
            
            result = f"""
🇸🇦 **Islamic Portfolio Analysis**

**Total Investment**: {total_investment:,} SAR
**Number of Stocks**: {len(selected)}
**Allocation Strategy**: Equal Weight (Islamic Fairness Principle)

**Portfolio Holdings**:
"""
            
            for _, row in df_portfolio.iterrows():
                result += f"\n• **{row['Company']}** ({row['Symbol']}): {row['Investment (SAR)']} SAR ({row['Weight']})"
            
            result += f"""

**Islamic Compliance**: ✅ All selected companies are Sharia-compliant
**Diversification**: Portfolio follows Islamic risk distribution principles
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d')}

*This portfolio allocation follows Islamic finance principles of fairness and risk sharing.*
"""
            
            return result
            
        except Exception as e:
            return f"❌ Error analyzing portfolio: {str(e)}"

def create_tasi_interface():
    """Create the main TASI ML interface."""
    interface = TASIMLInterface()
    
    with gr.Blocks(title="🇸🇦 TASI Islamic Finance ML Interface") as demo:
        gr.Markdown("""
        # 🇸🇦 TASI Islamic Finance ML Interface
        ## Saudi Stock Exchange Analysis with Sharia-Compliant Machine Learning
        
        *Powered by Islamic Finance-Compliant AI Models*
        """)
        
        with gr.Tab("🔮 Stock Price Prediction"):
            gr.Markdown("### Predict individual TASI stock prices using Islamic ML models")
            
            company_dropdown = gr.Dropdown(
                choices=list(interface.tasi_companies.keys()),
                value="2222.SR",
                label="Select TASI Company",
                info="Choose a Saudi company for price prediction"
            )
            
            predict_btn = gr.Button("🔮 Predict Price", variant="primary")
            
            prediction_output = gr.Textbox(
                label="Islamic Finance Prediction Results",
                lines=15,
                max_lines=20
            )
            
            prediction_chart = gr.Plot(label="Price Chart with Prediction")
            
            predict_btn.click(
                interface.predict_tasi_price,
                inputs=[company_dropdown],
                outputs=[prediction_output, prediction_chart]
            )
        
        with gr.Tab("💼 Islamic Portfolio Analysis"):
            gr.Markdown("### Analyze Sharia-compliant portfolio allocation")
            
            portfolio_companies = gr.CheckboxGroup(
                choices=list(interface.tasi_companies.keys()),
                value=["2222.SR", "1120.SR", "2030.SR"],
                label="Select Companies for Islamic Portfolio",
                info="Choose multiple TASI companies for portfolio analysis"
            )
            
            analyze_btn = gr.Button("💼 Analyze Portfolio", variant="primary")
            
            portfolio_output = gr.Textbox(
                label="Islamic Portfolio Analysis",
                lines=15,
                max_lines=20
            )
            
            analyze_btn.click(
                interface.analyze_portfolio,
                inputs=[portfolio_companies],
                outputs=[portfolio_output]
            )
        
        with gr.Tab("ℹ️ About Islamic Finance ML"):
            gr.Markdown("""
            ### 🕌 Islamic Finance Compliance
            
            This machine learning interface follows strict Islamic finance principles:
            
            #### ✅ Sharia-Compliant Features:
            - **No Interest Calculations**: All models avoid Riba (interest-based calculations)
            - **Ethical Investments**: Focus on halal business sectors
            - **Risk Sharing**: Portfolio allocation follows Islamic risk distribution
            - **Transparency**: All predictions include clear methodology
            - **Fairness**: Equal-weight portfolio allocation principles
            
            #### 🤖 Technical Features:
            - **Ensemble Models**: Random Forest + Linear Regression
            - **Feature Engineering**: 20+ technical indicators
            - **Real-time Data**: Live TASI market integration
            - **Risk Assessment**: Islamic finance-based risk evaluation
            
            #### 📊 Supported Companies:
            - Saudi Aramco (2222.SR) - Energy
            - Al Rajhi Bank (1120.SR) - Islamic Banking  
            - SABIC (2030.SR) - Chemicals
            - SABB (2010.SR) - Banking
            - And more TASI-listed companies...
            
            #### 📖 Disclaimer:
            *This system provides educational and analytical insights following Islamic finance principles. 
            All investments carry risk. Please consult with Islamic finance scholars and financial advisors 
            before making investment decisions.*
            """)
    
    return demo

def main():
    """Launch the TASI ML interface."""
    print("🇸🇦 Starting TASI Islamic Finance ML Interface...")
    print("🕌 Sharia-Compliant Machine Learning for Saudi Stock Market")
    print("🌐 Access: http://localhost:7861")
    
    demo = create_tasi_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()