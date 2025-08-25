# Chapter 26: Command Line Reference

## 📟 DEBT Platform Command Reference

Complete command-line interface documentation for the DEBT platform.

## Core Commands

### Environment Management

#### activate_env.sh
Activate the DEBT environment
```bash
# Basic activation
source activate_env.sh

# Check activation status
echo $DEBT_HOME
echo $PYTHONPATH
```

**Environment Variables Set:**
- `DEBT_HOME` - Platform root directory
- `PYTHONPATH` - Python module search path
- `PATH` - Script execution path

#### install-packages.sh
Install platform dependencies
```bash
# Full installation (requires sudo)
sudo ./install-packages.sh

# Check installation status
./install-packages.sh --check

# Repair installation
sudo ./install-packages.sh --repair
```

**Options:**
- `--check` - Verify installation without installing
- `--repair` - Fix broken installations
- `--minimal` - Install only core dependencies

### Platform Management

#### menu.sh
Interactive platform menu
```bash
# Launch interactive menu
./menu.sh

# Direct service launch
./menu.sh --service financial_dashboard
./menu.sh --service api_gateway
```

**Available Services:**
1. Financial Dashboard (Streamlit)
2. ML Interface (Gradio)
3. MLflow Tracking
4. Jupyter Lab
5. n8n Workflows
6. API Plugin
7. TASI Market Intelligence
8. Global Markets Intelligence

#### start_all_business_intelligence.sh
Start all BI suites simultaneously
```bash
# Interactive selection
./start_all_business_intelligence.sh

# Auto-start all services
./start_all_business_intelligence.sh --all

# Start specific suite
./start_all_business_intelligence.sh --suite tasi
./start_all_business_intelligence.sh --suite global
```

**Options:**
- `--all` - Start all suites without prompts
- `--suite NAME` - Start specific suite only
- `--background` - Run services in background

## Service-Specific Commands

### Financial Dashboard

#### Start Dashboard
```bash
# Original sophisticated example
cd sophisticated_example/financial_dashboard
./start_dashboard.sh

# TASI Islamic finance
cd tasi_market_intelligence/financial_dashboard
./start_tasi_dashboard.sh

# Global markets
cd global_markets_intelligence/financial_dashboard
./start_global_dashboard.sh
```

**Options:**
- `--port PORT` - Custom port (default: 8501)
- `--host HOST` - Custom host (default: 0.0.0.0)
- `--debug` - Enable debug mode

### API Services

#### Start API Gateway
```bash
# Main API gateway
python api_plugin.py

# With custom configuration
python api_plugin.py --config custom_config.py
python api_plugin.py --port 9001

# Background mode
nohup python api_plugin.py &
```

#### Start Suite APIs
```bash
# Original suite API
cd sophisticated_example/api_services
python main.py

# TASI API
cd tasi_market_intelligence/api_services
python main.py

# Global markets API
cd global_markets_intelligence/api_services
python main.py
```

### Machine Learning Services

#### MLflow Commands
```bash
# Start MLflow UI
mlflow ui --host 0.0.0.0 --port 5000

# Start with specific backend
mlflow server --backend-store-uri sqlite:///mlflow.db
mlflow server --default-artifact-root ./mlruns

# Track experiment
mlflow run . -P alpha=0.5
```

#### Model Training
```bash
# Train churn model
cd sophisticated_example/ml_pipeline
python train_models.py --model churn

# Train all models
python train_models.py --all

# Custom parameters
python train_models.py --model churn --n_estimators 200
```

#### Model Serving
```bash
# Serve model via MLflow
mlflow models serve -m runs:/RUN_ID/model -p 5001

# Serve with custom host
mlflow models serve -m models:/ChurnModel/Production -h 0.0.0.0
```

## GitHub Management Commands

### Repository Management

#### make_xnox_repos_public.sh
Make all organization repositories public
```bash
# Interactive mode
./make_xnox_repos_public.sh

# Auto-confirm
echo "y" | ./make_xnox_repos_public.sh

# Specific repository
gh repo edit xnox-me/DEBT --visibility public --accept-visibility-change-consequences
```

#### Profile Setup
```bash
# Setup organization profile
cd xnox-me-profile
./setup_profile.sh

# Auto-create .github repository
echo "y" | ./setup_profile.sh
```

### Git Operations
```bash
# Push to both remotes
git push origin master
git push github master

# Add and commit all changes
git add .
git commit -m "feat: description of changes"

# Check repository status
git status
git remote -v
```

## Docker Commands

### Container Management

#### Build Images
```bash
# Build main platform image
docker build -t debt-platform .

# Build specific service
docker build -t debt-api ./api_services

# Build with custom tag
docker build -t debt-platform:v1.0 .
```

#### Run Containers
```bash
# Run main platform
docker run -p 8501:8501 -p 9000:9000 debt-platform

# Run with volume mounting
docker run -v $(pwd):/app -p 8501:8501 debt-platform

# Run in background
docker run -d --name debt-platform -p 8501:8501 debt-platform
```

#### Container Operations
```bash
# List running containers
docker ps

# View container logs
docker logs debt-platform

# Execute command in container
docker exec -it debt-platform bash

# Stop and remove
docker stop debt-platform
docker rm debt-platform
```

## Monitoring Commands

### System Health

#### Service Health Checks
```bash
# Check all services
curl http://localhost:9000/health

# Check specific service
curl http://localhost:8501/health
curl http://localhost:8003/health

# Detailed status
curl http://localhost:9000/api/status | jq
```

#### Process Monitoring
```bash
# Show DEBT processes
ps aux | grep -E "(streamlit|uvicorn|mlflow|gradio)"

# Check port usage
netstat -tulpn | grep -E "(8501|9000|5000)"

# Monitor resource usage
top -p $(pgrep -d, -f "streamlit|uvicorn")
```

### Log Monitoring
```bash
# View service logs
tail -f logs/api_gateway.log
tail -f logs/financial_dashboard.log

# View all logs
tail -f logs/*.log

# Search logs
grep "ERROR" logs/*.log
grep -n "startup" logs/api_gateway.log
```

## Data Management Commands

### Cache Management

#### Clear Cache
```bash
# Clear application cache
python -c "from api_plugin import cache_store; cache_store.clear()"

# Clear MLflow cache
rm -rf mlruns/.cache

# Clear browser cache (programmatic)
rm -rf ~/.cache/streamlit
```

#### Cache Statistics
```bash
# View cache status
curl http://localhost:9000/api/cache/status

# Cache performance
curl http://localhost:9000/api/cache/stats
```

### Database Operations
```bash
# Backup data
pg_dump debt_db > backup_$(date +%Y%m%d).sql

# Restore data
psql debt_db < backup_20250825.sql

# Check database status
psql -c "SELECT version();"
```

## Testing Commands

### Unit Tests
```bash
# Run all tests
python -m pytest

# Run specific test suite
python -m pytest tests/test_api.py
python -m pytest tests/test_ml_models.py

# Run with coverage
python -m pytest --cov=./ --cov-report=html
```

### API Testing
```bash
# Test API endpoints
curl -X GET http://localhost:9000/api/financial/market/AAPL
curl -X POST http://localhost:9000/api/ml/predict/churn -d '{"age": 35}'

# Load testing
ab -n 1000 -c 10 http://localhost:9000/health
```

### Integration Tests
```bash
# Full platform test
./tests/integration_test.sh

# Service connectivity test
./tests/connectivity_test.sh

# Performance test
./tests/performance_test.sh
```

## Utility Commands

### File Operations

#### Find and Replace
```bash
# Update configuration across files
find . -name "*.py" -exec sed -i 's/old_value/new_value/g' {} \;

# Update port numbers
grep -r "8501" --include="*.py" . | cut -d: -f1 | xargs sed -i 's/8501/8502/g'
```

#### Backup and Restore
```bash
# Create backup
tar -czf debt_backup_$(date +%Y%m%d).tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  .

# Restore backup
tar -xzf debt_backup_20250825.tar.gz
```

### Performance Optimization
```bash
# Optimize Python files
python -m py_compile **/*.py

# Clean temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Disk usage analysis
du -sh */
du -h --max-depth=1 | sort -hr
```

## Environment Commands

### Python Environment
```bash
# List installed packages
pip list
pip freeze > requirements.txt

# Update packages
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Virtual environment info
python -m venv --help
which python
python --version
```

### System Information
```bash
# System resources
free -h
df -h
lscpu

# Network connectivity
ping -c 4 github.com
curl -I https://github.com/xnox-me/DEBT

# Service status
systemctl status docker
systemctl status nginx  # if using reverse proxy
```

## Troubleshooting Commands

### Common Issues

#### Permission Fixes
```bash
# Fix script permissions
find . -name "*.sh" -exec chmod +x {} \;

# Fix Python file permissions
find . -name "*.py" -exec chmod 644 {} \;

# Fix directory permissions
find . -type d -exec chmod 755 {} \;
```

#### Service Recovery
```bash
# Kill stuck processes
pkill -f streamlit
pkill -f uvicorn
pkill -f mlflow

# Restart services
./menu.sh --restart
./start_all_business_intelligence.sh --restart
```

#### Reset Environment
```bash
# Reset Python environment
rm -rf ~/.debt-env
python3 -m venv ~/.debt-env
source ~/.debt-env/bin/activate
pip install -r requirements.txt

# Reset configuration
cp config/default_config.py config/user_config.py
```

## Aliases and Shortcuts

### Useful Aliases
```bash
# Add to ~/.bashrc
alias debt-start='cd $DEBT_HOME && source activate_env.sh && ./menu.sh'
alias debt-api='cd $DEBT_HOME && python api_plugin.py'
alias debt-dash='cd $DEBT_HOME/sophisticated_example/financial_dashboard && ./start_dashboard.sh'
alias debt-logs='cd $DEBT_HOME && tail -f logs/*.log'
alias debt-health='curl -s http://localhost:9000/health | jq'
```

### Quick Scripts
```bash
# Quick status check
#!/bin/bash
echo "DEBT Platform Status"
echo "==================="
curl -s http://localhost:9000/health | jq '.status' || echo "API Gateway: DOWN"
curl -s http://localhost:8501 > /dev/null && echo "Dashboard: UP" || echo "Dashboard: DOWN"
```

---

**📖 Next: [Chapter 27: Configuration Templates](./27_config_templates.md)**