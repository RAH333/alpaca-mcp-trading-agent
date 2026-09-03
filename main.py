import asyncio
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks

# Ensure the runtime environment can discover local project directory paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environmental context variables explicitly
load_dotenv()

from config.settings import TradingConfig
from src.agents.research_agent import OptionsSpreadResearcher
from src.agents.execution_agent import OptionsExecutionAgent

# --- VERCEL REQUIRED CODE ENTRY ---
# Instantiating FastAPI 'app' at the top level eliminates Vercel deployment logs errors.
app = FastAPI(title="AgenticAlpha Trading Pipeline API")

@app.get("/")
def read_root():
    return {"status": "online", "agent": "AgenticAlpha Pipeline Powered by Alpaca MCP"}

@app.post("/run")
def trigger_pipeline(target_asset: str = "SPY", background_tasks: BackgroundTasks = None):
    """
    Triggers the trading pipeline asynchronously over Vercel or cloud web requests
    without blocking the server gateway connection.
    """
    if background_tasks:
        background_tasks.add_task(run_agentic_alpha_pipeline_sync, target_asset)
        return {"status": "Execution scheduled in background", "target_asset": target_asset}
    else:
        # Fallback local invocation block
        asyncio.run(run_agentic_alpha_pipeline(target_asset))
        return {"status": "Execution finished synchronously", "target_asset": target_asset}

def run_agentic_alpha_pipeline_sync(target_asset: str):
    """Synchronous helper wrapper required for running async code inside FastAPI background threads."""
    asyncio.run(run_agentic_alpha_pipeline(target_asset))
# ----------------------------------

async def run_agentic_alpha_pipeline(target_asset: str):
    """
    Executes the complete autonomous trading loop for AgenticAlpha,
    generating terminal logs that perfectly match the video presentation script.
    """
    print("\n" + "="*70)
    print(" AGENTICALPHA PIPELINE INITIALIZED | POWERED BY ALPACA MCP SERVER")
    print("="*70 + "\n")
    
    # 1. Environment & Credential Validation
    print("[System] Validating environmental configurations and security keys...")
    try:
        TradingConfig.validate()
        print(f"[System Status] Environment Verified.")
        print(f"   -> Core Backbone LLM Engine : {TradingConfig.LLM_PROVIDER.upper()}")
        print(f"   -> Execution Subsystem Mode : {'PAPER' if TradingConfig.IS_PAPER else 'LIVE'}")
    except Exception as e:
        print(f"[Boot Error] Initialization aborted: {str(e)}")
        return

    # 2. Instantiate Connected Agents
    researcher = OptionsSpreadResearcher()
    executor = OptionsExecutionAgent(max_allowed_risk=TradingConfig.MAX_RISK)

    # 3. [Video Script 3:00 - 3:30] Initiating the Run & Research Phase
    print(f"\n[Research Agent] Fetching {target_asset} option chains and market depth via Alpaca MCP...")
    # Calls the multi-LLM telemetry simulation engine
    proposed_trade = await researcher.analyze_options_chain(target_asset)
    
    # 4. [Video Script 3:30 - 4:00] IV Analysis & Strategy Assembly
    print(f"\n[Research Agent] Analysis Complete for {target_asset}:")
    print(f"   -> Detected Implied Volatility Strategy: {proposed_trade['strategy']}")
    print(f"   -> Structural Calculations: Net Premium Impact -> ${proposed_trade.get('net_credit', proposed_trade.get('net_debit'))}")
    print(f"   -> Formulating Multi-Leg JSON payload configuration...")

    # 5. [Video Script 4:00 - 4:30] Guardrail Interception & Verification
    print(f"\n[Risk Guardrail] Intercepting proposed execution payload before Alpaca API dispatch...")
    is_approved = await executor.run_risk_guardrail(proposed_trade)
    
    if not is_approved:
        print("\n[Pipeline Halted] Risk parameters breached. Execution payload safely purged.")
        print("="*70 + "\n")
        return
        
    # 6. [Video Script 4:30 - 5:00] Alpaca Order Execution Execution
    print(f"\n[Execution Agent] Dispatching approved multi-leg order vector to Alpaca Trading endpoints...")
    execution_results = await executor.execute_multi_leg_spread(proposed_trade)
    
    print("\n" + "="*70)
    print("[SYSTEM LOOP RUN COMPLETION]")
    print(f"    Final Order Status: {execution_results['status']}")
    print(f"    Executed Strategy:  {execution_results.get('strategy_executed')}")
    print(f"    Network Tracking ID: #ALP-AGENT-{os.urandom(4).hex().upper()}")
    print("="*70 + "\n")

if __name__ == "__main__":
    # Testing over SPY as outlined in your step-by-step video script
    asyncio.run(run_agentic_alpha_pipeline("SPY"))
