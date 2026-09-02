from config.settings import TradingConfig
from src.utils.helpers import logger

class GeminiAdapter:
    """Wraps native structural objects for Google Gemini API models."""
    def __init__(self):
        self.api_key = TradingConfig.GEMINI_API_KEY
        self.model = TradingConfig.MODEL_NAME if "gemini" in TradingConfig.MODEL_NAME.lower() else "gemini-2.5-flash"

    async def execute_structured_prompt(self, system_instruction: str, user_payload: str) -> dict:
        logger.info(f"Dispatching Context content vectors down to Gemini Client [{self.model}]")
        return {"provider": "gemini", "model": self.model}
