#!/bin/bash
set -e

echo "=========================================================="
echo "🤖 INITIALIZING AUTOMATED ENVIRONMENT CONTEXT"
echo "=========================================================="

echo -e "\n=========================================================="
echo " PASTE YOUR SECURITY PARAMETERS BELOW & PRESS ENTER:"
echo "=========================================================="

read -p "🔹 Enter Alpaca API Key: " alpaca_key
read -p "🔹 Enter Alpaca Secret Key: " alpaca_secret
read -p "🔹 Enter OpenAI API Key (Leave blank if using Gemini): " openai_key
read -p "🔹 Enter Gemini API Key (Leave blank if using OpenAI): " gemini_key
read -p "🔹 Enter Open Cloud Key (Leave blank if using others): " opencloud_key

# FIXED INTELLIGENT AUTO-DETECTION SYSTEM
# Using standard bash string tests [ -n "$var" ] to see if a key has been pasted
if [ -n "$gemini_key" ]; then
    provider="gemini"
    model="gemini-2.5-flash" # "gemini-1.5-flash" 
elif [ -n "$openai_key" ]; then
    provider="openai"
    model="gpt-4o"
elif [ -n "$opencloud_key" ]; then
    provider="open_cloud"
    model="claude-3-5-sonnet"
else
    # Safety fallback default state
    provider="openai"
    model="gpt-4o"
fi

echo -e "\n[Auto-Detect] Activating Engine Blueprint: ${provider^^} (${model})"

# Programmatic Creation of .env
cat << EOF > .env
LLM_PROVIDER=$provider
LLM_MODEL_NAME=$model

ALPACA_API_KEY=$alpaca_key
ALPACA_SECRET_KEY=$alpaca_secret
ALPACA_IS_PAPER=true

OPENAI_API_KEY=$openai_key
GEMINI_API_KEY=$gemini_key
OPEN_CLOUD_API_KEY=$opencloud_key

MAX_PORTFOLIO_RISK_PERCENT=0.05
MAX_LEG_COUNT=4
EOF

# Programmatic Creation of mcp_config.json
mkdir -p config
cat << EOF > config/mcp_config.json
{
  "mcpServers": {
    "alpaca-options-server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-server-alpaca",
        "mcp-server-alpaca"
      ],
      "env": {
        "ALPACA_API_KEY": "$alpaca_key",
        "ALPACA_SECRET_KEY": "$alpaca_secret",
        "ALPACA_USE_PAPER": "true"
      }
    }
  }
}
EOF

echo -e "\nWORKSPACE ARCHITECTURE SAFELY PROVISIONED!"
echo "=========================================================="

python3 main.py
