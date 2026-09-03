import os
import sys
from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv

# This forces the server to look one folder up to find your local project directories
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

load_dotenv()

from config.settings import TradingConfig
from main import run_agentic_alpha_pipeline

app = FastAPI(title="AgenticAlpha Trading Pipeline API")

@app.get("/")
def read_root():
    try:
        TradingConfig.validate()
        config_status = "Keys Verified & Loaded Successfully."
    except Exception as e:
        config_status = f"Public View Mode (Keys not configured on Vercel dashboard: {str(e)})"

    return {
        "status": "online",
        "agent": "AgenticAlpha Pipeline Powered by Alpaca MCP",
        "server_environment": config_status,
        "note": "To execute live loops locally, run 'python main.py' with your own .env file."
    }

@app.post("/run")
def trigger_pipeline(target_asset: str = "SPY", background_tasks: BackgroundTasks = None):
    import asyncio
    if background_tasks:
        background_tasks.add_task(asyncio.run, run_agentic_alpha_pipeline(target_asset))
        return {"status": "Execution scheduled in background", "target_asset": target_asset}
    else:
        asyncio.run(run_agentic_alpha_pipeline(target_asset))
        return {"status": "Execution finished synchronously", "target_asset": target_asset}
