#!/bin/bash

# xnox-me GitHub Organization Profile Setup Script
# Automates repository configuration and profile enhancement

echo "🎯 xnox-me GitHub Organization Profile Setup"
echo "============================================="
echo ""

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "🔐 Please authenticate with GitHub CLI first:"
    echo "gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready"
echo ""

# Function to update repository settings
update_repository() {
    local repo=$1
    local description=$2
    local topics=$3
    
    echo "🔄 Updating repository: $repo"
    
    # Update description
    if [ ! -z "$description" ]; then
        echo "  📝 Setting description..."
        gh repo edit "$repo" --description "$description"
    fi
    
    # Note: Topics need to be set via web interface or API calls
    echo "  🏷️  Topics to add manually: $topics"
    echo ""
}

# Repository configurations
echo "📋 Repository Configuration:"
echo ""

# DEBT Repository
echo "1. 📊 DEBT Repository Configuration:"
DEBT_DESC="🚀 Complete Business Intelligence Platform • Islamic Finance • Global Markets • Real-time Analytics • ML/AI • Open Source"
DEBT_TOPICS="business-intelligence fintech islamic-finance machine-learning python fastapi streamlit real-time global-markets cryptocurrency portfolio-analysis api dashboard"

update_repository "xnox-me/DEBT" "$DEBT_DESC" "$DEBT_TOPICS"

# Dronat Repository  
echo "2. 🏗️ Dronat Repository Configuration:"
DRONAT_DESC="🛠️ Advanced Development Tools & Infrastructure • Automation • Deployment • Package Management • Developer Experience"
DRONAT_TOPICS="development-tools infrastructure automation deployment package-management developer-experience productivity"

update_repository "xnox-me/Dronat" "$DRONAT_DESC" "$DRONAT_TOPICS"

# Instructions for manual steps
echo "📋 Manual Steps Required:"
echo ""
echo "🌐 Organization Profile Settings:"
echo "   Visit: https://github.com/organizations/xnox-me/settings"
echo ""
echo "   Bio: Advanced Business Intelligence & Development Tools • Open Source • Islamic Finance • Global Markets • ML/AI Solutions • Community Driven"
echo "   Website: https://github.com/xnox-me"
echo "   Location: Global • Remote-First"
echo ""

echo "🎨 Organization README:"
echo "   1. Create repository: .github"
echo "   2. Create file: profile/README.md"
echo "   3. Copy content from: /home/eboalking/Dronat011/DEBT/xnox-me-profile/README.md"
echo ""

echo "🏷️  Repository Topics (add manually via web interface):"
echo ""
echo "   DEBT Repository Topics:"
echo "   $DEBT_TOPICS"
echo ""
echo "   Dronat Repository Topics:"
echo "   $DRONAT_TOPICS"
echo ""

echo "🎯 Additional Profile Enhancement:"
echo "   • Upload organization avatar/logo"
echo "   • Set up team structure"
echo "   • Configure security settings"
echo "   • Create project boards"
echo "   • Set repository visibility preferences"
echo ""

# Check if .github repository exists
echo "🔍 Checking for .github repository..."
if gh repo view "xnox-me/.github" &> /dev/null; then
    echo "✅ .github repository exists"
else
    echo "❌ .github repository not found"
    echo ""
    read -p "🤔 Create .github repository for organization profile? (y/N): " create_github_repo
    
    if [[ $create_github_repo =~ ^[Yy]$ ]]; then
        echo "🚀 Creating .github repository..."
        
        # Create temporary directory
        temp_dir=$(mktemp -d)
        cd "$temp_dir"
        
        # Initialize repository
        git init
        mkdir -p profile
        
        # Copy README content
        cp "/home/eboalking/Dronat011/DEBT/xnox-me-profile/README.md" "profile/README.md"
        
        # Create initial commit
        git add .
        git commit -m "feat: Add organization profile README"
        
        # Create repository and push
        gh repo create "xnox-me/.github" --public --description "xnox-me organization profile and community health files"
        git branch -M main
        git remote add origin "https://github.com/xnox-me/.github.git"
        git push -u origin main
        
        echo "✅ .github repository created with profile README"
        
        # Cleanup
        cd - > /dev/null
        rm -rf "$temp_dir"
    else
        echo "⏭️  Skipping .github repository creation"
    fi
fi

echo ""
echo "🎉 Organization Profile Setup Complete!"
echo ""
echo "📋 Summary of Changes:"
echo "   ✅ Repository descriptions updated"
echo "   📋 Topics identified (add manually)"
echo "   📝 Profile content prepared"
echo "   📚 Setup guide available"
echo ""
echo "🌐 Next Steps:"
echo "   1. Visit: https://github.com/organizations/xnox-me/settings"
echo "   2. Fill in organization bio and details"
echo "   3. Add repository topics manually"
echo "   4. Upload organization avatar"
echo "   5. Configure team and security settings"
echo ""
echo "📚 Reference Files:"
echo "   • Profile Content: /home/eboalking/Dronat011/DEBT/xnox-me-profile/PROFILE_CONTENT.md"
echo "   • Setup Guide: /home/eboalking/Dronat011/DEBT/xnox-me-profile/SETUP_GUIDE.md"
echo "   • Organization README: /home/eboalking/Dronat011/DEBT/xnox-me-profile/README.md"
echo ""
echo "🚀 Your xnox-me organization is ready to shine!"