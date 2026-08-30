# alpaca-mcp-trading-agent
Alpaca MCP Trading Agent: An asynchronous AI agent running over modern multi-agent routing.

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
│       └── helpers.py              # Logging and payload formatters
├── tests/
│   └── test_agents.py             # Simple unit tests for system validation
├── .env.example                   # Clean template for API keys
├── .gitignore                     # Prevents secrets leakage (.env, __pycache__)
├── pyproject.toml                 # Modern package manager configuration (uv / poetry)
├── requirements.txt               # Legacy package definitions
└── README.md                      # The centerpiece submission document for judges
```
