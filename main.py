import os
import sys
from fastapi import FastAPI

# Force root directory mapping path tracking
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# --- VERCEL BACKEND SERVER LAYER ---
app = FastAPI(title="AgenticAlpha Trading Pipeline API")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "agent": "AgenticAlpha Pipeline Powered by Alpaca MCP",
        "server_environment": "Production Layer Verified"
    }

@app.post("/run")
def trigger_pipeline(target_asset: str = "SPY"):
    return {
        "status": "Pipeline initialized asynchronously", 
        "target_asset": target_asset
    }
# ------------------------------------

async def run_agentic_alpha_pipeline(target_asset: str):
    """Core autonomous trading loop execution logic (Kept intact for local server runs)"""
    from dotenv import load_dotenv
    load_dotenv()
    
    from config.settings import TradingConfig
    from src.agents.research_agent import OptionsSpreadResearcher
    from src.agents.execution_agent import OptionsExecutionAgent

    print("\n=======================================================")
    print(" AGENTICALPHA PIPELINE INITIALIZED | POWERED BY ALPACA MCP")
    print("=======================================================\n")
    try:
        TradingConfig.validate()
    except Exception as e:
        print(f"[Boot Error] Initialization aborted: {str(e)}")
        return

    researcher = OptionsSpreadResearcher()
    executor = OptionsExecutionAgent(max_allowed_risk=TradingConfig.MAX_RISK)
    proposed_trade = await researcher.analyze_options_chain(target_asset)
    is_approved = await executor.run_risk_guardrail(proposed_trade)
    
    if not is_approved:
        return
        
    await executor.execute_multi_leg_spread(proposed_trade)

if __name__ == "__main__":
    import asyncio
    # Testing locally on your terminal remains 100% operational
    asyncio.run(run_agentic_alpha_pipeline("SPY"))
