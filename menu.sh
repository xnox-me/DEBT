#!/bin/bash

# Interactive menu for DEBT - Development Environment & Business Tools

# Activate virtual environment if it exists
VENV_PATH="$HOME/.debt-env"
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi

# --- Functions ---
show_menu() {
    clear
    echo "*********************************************"
    echo "*    Welcome to DEBT (Development          *"
    echo "*    Environment & Business Tools)         *"
    echo "*********************************************"
    echo "1. Start Neovim (Advanced Code Editor)"
    echo "2. Start n8n (Business Workflow Automation)"
    echo "3. Open Bash Shell (Command Line Interface)"
    echo "4. Start Lean Project (Mathematical Proofs)"
    echo "5. Start OpenBB (Financial Data & Analysis)"
    echo "6. Start ShellGPT (AI Business Assistant)"
    echo "7. Start Shellngn Pro (Remote Business Access)"
    echo "8. Start ML/AI (Business Intelligence Tools)"
    echo "9. 🌐 API Plugin (Unified Business Intelligence Gateway)"
    echo "10. 🔑 Key Management Portal (API Keys & Credentials)"
    echo "11. Exit DEBT Environment"
    echo "*********************************************"
}

start_neovim() {
    clear
    echo "Starting Neovim - Advanced Code Editor for DEBT..."
    nvim
}

start_n8n() {
    clear
    echo "Starting n8n - Business Workflow Automation..."
    echo "Access the business automation editor at http://localhost:5678"
    echo "Create workflows for business processes, data integration, and automation."
    echo "Press Ctrl+C to stop n8n."
    n8n
}

open_shell() {
    clear
    echo "Starting Bash shell..."
    bash
}

start_lean_project() {
    clear
    echo "Starting a new Lean project..."
    echo "Please enter a name for your new Lean project:"
    read -r project_name
    if [ -z "$project_name" ]; then
        echo "Project name cannot be empty."
        sleep 2
        return
    fi
    lake new "$project_name"
    echo "New Lean project '$project_name' created."
    echo "You can now open it in Neovim."
    sleep 2
}

start_openbb() {
    clear
    echo "Starting OpenBB - Financial Data & Market Analysis Platform..."
    echo "Loading comprehensive financial data and business intelligence tools..."
    echo "Access market data, financial analytics, and business insights."
    echo "Type 'exit' or use Ctrl+C to return to the DEBT main menu."
    source "$VENV_PATH/bin/activate" 2>/dev/null
    python3 -c "try:
    import openbb
    openbb.obb.account.login_guest()
    from openbb import obb
    print('OpenBB Financial Terminal Ready for Business Analysis!')
except ImportError:
    print('OpenBB not available. Starting Python with financial & business libraries...')
    import pandas as pd
    import numpy as np
    print('Available for business analysis: pandas, numpy, matplotlib, scikit-learn')
finally:
    import IPython
    IPython.embed()"
}

start_shellgpt() {
    clear
    echo "Starting ShellGPT - AI-Powered Business & Development Assistant..."
    echo "Your intelligent assistant for business automation and development tasks!"
    echo "Business Examples:"
    echo "  sgpt 'analyze quarterly sales data trends'"
    echo "  sgpt --code 'create a financial dashboard script'"
    echo "  sgpt --shell 'find all business reports from last month'"
    echo "  sgpt 'suggest workflow automation for invoice processing'"
    echo "Type 'exit' or use Ctrl+C to return to the DEBT main menu."
    echo ""
    echo "Starting interactive shell with AI business assistance..."
    source "$VENV_PATH/bin/activate" 2>/dev/null
    bash
}

start_shellngn() {
    clear
    echo "Starting Shellngn Pro (SSH/SFTP/VNC/RDP Web Client)..."
    echo "======================================================"
    echo ""
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not available. Shellngn Pro requires Docker to run."
        echo "   Please ensure Docker is installed and running."
        sleep 3
        return
    fi
    
    # Check if Shellngn container is already running
    if docker ps | grep -q "shellngn"; then
        echo "ℹ️  Shellngn Pro is already running!"
        echo "   Access it at: http://localhost:8080"
    else
        echo "🚀 Starting Shellngn Pro container..."
        # Pull the latest image if not available
        docker pull shellngn/pro
        
        # Start Shellngn Pro container
        docker run -d --name shellngn -p 8080:8080 -v "$(pwd)/shellngn-data:/data" shellngn/pro
        
        if [ $? -eq 0 ]; then
            echo "✅ Shellngn Pro started successfully!"
            echo ""
            echo "🌐 Access Shellngn Pro at: http://localhost:8080"
            echo "📁 Data persistence: $(pwd)/shellngn-data"
            echo ""
            echo "Features available:"
            echo "  • SSH/Telnet Terminal Access"
            echo "  • SFTP File Transfer & Browser"
            echo "  • VNC/RDP Remote Desktop"
            echo "  • Multi-session Management"
            echo "  • Device & Identity Management"
        else
            echo "❌ Failed to start Shellngn Pro container."
        fi
    fi
    
    echo ""
    echo "Management commands:"
    echo "  • Stop:  docker stop shellngn && docker rm shellngn"
    echo "  • Logs:  docker logs shellngn"
    echo "  • Status: docker ps | grep shellngn"
    echo ""
    echo "Press Enter to return to main menu..."
    read -r
}

start_ml_ai_env() {
    clear
    echo "🏢 DEBT Business Intelligence & ML/AI Environment"
    echo "================================================="
    echo ""
    echo "Choose your business intelligence and ML/AI tool:"
    echo "1. JupyterLab (Business Analytics & Data Science)"
    echo "2. Jupyter Notebook (Financial Modeling & Analysis)"
    echo "3. Python BI/ML REPL (Interactive Business Intelligence)"
    echo "4. TensorBoard (ML Model Performance Visualization)"
    echo "5. Gradio (Business ML Demo Server)"
    echo "6. Streamlit (Business Intelligence Dashboards)"
    echo "7. MLflow UI (Business ML Experiment Tracking)"
    echo "8. Return to DEBT main menu"
    echo ""
    read -p "Enter your choice [1-8]: " ml_choice
    
    case $ml_choice in
        1)
            echo "🚀 Starting JupyterLab for Business Analytics..."
            echo "Access your business intelligence workspace at: http://localhost:8888"
            echo "Perfect for financial modeling, data analysis, and business insights."
            echo "Token will be displayed below:"
            source "$VENV_PATH/bin/activate" 2>/dev/null
            jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
            ;;
        2)
            echo "🚀 Starting Jupyter Notebook for Financial Analysis..."
            echo "Access your financial modeling environment at: http://localhost:8888"
            echo "Ideal for business reports, financial calculations, and market analysis."
            echo "Token will be displayed below:"
            source "$VENV_PATH/bin/activate" 2>/dev/null
            jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
            ;;
        3)
            echo "💼 Starting Python Business Intelligence REPL..."
            echo "Interactive environment with business analytics libraries loaded."
            echo "Available: pandas, numpy, scikit-learn, matplotlib, financial analysis tools"
            echo "Type 'exit()' to return to DEBT menu."
            echo ""
            source "$VENV_PATH/bin/activate" 2>/dev/null
            python3 -c "
import sys
print('💼 DEBT Business Intelligence Python Environment Ready!')
print('📊 Available business analytics libraries:')
try:
    import sklearn
    print(f'  ✓ scikit-learn {sklearn.__version__}')
except: print('  ✗ scikit-learn not available')
try:
    import pandas as pd
    print(f'  ✓ pandas {pd.__version__}')
except: print('  ✗ pandas not available')
try:
    import numpy as np
    print(f'  ✓ numpy {np.__version__}')
except: print('  ✗ numpy not available')
try:
    import matplotlib
    print(f'  ✓ matplotlib {matplotlib.__version__}')
except: print('  ✗ matplotlib not available')
try:
    import seaborn
    print(f'  ✓ seaborn {seaborn.__version__}')
except: print('  ✗ seaborn not available')
print('\n💡 Quick start examples:')
print('  import pandas as pd')
print('  import numpy as np')
print('  from sklearn.datasets import load_iris')
print('')
import IPython
IPython.embed()
"
            ;;
        4)
            echo "📊 Starting TensorBoard..."
            echo "Access at: http://localhost:6006"
            echo "Monitoring logs in: ./logs"
            mkdir -p ./logs
            tensorboard --logdir=./logs --host=0.0.0.0 --port=6006
            ;;
        5)
            echo "🎯 Starting Gradio for Business ML Demos..."
            echo "Creating interactive business intelligence demos and ML applications."
            echo "Perfect for showcasing business models and analytics to stakeholders."
            source "$VENV_PATH/bin/activate" 2>/dev/null
            python3 -c "
import gradio as gr
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load and train a simple model
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)

def predict_iris(sepal_length, sepal_width, petal_length, petal_width):
    features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    species = iris.target_names[prediction]
    confidence = max(probability)
    return f'Species: {species} (Confidence: {confidence:.2f})'

interface = gr.Interface(
    fn=predict_iris,
    inputs=[
        gr.Number(label='Sepal Length'),
        gr.Number(label='Sepal Width'),
        gr.Number(label='Petal Length'),
        gr.Number(label='Petal Width')
    ],
    outputs=gr.Text(label='Prediction'),
    title='🏢 Business Iris Classifier',
    description='Business Intelligence Demo: Enter flower measurements to predict iris species for botanical analysis'
)

print('🎯 Business ML Demo ready at: http://localhost:7860')
interface.launch(server_name='0.0.0.0', server_port=7860)
"
            ;;
        6)
            echo "📊 Starting Streamlit for Business Intelligence Dashboards..."
            echo "Building interactive business dashboards and data applications."
            echo "Ideal for executive dashboards, KPI tracking, and business reporting."
            source "$VENV_PATH/bin/activate" 2>/dev/null
            cat > /tmp/ml_streamlit_app.py << 'EOF'
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris, load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

st.set_page_config(page_title='📈 DEBT Business Intelligence', page_icon='📈')

st.title('📈 DEBT Business Intelligence Dashboard')
st.sidebar.title('📊 Dataset Selection')

# Dataset selection
dataset_name = st.sidebar.selectbox('Choose Dataset', ['Iris', 'Wine'])

if dataset_name == 'Iris':
    data = load_iris()
else:
    data = load_wine()

df = pd.DataFrame(data.data, columns=data.feature_names)
df['target'] = data.target

st.subheader(f'📈 {dataset_name} Dataset Overview')
st.write(f'**Shape:** {df.shape}')
st.write(f'**Features:** {len(data.feature_names)}')
st.write(f'**Classes:** {len(data.target_names)}')

# Display data
if st.checkbox('Show raw data'):
    st.write(df.head())

# Visualizations
st.subheader('📊 Data Visualization')
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.histplot(data=df, x=df.columns[0], hue='target', ax=ax)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=df.columns[0], y=df.columns[1], hue='target', ax=ax)
    st.pyplot(fig)

# Model training
st.subheader('🤖 Model Training')
test_size = st.slider('Test Size', 0.1, 0.5, 0.2)
n_estimators = st.slider('Number of Estimators', 10, 200, 100)

X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=test_size, random_state=42
)

model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
st.write(f'**Accuracy:** {accuracy:.3f}')

if st.checkbox('Show classification report'):
    report = classification_report(y_test, y_pred, target_names=data.target_names)
    st.text(report)
EOF
            source "$VENV_PATH/bin/activate" 2>/dev/null
            streamlit run /tmp/ml_streamlit_app.py --server.address 0.0.0.0 --server.port 8501
            ;;
        7)
            echo "📈 Starting MLflow for Business ML Experiment Tracking..."
            echo "Access business ML experiment tracking at: http://localhost:5000"
            echo "Perfect for tracking business model performance and ROI."
            echo "Tracking experiments in: ./mlruns"
            mkdir -p ./mlruns
            mlflow ui --host 0.0.0.0 --port 5000
            ;;
        8)
            return
            ;;
        *)
            echo "Invalid option. Please try again."
            sleep 2
            start_ml_ai_env
            ;;
    esac
    
    echo ""
    echo "Press Enter to return to ML/AI menu..."
    read -r
    start_ml_ai_env
}

start_key_portal() {
    clear
    echo "🔑 Starting DEBT Key Management Portal..."
    echo "==========================================="
    echo ""
    echo "🔐 Secure API Key & Credential Management"
    echo "📋 Supported Services:"
    echo "   • OpenAI API (for ShellGPT)"
    echo "   • Hugging Face (for ML models)"
    echo "   • Weights & Biases (for MLOps)"
    echo "   • MLflow Tracking"
    echo "   • GitHub Token"
    echo "   • Docker Hub"
    echo "   • OpenBB Financial APIs"
    echo "   • And more..."
    echo ""
    echo "🔒 Security Features:"
    echo "   • Password-protected access"
    echo "   • AES-256 encrypted storage"
    echo "   • Local-only access"
    echo ""
    
    # Launch the key portal
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    "$SCRIPT_DIR/start_key_portal.sh"
}
while true; do
    show_menu
    read -p "Enter your choice [1-10]: " choice

    case $choice in
        1)
            start_neovim
            ;;
        2)
            start_n8n
            ;;
        3)
            open_shell
            ;;
        4)
            start_lean_project
            ;;
        5)
            start_openbb
            ;;
        6)
            start_shellgpt
            ;;
        7)
            start_shellngn
            ;;
        8)
            start_ml_ai_env
            ;;
        9)
            start_key_portal
            ;;
        10)
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            sleep 2
            ;;
    esac
done
