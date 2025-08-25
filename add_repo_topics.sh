#!/bin/bash

# Add topics to xnox-me repositories

echo "🏷️ Adding topics to xnox-me repositories..."

# Add topics to DEBT repository
echo "📊 Adding topics to DEBT repository..."
gh api \
  --method PUT \
  /repos/xnox-me/DEBT/topics \
  --field names='["business-intelligence","fintech","islamic-finance","machine-learning","python","fastapi","streamlit","real-time","global-markets","cryptocurrency","portfolio-analysis","api","dashboard"]'

if [ $? -eq 0 ]; then
    echo "✅ DEBT repository topics added successfully"
else
    echo "❌ Failed to add DEBT repository topics"
fi

# Add topics to Dronat repository
echo "🛠️ Adding topics to Dronat repository..."
gh api \
  --method PUT \
  /repos/xnox-me/Dronat/topics \
  --field names='["development-tools","infrastructure","automation","deployment","package-management","developer-experience","productivity"]'

if [ $? -eq 0 ]; then
    echo "✅ Dronat repository topics added successfully"
else
    echo "❌ Failed to add Dronat repository topics"
fi

echo "🎉 Repository topics setup complete!"