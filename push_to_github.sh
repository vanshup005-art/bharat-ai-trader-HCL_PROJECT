#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Push BharatAI Trader to a Remote GitHub Repository
# Usage: ./push_to_github.sh <YOUR_GITHUB_REPO_URL>
# Example: ./push_to_github.sh https://github.com/your-username/bharat-ai-trader.git
# ==============================================================================

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub repository URL."
    echo ""
    echo "Usage:"
    echo "  ./push_to_github.sh https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git"
    echo ""
    exit 1
fi

REPO_URL="$1"

echo "🚀 Connecting to remote repository: $REPO_URL ..."

# If origin exists, update it; otherwise add it
if git remote | grep -q "origin"; then
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

echo "📦 Pushing main branch to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "🔗 View your repository at: $REPO_URL"
