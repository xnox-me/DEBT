#!/bin/bash

# DEBT Master Business Intelligence Startup Script
# Comprehensive startup for all business intelligence suites

echo "🚀 DEBT Business Intelligence Master Startup"
echo "============================================="
echo ""
echo "Available Business Intelligence Suites:"
echo ""
echo "1. 📊 Original Sophisticated Example (Port 8501)"
echo "2. 🇸🇦 TASI Market Intelligence (Islamic Finance)"
echo "3. 🌍 Global Markets & Crypto Intelligence"
echo "4. 🌐 API Plugin (Unified Gateway - Port 9000)"
echo "5. 🔄 All Suites (Complete Platform)"
echo "6. Exit"
echo ""
read -p "Select suite to start [1-6]: " choice

case $choice in
    1)
        echo "📊 Starting Original Sophisticated Example..."
        cd sophisticated_example
        if [ -f "start_all_services.sh" ]; then
            ./start_all_services.sh
        else
            echo "Starting individual components..."
            cd financial_dashboard && ./start_dashboard.sh &
            cd ../ml_pipeline && ./start_ml_services.sh &
            cd ../api_services && python main.py &
            wait
        fi
        ;;
    2)
        echo "🇸🇦 Starting TASI Market Intelligence Suite..."
        echo "Islamic Finance-Compliant Business Intelligence"
        echo ""
        echo "Choose TASI components:"
        echo "1. Financial Dashboard (Port 8502)"
        echo "2. ML Services (MLflow 5001 + Gradio 7861)"
        echo "3. API Services (Port 8003)"
        echo "4. All TASI Components"
        echo ""
        read -p "Enter choice [1-4]: " tasi_choice
        
        case $tasi_choice in
            1)
                cd tasi_market_intelligence/financial_dashboard
                ./start_tasi_dashboard.sh
                ;;
            2)
                cd tasi_market_intelligence/ml_pipeline
                ./start_ml_services.sh
                ;;
            3)
                cd tasi_market_intelligence/api_services
                python main.py
                ;;
            4)
                echo "🚀 Starting all TASI services..."
                cd tasi_market_intelligence/financial_dashboard
                ./start_tasi_dashboard.sh &
                sleep 2
                cd ../ml_pipeline
                ./start_ml_services.sh &
                sleep 2
                cd ../api_services
                python main.py &
                echo ""
                echo "✅ All TASI services starting!"
                echo "📊 Dashboard: http://localhost:8502"
                echo "🤖 ML Interface: http://localhost:7861"
                echo "📈 MLflow: http://localhost:5001"
                echo "🌐 API: http://localhost:8003"
                wait
                ;;
        esac
        ;;
    3)
        echo "🌍 Starting Global Markets & Crypto Intelligence..."
        echo "International Markets + Cryptocurrency Analysis"
        echo ""
        echo "Choose Global Markets components:"
        echo "1. Global Markets Dashboard (Port 8504)"
        echo "2. ML & Analytics Services"
        echo "3. All Global Components"
        echo ""
        read -p "Enter choice [1-3]: " global_choice
        
        case $global_choice in
            1)
                cd global_markets_intelligence/financial_dashboard
                ./start_global_dashboard.sh
                ;;
            2)
                echo "🤖 Starting Global Markets ML services..."
                cd global_markets_intelligence/ml_pipeline
                mlflow server --host 0.0.0.0 --port 5002 &
                echo "📈 MLflow UI: http://localhost:5002"
                wait
                ;;
            3)
                echo "🚀 Starting all Global Markets services..."
                cd global_markets_intelligence/financial_dashboard
                ./start_global_dashboard.sh &
                sleep 2
                cd ../ml_pipeline
                mlflow server --host 0.0.0.0 --port 5002 &
                echo ""
                echo "✅ All Global Markets services starting!"
                echo "🌍 Dashboard: http://localhost:8504"
                echo "📈 MLflow: http://localhost:5002"
                wait
                ;;
        esac
        ;;
    4)
        echo "🌐 Starting DEBT API Plugin (Unified Gateway)..."
        ./start_api_plugin.sh
        ;;
    5)
        echo "🔄 Starting ALL Business Intelligence Suites..."
        echo "This will start all available suites simultaneously"
        echo ""
        echo "⚠️  Warning: This requires significant system resources"
        echo "💻 Recommended: 8GB+ RAM and modern CPU"
        echo ""
        read -p "Continue? [y/N]: " confirm
        
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo "🚀 Starting complete DEBT Business Intelligence Platform..."
            
            # Start Original Suite
            echo "📊 Starting Original Suite..."
            cd sophisticated_example/financial_dashboard
            ./start_dashboard.sh &
            cd ../api_services
            python main.py &
            
            # Start TASI Suite
            echo "🇸🇦 Starting TASI Suite..."
            cd ../../tasi_market_intelligence/financial_dashboard
            ./start_tasi_dashboard.sh &
            cd ../api_services
            python main.py &
            
            # Start Global Markets Suite
            echo "🌍 Starting Global Markets Suite..."
            cd ../../global_markets_intelligence/financial_dashboard
            ./start_global_dashboard.sh &
            
            # Start API Plugin
            echo "🌐 Starting API Plugin..."
            cd ../../
            python api_plugin.py &
            
            # Start MLflow servers
            echo "📈 Starting MLflow servers..."
            cd sophisticated_example && mlflow ui --host 0.0.0.0 --port 5000 &
            cd ../tasi_market_intelligence/ml_pipeline && mlflow server --host 0.0.0.0 --port 5001 &
            cd ../../global_markets_intelligence/ml_pipeline && mlflow server --host 0.0.0.0 --port 5002 &
            
            echo ""
            echo "🎉 Complete DEBT Business Intelligence Platform Started!"
            echo "=================================================="
            echo ""
            echo "📊 Original Suite:"
            echo "   • Dashboard: http://localhost:8501"
            echo "   • API: http://localhost:8000"
            echo "   • MLflow: http://localhost:5000"
            echo ""
            echo "🇸🇦 TASI Islamic Finance Suite:"
            echo "   • Dashboard: http://localhost:8502"
            echo "   • ML Interface: http://localhost:7861"
            echo "   • API: http://localhost:8003"
            echo "   • MLflow: http://localhost:5001"
            echo ""
            echo "🌍 Global Markets Suite:"
            echo "   • Dashboard: http://localhost:8504"
            echo "   • MLflow: http://localhost:5002"
            echo ""
            echo "🌐 Unified API Gateway:"
            echo "   • Main Gateway: http://localhost:9000"
            echo "   • Documentation: http://localhost:9000/api/docs"
            echo ""
            echo "💡 Tip: Use the API Gateway for unified access to all services"
            echo "🔧 Management: All services running in background"
            echo ""
            echo "Press Ctrl+C to stop all services"
            wait
        else
            echo "❌ Startup cancelled"
        fi
        ;;
    6)
        echo "👋 Exiting DEBT Business Intelligence Master Startup"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Please try again."
        sleep 2
        exec "$0"
        ;;
esac