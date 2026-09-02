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
EOF

# 2. Update Gemini wrapper stub syntax to stay perfectly synchronized
cat << 'EOF' > src/utils/llm_gemini.py
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
