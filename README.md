# AgenticAlpha: Multi-Leg Option Spread Autonomous Trading Infrastructure

Developed live for the official **[Alpaca AI Trading Agents Hackathon](https://lablab.ai)** hosted on lablab.ai.

## Overview
AgenticAlpha is a next-generation autonomous multi-agent quantitative framework designed to analyze market vectors and safely manage derivative risk profiles. By integrating specialized Large Language Models with **Alpaca's Model Context Protocol (MCP) Server**, the system translates natural market conditions into robust, risk-defined option spreads governed by programmatic guardrails.

---

## System Architecture & File Layout

```text
alpaca-mcp-trading-agent/
├── config/
│   ├── settings.py            # Unified environment parsing & schema validation
│   └── mcp_config.json        # Reference guide for registering Alpaca Tools (Generated via script)
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
├── main.py                    # Local Command-Line Interface Entry-Point
├── setup.sh                   # Mobile-friendly automated installation & configuration script
└── .gitignore                 # Enforces security exclusions (.env, private secrets, mcp_config.json)
```

---

## Step-by-Step Installation & Automated Testing Guide

To make evaluation easy, an interactive setup script handles all dependency synchronization and key generation directly inside the terminal without requiring text file editing.

### 1. Clone the Project Repository Workspace
```bash
git clone https://github.com
cd alpaca-mcp-trading-agent
```

### 2. Launch the Automated Mobile-Friendly Installer
Make the automation engine executable and run it:
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Provide Your API Parameter Enclaves When Prompted
The terminal will pause and ask for your inputs sequentially. Long-press or right-click to paste each parameter cleanly:
*   **Alpaca API Key & Secret Key:** Required to connect to the broker endpoints.
*   **LLM Model API Keys:** Provide the key matching your intended runtime provider (`openai`, `gemini`, or `open_cloud`).

---

## Modifying the Active LLM Backbone via `.env`

The code relies on a single-source-of-truth orchestration structure. When changing model targets, the configurations inside `config/settings.py` update automatically—**the model name and provider line only need to be altered inside your localized `.env` file:**

```env
# Change these lines to swap underlying models instantly:
LLM_PROVIDER=gemini
LLM_MODEL_NAME=gemini-3.5-flash

# Alternatives:
# For OpenAI:     LLM_PROVIDER=openai     | LLM_MODEL_NAME=gpt-4o
# For Open Cloud: LLM_PROVIDER=open_cloud | LLM_MODEL_NAME=claude-3-5-sonnet
```

---

## Running Manual Pipelines

### Run the Interactive Verification Loop:
```bash
python main.py
```

### Activate the Background Execution Runtime Engine:
```bash
python -m src.server
```
