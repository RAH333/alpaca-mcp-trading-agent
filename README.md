# AgenticAlpha: Multi-Leg Option Spread Autonomous Trading Infrastructure

Developed live for the official **[Alpaca AI Trading Agents Hackathon](https://lablab.ai/ai-hackathons/alpaca-ai-trading-agents-hackathon)** hosted on lablab.ai.

## Overview
AgenticAlpha is a next-generation autonomous multi-agent quantitative framework designed to analyze market vectors and safely manage derivative risk profiles. By integrating specialized Large Language Models with **Alpaca's Model Context Protocol (MCP) Server**, the system translates natural market conditions into robust, risk-defined option spreads (e.g., Credit Spreads and Debit Spreads) governed by programmatic guardrails.

---

## System Architecture & File Layout

```text
alpaca-mcp-trading-agent/
├── config/
│   ├── settings.py            # Unified environment parsing, schema validation & type mapping
│   └── mcp_config.json        # Reference guide for registering Alpaca Tools into the LLM runtime
├── src/
│   ├── __init__.py            # Global module exposure context
│   ├── server.py              # Main production orchestration heartbeat loop
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py  # Evaluates market metrics & dynamically switches core LLM engines
│   │   └── execution_agent.py # Validates trade vectors against risk matrices before API dispatch
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py         # Universal telemetry string formatting & logger pipelines
│       ├── llm_openai.py      # OpenAI gpt-4o structural abstraction client
│       ├── llm_gemini.py      # Google Gemini 3.5 Flash abstraction client
│       └── llm_open_cloud.py  # Anthropic Claude 3.5 Sonnet abstraction client
├── main.py                    # Local Command-Line Interface and Video Script Simulator Entry-Point
├── setup.sh                   # Mobile-friendly automated installation & configuration script
└── .gitignore                 # Enforces security exclusions (.env, private secrets, mcp_config.json)
```

---

## Installation & Judge Testing Guide

You can initialize and evaluate AgenticAlpha using either the **Automated Setup Script** (recommended for mobile touchscreen users and fast terminal deployment) or the **Manual Configuration path**.

### Option A: Automated Configuration (Fastest & Mobile-Friendly)

If you are evaluating this repository via a mobile cloud terminal environment where keyboard shortcuts and text editors like `nano` are unavailable, use our fully automated setup script:

1. **Clone the Project Repository Workspace:**
   ```bash
   git clone https://github.com/RAH333/alpaca-mcp-trading-agent.git
   cd alpaca-mcp-trading-agent
   ```
2. **Make the Automation Engine Executable:**
   ```bash
   chmod +x setup.sh
   ```
3. **Launch the Interactive Terminal Installer:**
   ```bash
   ./setup.sh
   ```
4. **Input Your Private API Keys:**
   The terminal prompt will automatically pause and accept your credentials sequentially. Simply right-click or long-press your mobile terminal screen to paste your Alpaca and selected LLM API keys. The script will automatically upgrade `pip`, install dependencies, programmatically generate your `.env`, assemble `config/mcp_config.json`, and kickstart the validation verification script.

---

### Option B: Manual Configuration

If you prefer to review and build the architecture layers by hand, execute these step-by-step terminal instructions:

1. **Clone the Project Repository Workspace:**
   ```bash
   git clone https://github.com
   cd alpaca-mcp-trading-agent
   ```
2. **Configure Local Secrets (`.env`):**
   Create a localized environment file in the root directory:
   ```bash
   touch .env
   ```
   Open the `.env` file and populate it with your real credentials:
   ```env
   # Alpaca Financial API Infrastructure Execution Credentials
   ALPACA_API_KEY=your_actual_alpaca_paper_key_here
   ALPACA_SECRET_KEY=your_actual_alpaca_secret_here
   ALPACA_IS_PAPER=true

   # Multi-LLM Provider Engine Routing Layer Configuration
   # Options: "openai" | "gemini" | "open_cloud"
   LLM_PROVIDER=openai
   LLM_MODEL_NAME=gpt-4o

   # Individual Provider Key Entries (Populate the one matching your LLM_PROVIDER choice)
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   OPEN_CLOUD_API_KEY=your_anthropic_claude_key_here

   # Risk Compliance Parameters
   MAX_PORTFOLIO_RISK_PERCENT=0.05
   MAX_LEG_COUNT=4
   ```
3. **Initialize Local Server Configurations (`config/mcp_config.json`):**
   Create your tracking parameter configuration inside the `config/` directory:
   ```bash
   mkdir -p config
   touch config/mcp_config.json
   ```
   Populate `config/mcp_config.json` with your verified Alpaca runtime parameters:
   ```json
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
           "ALPACA_API_KEY": "your_actual_alpaca_paper_key_here",
           "ALPACA_SECRET_KEY": "your_actual_alpaca_secret_here",
           "ALPACA_USE_PAPER": "true"
         }
       }
     }
   }
   ```
4. **Install Dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Modifying the Active LLM Backbone

The workspace operates under a single-source-of-truth configuration architecture. Changing the targeted engine does not require edits inside `config/settings.py` or agent files—**the provider environment lines only need to be altered inside your localized `.env` file:**

```env
# Example configuration for Google Gemini:
LLM_PROVIDER=gemini
LLM_MODEL_NAME=gemini-3.5-flash

# Alternatives:
# For OpenAI:     LLM_PROVIDER=openai     | LLM_MODEL_NAME=gpt-4o
# For Open Cloud: LLM_PROVIDER=open_cloud | LLM_MODEL_NAME=claude-3-5-sonnet
```

---

## Running Execution Pipelines

### Run the Interactive Verification Loop & Video Simulator:
To test the end-to-end multi-agent pipeline exactly as showcased in our presentation walkthrough, trigger the local master entry-point script:
```bash
python main.py
```

### Activate the Continuous Automated Server Module:
To boot the continuous system background orchestration execution matrix:
```bash
python -m src.server
```

---

## Hackathon Open Community Framework
Contributions, optimization pull requests, and additional structural options strategy maps are highly welcome! Please ensure any code changes pass local verification checks and automated Github actions pipelines before submitting upstream merges.
