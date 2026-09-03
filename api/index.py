import os
import sys
from fastapi import FastAPI
from dotenv import load_dotenv

# Ensure Vercel can locate your core config submodules cleanly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

load_dotenv()

from config.settings import TradingConfig

app = FastAPI(title="AgenticAlpha Trading Pipeline API")

@app.get("/")
def read_root():
    """Web interface landing page for the examiner."""
    try:
        TradingConfig.validate()
        config_status = "Keys Verified & Loaded Successfully."
    except Exception as e:
        config_status = f"Public View Mode (Keys not configured on Vercel: {str(e)})"

    return {
        "status": "online",
        "agent": "AgenticAlpha Pipeline Powered by Alpaca MCP",
        "server_environment": config_status,
        "note": "To execute live loops locally, run 'python main.py' with your own .env file."
    }
