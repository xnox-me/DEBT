#!/usr/bin/env python3
"""
DEBT Gradio ML Interface
Interactive business intelligence and ML model demonstrations with Gradio.
"""

import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import joblib
from pathlib import Path
import json
import sys
import os

# Add the ml_pipeline directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from train_models import BusinessMLPipeline

class GradioMLInterface:
    """Interactive ML interface for DEBT business intelligence demonstrations."""
    
    def __init__(self):
        """Initialize the Gradio ML interface."""
        
        self.pipeline = BusinessMLPipeline("DEBT_Gradio_Demo")
        self.models_loaded = False
        
        # Try to load existing models
        self.load_existing_models()
        
        # Business data for demos
        self.sample_business_data = self.generate_sample_data()
        
    def load_existing_models(self):
        """Load pre-trained models if available."""
        
        models_dir = Path("models")
        if models_dir.exists():
            try:
                self.pipeline.load_models("models")
                self.models_loaded = True
                print("✅ Pre-trained models loaded successfully")
            except Exception as e:
                print(f"⚠️ Could not load pre-trained models: {e}")
                self.models_loaded = False
        else:
            print("ℹ️ No pre-trained models found. Training new models...")
            self.train_demo_models()
    
    def train_demo_models(self):
        """Train models for demonstration purposes."""
        
        try:
            # Train business models
            business_results = self.pipeline.train_business_models()
            
            # Save models
            self.pipeline.save_models("models")
            self.models_loaded = True
            
            print("✅ Demo models trained and saved")
            
        except Exception as e:
            print(f"❌ Failed to train demo models: {e}")
            self.models_loaded = False
    
    def generate_sample_data(self):
        """Generate sample business data for demonstrations."""
        
        return {
            'customer_profile_1': {
                'customer_age': 35,
                'income': 65000,
                'credit_score': 720,
                'months_as_customer': 18,
                'num_products': 2,
                'monthly_charges': 85,
                'total_charges': 1530,
                'satisfaction_score': 8,
                'support_tickets': 1
            },
            'customer_profile_2': {
                'customer_age': 45,
                'income': 45000,
                'credit_score': 650,
                'months_as_customer': 36,
                'num_products': 1,
                'monthly_charges': 45,
                'total_charges': 1620,
                'satisfaction_score': 5,
                'support_tickets': 4
            },
            'sales_scenario_1': {
                'customer_age': 30,
                'income': 75000,
                'num_products': 3,
                'satisfaction_score': 9,
                'months_as_customer': 12
            }
        }
    
    def predict_customer_churn(self, age, income, credit_score, months_customer, 
                             num_products, monthly_charges, satisfaction_score, support_tickets):
        """Predict customer churn probability."""
        
        if not self.models_loaded:
            return "❌ Models not available. Please train models first.", None
        
        try:
            # Calculate total charges
            total_charges = monthly_charges * months_customer
            
            # Prepare features
            features = np.array([age, income, credit_score, months_customer, 
                               num_products, monthly_charges, total_charges, 
                               satisfaction_score, support_tickets])
            
            # Make prediction
            result = self.pipeline.predict('customer_churn', features)
            
            churn_prob = result['probability'][1] if result['probability'] is not None else 0.5
            churn_prediction = "High Risk" if result['prediction'] == 1 else "Low Risk"
            
            # Risk assessment
            if churn_prob > 0.7:
                risk_level = "🔴 Very High Risk"
                recommendations = [
                    "Immediate retention campaign needed",
                    "Offer premium support package", 
                    "Consider discount or loyalty rewards",
                    "Schedule personal account review"
                ]
            elif churn_prob > 0.5:
                risk_level = "🟡 Moderate Risk" 
                recommendations = [
                    "Monitor account closely",
                    "Proactive customer outreach",
                    "Improve satisfaction score",
                    "Consider product upsell"
                ]
            else:
                risk_level = "🟢 Low Risk"
                recommendations = [
                    "Customer is likely to stay",
                    "Focus on cross-selling opportunities",
                    "Maintain current service level",
                    "Consider for referral program"
                ]
            
            # Create visualization
            fig = go.Figure()
            
            # Churn probability gauge
            fig.add_trace(go.Indicator(
                mode = "gauge+number",
                value = churn_prob * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Churn Risk Probability (%)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkred" if churn_prob > 0.7 else "orange" if churn_prob > 0.5 else "darkgreen"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgray"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            
            # Business insights
            analysis = f"""
## 🎯 Business Analysis Results

**Customer Risk Level:** {risk_level}
**Churn Probability:** {churn_prob:.1%}
**Model Prediction:** {churn_prediction}
**Model Used:** {result['model_name']}

### 📊 Key Risk Factors:
- **Satisfaction Score:** {'⚠️ Low' if satisfaction_score < 6 else '✅ Good'}
- **Support Tickets:** {'⚠️ High' if support_tickets > 2 else '✅ Normal'}
- **Customer Tenure:** {'⚠️ New' if months_customer < 12 else '✅ Established'}
- **Monthly Charges:** {'⚠️ High' if monthly_charges > 100 else '✅ Reasonable'}

### 💡 Business Recommendations:
"""
            for rec in recommendations:
                analysis += f"- {rec}\n"
            
            return analysis, fig
            
        except Exception as e:
            return f"❌ Error making prediction: {str(e)}", None
    
    def predict_sales_forecast(self, age, income, num_products, satisfaction_score, months_customer):
        """Predict monthly sales for a customer."""
        
        if not self.models_loaded:
            return "❌ Models not available. Please train models first.", None
        
        try:
            # Prepare features  
            features = np.array([age, income, num_products, satisfaction_score, months_customer])
            
            # Make prediction
            result = self.pipeline.predict('sales_forecasting', features)
            predicted_sales = result['prediction']
            
            # Sales category
            if predicted_sales > 200:
                category = "🔥 High Value"
                color = "green"
            elif predicted_sales > 100:
                category = "📊 Medium Value"
                color = "orange"
            else:
                category = "📉 Low Value"  
                color = "red"
            
            # Create sales visualization
            fig = go.Figure()
            
            # Sales prediction bar
            fig.add_trace(go.Bar(
                x=['Predicted Monthly Sales'],
                y=[predicted_sales],
                marker_color=color,
                text=[f'${predicted_sales:.2f}'],
                textposition='auto',
                name='Sales Prediction'
            ))
            
            # Add benchmark lines
            fig.add_hline(y=200, line_dash="dash", line_color="green", 
                         annotation_text="High Value Threshold")
            fig.add_hline(y=100, line_dash="dash", line_color="orange",
                         annotation_text="Medium Value Threshold")
            
            fig.update_layout(
                title="Monthly Sales Prediction",
                yaxis_title="Sales ($)",
                showlegend=False
            )
            
            # Business analysis
            analysis = f"""
## 💰 Sales Forecast Analysis

**Predicted Monthly Sales:** ${predicted_sales:.2f}
**Customer Category:** {category}
**Model Used:** {result['model_name']}

### 📈 Business Insights:
- **Revenue Potential:** {'High - prioritize for upselling' if predicted_sales > 150 else 'Moderate - focus on retention' if predicted_sales > 75 else 'Low - consider cost optimization'}
- **Product Opportunity:** {'Cross-sell additional products' if num_products < 3 else 'Customer is well-served'}
- **Relationship Status:** {'Long-term customer' if months_customer > 24 else 'Developing relationship'}

### 🎯 Action Items:
- **Account Management:** {'Assign premium account manager' if predicted_sales > 150 else 'Regular account management'}
- **Marketing Focus:** {'Premium product offerings' if predicted_sales > 150 else 'Value-focused communications'}
- **Support Level:** {'Priority support queue' if predicted_sales > 150 else 'Standard support'}
"""
            
            return analysis, fig
            
        except Exception as e:
            return f"❌ Error making prediction: {str(e)}", None
    
    def analyze_stock_performance(self, symbol, period):
        """Analyze stock performance and make predictions."""
        
        try:
            # Fetch stock data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return f"❌ No data available for {symbol}", None
            
            # Calculate basic metrics
            current_price = df['Close'].iloc[-1]
            price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2] if len(df) > 1 else 0
            price_change_pct = (price_change / df['Close'].iloc[-2] * 100) if len(df) > 1 else 0
            
            # Create stock chart
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(f'{symbol} Stock Price', 'Volume'),
                row_heights=[0.7, 0.3]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'], 
                    low=df['Low'],
                    close=df['Close'],
                    name="Price"
                ), row=1, col=1
            )
            
            # Moving averages
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_20'], 
                name='SMA 20', line=dict(color='orange')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_50'],
                name='SMA 50', line=dict(color='red') 
            ), row=1, col=1)
            
            # Volume
            fig.add_trace(go.Bar(
                x=df.index, y=df['Volume'],
                name='Volume', marker_color='blue'
            ), row=2, col=1)
            
            fig.update_layout(
                title=f"{symbol} Technical Analysis",
                height=600,
                xaxis_rangeslider_visible=False
            )
            
            # Technical analysis
            sma_signal = "Bullish" if df['Close'].iloc[-1] > df['SMA_20'].iloc[-1] else "Bearish"
            trend = "Uptrend" if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1] else "Downtrend"
            
            analysis = f"""
## 📈 Stock Analysis: {symbol}

**Current Price:** ${current_price:.2f}
**Price Change:** ${price_change:.2f} ({price_change_pct:+.2f}%)
**Short-term Signal:** {sma_signal}
**Overall Trend:** {trend}

### 🔍 Technical Indicators:
- **20-day SMA:** ${df['SMA_20'].iloc[-1]:.2f}
- **50-day SMA:** ${df['SMA_50'].iloc[-1]:.2f}
- **Average Volume:** {df['Volume'].rolling(20).mean().iloc[-1]:,.0f}

### 💡 Investment Insights:
- **Momentum:** {'Positive' if price_change_pct > 0 else 'Negative'}
- **Volatility:** {'High' if df['Close'].pct_change().std() * 100 > 3 else 'Moderate'}
- **Volume Trend:** {'Above Average' if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] else 'Below Average'}
"""
            
            return analysis, fig
            
        except Exception as e:
            return f"❌ Error analyzing stock: {str(e)}", None
    
    def create_interface(self):
        """Create the Gradio interface."""
        
        with gr.Blocks(
            title="DEBT Business Intelligence ML Suite",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                font-family: 'Arial', sans-serif;
            }
            .gr-button-primary {
                background: linear-gradient(90deg, #1f77b4, #2ca02c);
                border: none;
            }
            """
        ) as interface:
            
            gr.Markdown("""
            # 🏦 DEBT Business Intelligence & ML Suite
            ### Advanced Machine Learning Demonstrations for Business Intelligence
            
            Explore sophisticated ML models for customer analytics, sales forecasting, and financial analysis.
            """)
            
            with gr.Tabs():
                
                # Customer Churn Analysis
                with gr.Tab("🎯 Customer Churn Analysis"):
                    gr.Markdown("### Predict Customer Churn Risk with Advanced ML Models")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("#### Customer Demographics")
                            age = gr.Slider(18, 80, value=35, label="Customer Age")
                            income = gr.Slider(20000, 200000, value=65000, step=5000, label="Annual Income ($)")
                            credit_score = gr.Slider(300, 850, value=720, label="Credit Score")
                            
                            gr.Markdown("#### Account Information") 
                            months_customer = gr.Slider(1, 60, value=18, label="Months as Customer")
                            num_products = gr.Slider(1, 5, value=2, label="Number of Products")
                            monthly_charges = gr.Slider(20, 200, value=85, label="Monthly Charges ($)")
                            
                            gr.Markdown("#### Service Experience")
                            satisfaction_score = gr.Slider(1, 10, value=8, label="Satisfaction Score")
                            support_tickets = gr.Slider(0, 10, value=1, label="Support Tickets (Last 6 Months)")
                            
                            churn_predict_btn = gr.Button("🔍 Analyze Churn Risk", variant="primary")
                        
                        with gr.Column(scale=2):
                            churn_analysis = gr.Markdown()
                            churn_plot = gr.Plot()
                    
                    # Sample customer buttons
                    with gr.Row():
                        gr.Markdown("#### Quick Test with Sample Customers:")
                        sample1_btn = gr.Button("👤 Low Risk Customer")
                        sample2_btn = gr.Button("⚠️ High Risk Customer")
                    
                    # Event handlers for churn analysis
                    churn_predict_btn.click(
                        self.predict_customer_churn,
                        inputs=[age, income, credit_score, months_customer, num_products, 
                               monthly_charges, satisfaction_score, support_tickets],
                        outputs=[churn_analysis, churn_plot]
                    )
                    
                    def load_sample_customer_1():
                        sample = self.sample_business_data['customer_profile_1']
                        return (sample['customer_age'], sample['income'], sample['credit_score'],
                               sample['months_as_customer'], sample['num_products'], 
                               sample['monthly_charges'], sample['satisfaction_score'], 
                               sample['support_tickets'])
                    
                    def load_sample_customer_2():
                        sample = self.sample_business_data['customer_profile_2'] 
                        return (sample['customer_age'], sample['income'], sample['credit_score'],
                               sample['months_as_customer'], sample['num_products'],
                               sample['monthly_charges'], sample['satisfaction_score'],
                               sample['support_tickets'])
                    
                    sample1_btn.click(
                        load_sample_customer_1,
                        outputs=[age, income, credit_score, months_customer, num_products,
                                monthly_charges, satisfaction_score, support_tickets]
                    )
                    
                    sample2_btn.click(
                        load_sample_customer_2, 
                        outputs=[age, income, credit_score, months_customer, num_products,
                                monthly_charges, satisfaction_score, support_tickets]
                    )
                
                # Sales Forecasting
                with gr.Tab("💰 Sales Forecasting"):
                    gr.Markdown("### Predict Customer Sales Potential with ML Models")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("#### Customer Profile")
                            sales_age = gr.Slider(18, 80, value=30, label="Customer Age")
                            sales_income = gr.Slider(20000, 200000, value=75000, step=5000, label="Annual Income ($)")
                            sales_products = gr.Slider(1, 5, value=3, label="Current Products")
                            sales_satisfaction = gr.Slider(1, 10, value=9, label="Satisfaction Score")
                            sales_tenure = gr.Slider(1, 60, value=12, label="Months as Customer")
                            
                            sales_predict_btn = gr.Button("📊 Forecast Sales", variant="primary")
                        
                        with gr.Column(scale=2):
                            sales_analysis = gr.Markdown()
                            sales_plot = gr.Plot()
                    
                    sales_predict_btn.click(
                        self.predict_sales_forecast,
                        inputs=[sales_age, sales_income, sales_products, sales_satisfaction, sales_tenure],
                        outputs=[sales_analysis, sales_plot]
                    )
                
                # Stock Analysis
                with gr.Tab("📈 Stock Market Analysis"):
                    gr.Markdown("### Advanced Stock Analysis with Technical Indicators")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            stock_symbol = gr.Textbox("AAPL", label="Stock Symbol")
                            stock_period = gr.Dropdown(
                                choices=["1mo", "3mo", "6mo", "1y", "2y"],
                                value="6mo",
                                label="Analysis Period"
                            )
                            
                            analyze_stock_btn = gr.Button("📊 Analyze Stock", variant="primary")
                            
                            gr.Markdown("""
                            #### Popular Stocks to Analyze:
                            - **Tech:** AAPL, MSFT, GOOGL, AMZN
                            - **Finance:** JPM, BAC, GS  
                            - **ETFs:** SPY, QQQ, VTI
                            """)
                        
                        with gr.Column(scale=2):
                            stock_analysis = gr.Markdown()
                            stock_plot = gr.Plot()
                    
                    analyze_stock_btn.click(
                        self.analyze_stock_performance,
                        inputs=[stock_symbol, stock_period],
                        outputs=[stock_analysis, stock_plot]
                    )
                
                # Model Information
                with gr.Tab("🤖 Model Information"):
                    gr.Markdown(f"""
                    ### DEBT ML Pipeline Status
                    
                    **Models Loaded:** {'✅ Yes' if self.models_loaded else '❌ No'}
                    
                    #### Available Models:
                    
                    **1. Customer Churn Prediction**
                    - **Type:** Binary Classification
                    - **Algorithm:** Ensemble (Random Forest, XGBoost, Logistic Regression)
                    - **Features:** Customer demographics, account info, service experience
                    - **Business Value:** Proactive customer retention, reduce churn costs
                    
                    **2. Sales Forecasting**
                    - **Type:** Regression
                    - **Algorithm:** Ensemble (Gradient Boosting, XGBoost, Random Forest)  
                    - **Features:** Customer profile and behavior patterns
                    - **Business Value:** Revenue optimization, resource planning
                    
                    **3. Stock Analysis** (Future ML Integration)
                    - **Type:** Technical Analysis + ML Predictions
                    - **Features:** Price action, volume, technical indicators
                    - **Business Value:** Investment insights, risk assessment
                    
                    #### MLflow Experiment Tracking:
                    - **Experiment Management:** Comprehensive model versioning
                    - **Metrics Tracking:** Performance monitoring across all models
                    - **Model Registry:** Centralized model storage and deployment
                    - **Comparison Tools:** A/B testing and model performance comparison
                    
                    #### Business Intelligence Features:
                    - **Real-time Predictions:** Instant business insights
                    - **Risk Assessment:** Automated risk scoring and alerts  
                    - **Decision Support:** Data-driven business recommendations
                    - **Performance Monitoring:** Continuous model and business KPI tracking
                    """)
            
            gr.Markdown("""
            ---
            ### 🏢 DEBT Business Intelligence Suite
            **Powered by:** MLflow • Scikit-learn • XGBoost • Gradio • Advanced Business Analytics
            
            **Features:** Real-time ML predictions • Business intelligence • Risk assessment • Sales optimization
            """)
        
        return interface

def main():
    """Launch the Gradio ML interface."""
    
    print("🤖 Starting DEBT Gradio ML Interface...")
    
    # Initialize interface
    ml_interface = GradioMLInterface()
    
    # Create and launch Gradio app
    interface = ml_interface.create_interface()
    
    # Launch with business-friendly settings
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()