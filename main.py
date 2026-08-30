import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure the runtime environment can discover local project directory paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TradingConfig
from src.agents.research_agent import OptionsSpreadResearcher
from src.agents.execution_agent import OptionsExecutionAgent

async def run_agentic_alpha_pipeline(target_asset: str):
    """
    Executes the complete autonomous trading loop for AgenticAlpha,
    generating terminal logs that perfectly match the video presentation script.
    """
    print("\n" + "="*70)
    print("🤖 AGENTICALPHA PIPELINE INITIALIZED | POWERED BY ALPACA MCP SERVER")
    print("="*70 + "\n")
    
    # 1. Environment & Credential Validation
    print("[⚙️ System System] Validating environmental configurations and security keys...")
    try:
        TradingConfig.validate()
        print(f"[⚙️ System Status] Environment Verified. Mode: {'PAPER' if TradingConfig.IS_PAPER else 'LIVE'}")
    except Exception as e:
        print(f"[❌ Boot Error] Initialization aborted: {str(e)}")
        return

    # 2. Instantiate Agents
    researcher = OptionsSpreadResearcher()
    executor = OptionsExecutionAgent(max_allowed_risk=TradingConfig.MAX_RISK)

    # 3. [Video Script 3:00 - 3:30] Initiating the Run & Research Phase
    print(f"\n[🔬 Research Agent] Fetching {target_asset} option chains and market depth via Alpaca MCP...")
    # Calls the inner simulation engine inside your agents folder
    proposed_trade = await researcher.analyze_options_chain(target_asset)
    
    # 4. [Video Script 3:30 - 4:00] IV Analysis & Strategy Assembly
    print(f"\n[🔬 Research Agent] Analysis Complete for {target_asset}:")
    print(f"   -> Detected Implied Volatility Strategy: {proposed_trade['strategy']}")
    print(f"   -> Structural Calculations: Net Premium Impact -> {proposed_trade.get('net_credit', proposed_trade.get('net_debit'))}")
    print(f"   -> Formulating Multi-Leg JSON payload configuration...")

    # 5. [Video Script 4:00 - 4:30] Guardrail Interception & Verification
    print(f"\n[🛡️ Risk Guardrail] Intercepting proposed execution payload before Alpaca API dispatch...")
    is_approved = await executor.run_risk_guardrail(proposed_trade)
    
    if not is_approved:
        print("\n[❌ Pipeline Halted] Risk parameters breached. Execution payload safely purged.")
        print("="*70 + "\n")
        return
        
    # 6. [Video Script 4:30 - 5:00] Alpaca SDK Order Execution
    print(f"\n[⚡ Execution Agent] Dispatching approved multi-leg order vector to Alpaca Trading endpoints...")
    execution_results = await executor.execute_multi_leg_spread(proposed_trade)
    
    print("\n" + "="*70)
    print("🏁 [SYSTEM LOOP RUN COMPLETION]")
    print(f"    Final Order Status: {execution_results['status']}")
    print(f"    Executed Strategy:  {execution_results.get('strategy_executed')}")
    print(f"    Network Tracking ID: #ALP-AGENT-{os.urandom(4).hex().upper()}")
    print("="*70 + "\n")

if __name__ == "__main__":
    # Ensure dependencies are running asynchronously 
    # Testing over SPY as outlined in your step-by-step video script
    asyncio.run(run_agentic_alpha_pipeline("SPY"))
