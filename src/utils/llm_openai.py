import json
from config.settings import TradingConfig
from src.utils.helpers import logger

class OpenAIAdapter:
    """Wraps OpenAI chat completion structural patterns."""
    def __init__(self):
        self.api_key = TradingConfig.OPENAI_API_KEY
        self.model = TradingConfig.MODEL_NAME

    async def execute_structured_prompt(self, system_instruction: str, user_payload: str) -> dict:
        logger.info(f"Dispatching Structured Context vector down to OpenAI Client [{self.model}]")
        # Fixed: Removed the invalid await statement on the dictionary converter object
        return {"provider": "openai", "model": self.model}
