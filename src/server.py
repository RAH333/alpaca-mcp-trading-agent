import asyncio
from config.settings import TradingConfig
from src.agents.research_agent import OptionsSpreadResearcher
from src.agents.execution_agent import OptionsExecutionAgent

class AutonomousTradingRuntime:
    """
    Orchestration center driving the autonomous loop logic for the 
    LabLab.ai Alpaca AI Hackathon.
    """
    def __init__(self):
        TradingConfig.validate()
        self.researcher = OptionsSpreadResearcher()
        self.executor = OptionsExecutionAgent(max_allowed_risk=TradingConfig.MAX_RISK)

    async def system_heartbeat_loop(self, watch_ticker: str):
        print("====================================================================")
        print("🤖 DELTAGUARD AUTONOMOUS ENGINE INITIALIZED | POWERED BY ALPACA MCP")
        print("====================================================================\n")
        
        # Step 1: Initialize Research phase over the target ticker options chains
        proposed_spread = await self.researcher.analyze_options_chain(watch_ticker)
        
        # Step 2: Pass output to Execution and Risk Control Layer
        print(f"\n[🤖 Router] Routing determined {proposed_spread['strategy']} to Risk Engine...")
        execution_receipt = await self.executor.execute_multi_leg_spread(proposed_spread)
        
        print(f"\n[🏁 Cycle Completed] System Loop Status: {execution_receipt['status']}")
        print("====================================================================")

if __name__ == "__main__":
    runtime = AutonomousTradingRuntime()
    # Execute loop tracking a typical high liquidity equity target
    asyncio.run(runtime.system_heartbeat_loop("AAPL"))
