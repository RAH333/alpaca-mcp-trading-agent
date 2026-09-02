from config.settings import TradingConfig
from src.utils.helpers import logger

class OpenCloudAdapter:
    """Wraps message configurations required by Anthropic Claude engines hosted on cloud runtimes."""
    def __init__(self):
        self.api_key = TradingConfig.OPEN_CLOUD_API_KEY
        self.model = TradingConfig.MODEL_NAME if "claude" in TradingConfig.MODEL_NAME.lower() else "claude-3-5-sonnet"

    async def execute_structured_prompt(self, system_instruction: str, user_payload: str) -> dict:
        logger.info(f" Dispatching message block contexts down to OpenCloud Claude Engine [{self.model}]")
        return {"provider": "open_cloud", "model": self.model}
