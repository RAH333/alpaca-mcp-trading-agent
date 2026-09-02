# alpaca-mcp-trading-agent
Alpaca MCP Trading Agent: An asynchronous AI agent running over modern multi-agent routing.




# AgenticAlpha: Autonomous AI Trading Agent System

Developed for the **[Alpaca AI Trading Agents Hackathon](https://lablab.ai/ai-hackathons/alpaca-ai-trading-agents-hackathon)** on lablab.ai.

## Overview
AgenticAlpha is an open-source, multi-agent algorithmic infrastructure leveraging **Alpaca's Model Context Protocol (MCP) Server** and execution endpoints. It connects localized LLM intelligences with safe, live financial order books to execute multi-market trades entirely via natural language processing.

## Architecture
- **Research Agent:** Performs continuous sentiment evaluations across real-time news APIs.
- **Execution Agent:** Calls safe, atomic transaction routes across Alpaca's Paper Trading Engine API.
- **MCP Middleware Layer:** Enables fluid, zero-code tool invocation through natural language command configurations.

## Quickstart Installation

1. Clone the open workspace:
   ```bash
   git clone https://github.com
   cd alpaca-mcp-trading-agent
   ```

2. Establish your environment properties inside `.env`:
   ```bash
   cp .env.example .env
   # Populate keys from your Alpaca account dashboard
   ```

3. Initialize dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Launch the automated loop simulation:
   ```bash
   python -m src.server
   ```

## Open Contribution
This team is open to all skill levels! If you wish to join the design track, clone the repository, create a descriptive branch, and open a Pull Request.



```
alpaca-mcp-trading-agent/
├── .github/
│   └── workflows/
│       └── test-and-lint.yml      # CI pipeline for linting & automated testing
├── config/
│   ├── settings.py                # Environment validation and credentials management
│   └── mcp_config.json            # Setup file to load the Alpaca MCP server into your AI
├── src/
│   ├── __init__.py
│   ├── server.py                  # Core script initializing the server runtime 
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py      # Leverages LLMs to read sentiment & fetch market tickers
│   │   └── execution_agent.py     # Interacts directly with Alpaca tools via MCP commands
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py           # UNIVERSAL: Logging, text formatting, token counters
│       │                        # Logging and payload formatters
│       ├── llm_openai.py        # OPENAI-SPECIFIC: Payload parsers, tool calling schemas
│       ├── llm_claude.py        # CLAUDE-SPECIFIC: Message block formatters
│       └── llm_gemini.py        # GEMINI-SPECIFIC: Content/Part wrappers, model safety settings
├── tests/
│   └── test_agents.py             # Simple unit tests for system validation
├── .env.example                   # Clean template for API keys
├── .gitignore                     # Prevents secrets leakage (.env, __pycache__)
├── pyproject.toml                 # Modern package manager configuration (uv / poetry)
├── requirements.txt               # Legacy package definitions
└── README.md                      # The centerpiece submission document for judges
```


# AgenticAlpha: Multi-Leg Option Spread Trading Agent

Developed live for the official **[Alpaca AI Trading Agents Hackathon](https://lablab.ai/ai-hackathons/alpaca-ai-trading-agents-hackathon)** on lablab.ai.

## System Architecture Overview
AgenticAlpha solves the problem of automated derivative risk management by wrapping specialized LLM-driven research agents inside strict mathematical programmatic guardrails.

1. **Research Agent (src/agents/research_agent.py):** Queries Implied Volatility (IV) ranks over market indices via the Model Context Protocol (MCP) server. Formulates automated complex spreads (e.g., Credit Spreads).
2. **Execution Guardrail Agent (src/agents/execution_agent.py):** Intercepts raw actions and runs a deterministic risk analysis to ensure positions never violate capital protection parameters.
3. **Alpaca API Execution Core:** Dispatches programmatic options executions natively through the Alpaca Python SDK.

## Installation & Setup

1. **Clone the Repo Workspace:**
   ```bash
   git clone https://github.com
   cd alpaca-mcp-options-agent
   ```

2. **Establish Environment Properties:**
   Create a `.env` file from the repository template:
   ```bash
   cp .env.example .env
   ```
   Add your paper-trading developer parameters inside `.env`.

3. **Install Core Platform Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Boot Up the Autonomous Loop Runtime:**
   ```bash
   python -m src.server
   ```

## Open Community Team
Our codebase is open to all hackathon members. Please request access, review outstanding GitHub Issues, map new strategy criteria into the research module, and issue clean Pull Requests!
