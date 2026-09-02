import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    # Alpaca Credentials
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    IS_PAPER = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"
    
    # Model Architecture Router
    # Options: "openai" | "gemini" | "open_cloud"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")
    
    # Provider-Specific API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPEN_CLOUD_API_KEY = os.getenv("OPEN_CLOUD_API_KEY") # For Anthropic Claude
    
    # Financial Risk Parameters
    MAX_RISK = float(os.getenv("MAX_PORTFOLIO_RISK_PERCENT", "0.05"))
    MAX_LEG_COUNT = int(os.getenv("MAX_LEG_COUNT", "4"))
    
    @classmethod
    def validate(cls):
        """Validates configuration contexts to guarantee seamless runtime execution."""
        if not cls.API_KEY or not cls.SECRET_KEY:
            raise ValueError(" CRITICAL: Alpaca API keys are missing from environmental context.")
            
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError(" CRITICAL: OpenAI Provider selected but OPENAI_API_KEY is missing.")
            
        elif cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError(" CRITICAL: Gemini Provider selected but GEMINI_API_KEY is missing.")
            
        elif cls.LLM_PROVIDER == "open_cloud" and not cls.OPEN_CLOUD_API_KEY:
            raise ValueError(" CRITICAL: Open Cloud (Anthropic) Provider selected but OPEN_CLOUD_API_KEY is missing.")
            
