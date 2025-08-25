#!/bin/bash

# Script to make all xnox-me repositories public
# Requires GitHub CLI (gh) and proper authentication

echo "🌐 Making All xnox-me Repositories Public"
echo "=========================================="
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "🔐 GitHub CLI authentication required..."
    echo "Please run: gh auth login"
    echo ""
    echo "Then re-run this script."
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Function to make a repository public
make_repo_public() {
    local repo=$1
    echo "🔄 Processing repository: $repo"
    
    # Check current visibility
    visibility=$(gh repo view "$repo" --json visibility --jq '.visibility' 2>/dev/null)
    
    if [ "$visibility" = "public" ]; then
        echo "✅ $repo is already public"
    elif [ "$visibility" = "private" ]; then
        echo "🔓 Making $repo public..."
        if gh repo edit "$repo" --visibility public; then
            echo "✅ $repo is now public"
        else
            echo "❌ Failed to make $repo public"
        fi
    else
        echo "⚠️  Could not determine visibility for $repo"
    fi
    echo ""
}

# List all repositories for xnox-me organization
echo "📋 Fetching repositories for xnox-me organization..."
repos=$(gh repo list xnox-me --limit 100 --json name --jq '.[].name' 2>/dev/null)

if [ -z "$repos" ]; then
    echo "❌ No repositories found for xnox-me organization"
    echo "   This could mean:"
    echo "   - You don't have access to the organization"
    echo "   - The organization doesn't exist"
    echo "   - There are no repositories in the organization"
    exit 1
fi

echo "📋 Found repositories:"
for repo in $repos; do
    echo "   • xnox-me/$repo"
done
echo ""

# Confirm before proceeding
read -p "❓ Do you want to make ALL these repositories public? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ Operation cancelled by user"
    exit 0
fi

echo ""
echo "🚀 Starting to make repositories public..."
echo ""

# Process each repository
for repo in $repos; do
    make_repo_public "xnox-me/$repo"
done

echo "🎉 Repository visibility update complete!"
echo ""
echo "📋 Summary:"
echo "   • Organization: xnox-me"
echo "   • Repositories processed: $(echo "$repos" | wc -w)"
echo "   • All repositories should now be public"
echo ""
echo "🌐 You can verify at: https://github.com/xnox-me"
echo ""

# Optional: List final status
echo "📊 Final repository status:"
for repo in $repos; do
    visibility=$(gh repo view "xnox-me/$repo" --json visibility --jq '.visibility' 2>/dev/null)
    if [ "$visibility" = "public" ]; then
        echo "   ✅ xnox-me/$repo - PUBLIC"
    else
        echo "   ❌ xnox-me/$repo - $visibility"
    fi
done