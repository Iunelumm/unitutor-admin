#!/bin/bash

echo "🚀 UniTutor Admin Panel - Quick Deploy Script"
echo "=============================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📝 Adding files to Git..."
git add .

echo ""
echo "💾 Committing changes..."
git commit -m "Fix dependencies and add deployment configuration" || echo "⚠️  No changes to commit"

echo ""
echo "=============================================="
echo "✅ Local preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/unitutor-admin.git"
echo "3. Run: git push -u origin main"
echo "4. Deploy on Streamlit Cloud: https://share.streamlit.io/"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
