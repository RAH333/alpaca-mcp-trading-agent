import asyncio
from config.settings import TradingConfig
from src.agents.research_agent import OptionsSpreadResearcher
from src.agents.execution_agent import OptionsExecutionAgent
from src.utils.helpers import logger

# Import the app to keep routing pathways explicitly clear if Vercel targets this submodule directory
from main import app

class AutonomousTradingRuntime:
    """System entry engine validating credentials and processing order flow."""
    def __init__(self):
        TradingConfig.validate()
        self.researcher = OptionsSpreadResearcher()
        self.executor = OptionsExecutionAgent(max_allowed_risk=TradingConfig.MAX_RISK)

    async def system_heartbeat_loop(self, watch_ticker: str):
        print("\n====================================================================")
        print(" DELTAGUARD AUTONOMOUS ENGINE INITIALIZED | POWERED BY ALPACA MCP")
        print(f"   ACTIVE BACKBONE LLM INTERFACE PROVIDER: {TradingConfig.LLM_PROVIDER.upper()}")
        print("====================================================================\n")
        
        # Step 1: Query research adapter metrics
        proposed_spread = await self.researcher.analyze_options_chain(watch_ticker)
        
        # Step 2: Route order structure to the execution safety network
        logger.info(f"Routing detected spread sequence model ({proposed_spread['strategy']}) to risk processors...")
        execution_receipt = await self.executor.execute_multi_leg_spread(proposed_spread)
        
        print(f"\n[ Sequence Summary] Processing Results: {execution_receipt['status']}")
        print("====================================================================\n")

if __name__ == "__main__":
    runtime = AutonomousTradingRuntime()
    asyncio.run(runtime.system_heartbeat_loop("AAPL"))
