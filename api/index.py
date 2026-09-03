import os
import sys

# Dynamic root path injection so Vercel can locate your main logic modules
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv

# Load credentials safely
load_dotenv()

from config.settings import TradingConfig
# We import your pipeline loop directly from your original main.py script
from main import run_agentic_alpha_pipeline

app = FastAPI(title="AgenticAlpha Trading Pipeline API")

@app.get("/")
def read_root():
    """Landing page verifying deployment health for your examiner."""
    try:
        TradingConfig.validate()
        config_status = "Keys Verified & Loaded Successfully."
    except Exception as e:
        config_status = f"Public View Mode (Keys not fully configured on web server dashboard: {str(e)})"

    return {
        "status": "online",
        "agent": "AgenticAlpha Pipeline Powered by Alpaca MCP",
        "server_environment": config_status,
        "note": "To execute live loops locally, run 'python main.py' with your own local .env configuration file."
    }

@app.post("/run")
def trigger_pipeline(target_asset: str = "SPY", background_tasks: BackgroundTasks = None):
    """Triggers the trading agent pipeline via web request."""
    import asyncio
    if background_tasks:
        background_tasks.add_task(asyncio.run, run_agentic_alpha_pipeline(target_asset))
        return {"status": "Execution scheduled in background", "target_asset": target_asset}
    else:
        asyncio.run(run_agentic_alpha_pipeline(target_asset))
        return {"status": "Execution finished synchronously", "target_asset": target_asset}
