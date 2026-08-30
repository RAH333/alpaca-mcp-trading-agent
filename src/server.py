"""
# Main Entry Point
This script instantiates the workspace, orchestrating the connection between the LLM backbone and
the Alpaca Trading Infrastructure via the Model Context Protocol.
"""

import os
import asyncio
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from src.agents.research_agent import MarketResearcher
from src.agents.execution_agent import TradeExecutor

# Load secrets securely
load_dotenv()

class AlpacaAIPlatform:
    def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.is_paper = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Missing critical Alpaca API Credentials inside .env file.")
            
        # Instantiate physical Alpaca Python SDK Client
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=self.is_paper)
        
        # Instantiate Multi-Agent Pipeline
        self.researcher = MarketResearcher()
        self.executor = TradeExecutor(self.trading_client)

    async def run_autonomous_cycle(self, target_ticker: str):
        print(f"[🤖 Agent Matrix] Initiating loop for symbol: {target_ticker}")
        
        # Step 1: Query LLM for news extraction or raw sentiment analysis
        signal = await self.researcher.analyze_market(target_ticker)
        print(f"[🔬 Research Agent] Signal generated: {signal}")
        
        # Step 2: Route actions down to execution via Alpaca wrappers
        if signal in ["BUY", "SELL"]:
            order_receipt = await self.executor.execute_signal(target_ticker, signal)
            print(f"[⚡ Execution Agent] Execution Confirmed: {order_receipt}")
        else:
            print("[💤 System Status] Holding positions. No market entry parameters met.")

if __name__ == "__main__":
    platform = AlpacaAIPlatform()
    # Simulate a run on Apple stock
    asyncio.run(platform.run_autonomous_cycle("AAPL"))
