#!/bin/bash
# ====================================================================
# AGENTICALPHA MOBILE AUTOMATED INSTALLER & CONFIGURATION MATRIX
# ====================================================================

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo " INITIALIZING AUTOMATED ENVIRONMENT CONTEXT"
echo "=========================================================="

# Step 1: Core System & Dependency Upgrade
echo -e "\n[1/5] Upgrading platform package indexing..."
python3 -m pip install --upgrade pip

echo "[1/5] Compiling workspace dependencies via pip..."
pip install -r requirements.txt

# Step 2: Interactive Plain-Text Value Inputs (No Nano/Vim Editors Required)
echo -e "\n=========================================================="
echo " PASTE YOUR SECURITY PARAMETERS BELOW & PRESS ENTER:"
echo "=========================================================="

read -p "🔹 Enter Alpaca API Key: " alpaca_key
read -p "🔹 Enter Alpaca Secret Key: " alpaca_secret
read -p "🔹 Enter OpenAI API Key (Press Enter if blank): " openai_key
read -p "🔹 Enter Gemini API Key (Press Enter if blank): " gemini_key
read -p "🔹 Enter Open Cloud/Anthropic Key (Press Enter if blank): " opencloud_key

# Step 3: Programmatic Generation of .env
echo -e "\n[3/5] Constructing isolated environmental properties (.env)..."
cat << EOF > .env
# ====================================================================
# 🎛️ MASTER ROUTING SWITCH
# ====================================================================
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4o

# ====================================================================
# PRIVATE SECURITY CREDS
# ====================================================================
ALPACA_API_KEY=$alpaca_key
ALPACA_SECRET_KEY=$alpaca_secret
ALPACA_IS_PAPER=true

OPENAI_API_KEY=$openai_key
GEMINI_API_KEY=$gemini_key
OPEN_CLOUD_API_KEY=$opencloud_key

# ====================================================================
# DETERMINISTIC COMPLIANCE RISK BOUNDARIES
# ====================================================================
MAX_PORTFOLIO_RISK_PERCENT=0.05
MAX_LEG_COUNT=4
EOF

# Step 4: Programmatic Generation of mcp_config.json
echo "[4/5] Generating options server routing matrix (config/mcp_config.json)..."
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

echo -e "\n WORKSPACE ARCHITECTURE SAFELY PROVISIONED!"
echo "=========================================================="

# Step 5: Execute Validation Loop
echo -e "\n[5/5] Launching Local Pipeline Verification Script..."
python3 main.py
