# The Research Core


import asyncio
import random
from config.settings import TradingConfig
from src.utils.helpers import UniversalFormatters, logger
from src.utils.llm_openai import OpenAIAdapter
from src.utils.llm_gemini import GeminiAdapter
from src.utils.llm_open_cloud import OpenCloudAdapter

class OptionsSpreadResearcher:
    """
    Advanced multi-LLM agent mapping option data chains directly into 
    risk-defined spread parameters.
    """
    def __init__(self):
        # Instantiate LLM controller adapters based on configuration settings
        self.provider = TradingConfig.LLM_PROVIDER
        if self.provider == "openai":
            self.llm = OpenAIAdapter()
        elif self.provider == "gemini":
            self.llm = GeminiAdapter()
        elif self.provider == "open_cloud":
            self.llm = OpenCloudAdapter()
        else:
            raise ValueError(f"Unknown LLM Provider: {self.provider}")

    async def analyze_market(self, symbol: str) -> str:
        """
        Reads historical telemetry via universal decorators and uses the 
        active LLM engine to choose strategies.
        """
        logger.info(f"[Research Engine] Activating analytical routing loop via provider: {self.provider.upper()}")
        await asyncio.sleep(1.0)
        
        simulated_iv_rank = random.randint(30, 85)
        spot_price = 150.00
        
        # Utilize the universal formatting utility component
        telemetry_log = UniversalFormatters.format_market_payload(ticker, spot_price, simulated_iv_rank)
        print(telemetry_log)
        
        # Execute LLM routing layer prompt pipeline simulation
        _ = await self.llm.execute_structured_prompt(
            system_instruction="You are an expert options premium pricing researcher modeling spread contracts.",
            user_payload=telemetry_log
        )
        
        # Strategy selection parsing layer
        if simulated_iv_rank > 50:
            return {
                "strategy": "BULL_PUT_SPREAD",
                "underlying": ticker,
                "spot_price": spot_price,
                "legs": [
                    {"side": "SELL", "type": "PUT", "strike": 145.0, "expiry": "2026-09-18"},
                    {"side": "BUY", "type": "PUT", "strike": 140.0, "expiry": "2026-09-18"}
                ],
                "net_credit": 1.25,
                "max_risk": 3.75
            }
        else:
            return {
                "strategy": "BULL_CALL_DEBIT_SPREAD",
                "underlying": ticker,
                "spot_price": spot_price,
                "legs": [
                    {"side": "BUY", "type": "CALL", "strike": 150.0, "expiry": "2026-09-18"},
                    {"side": "SELL", "type": "CALL", "strike": 155.0, "expiry": "2026-09-18"}
                ],
                "net_debit": 2.10,
                "max_risk": 2.10
            }