import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    IS_PAPER = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")
    
    # Financial Controls
    MAX_RISK = float(os.getenv("MAX_PORTFOLIO_RISK_PERCENT", "0.05"))
    
    @classmethod
    def validate(cls):
        if not cls.API_KEY or not cls.SECRET_KEY:
            raise ValueError("⚠️ CRITICAL: Alpaca Credentials missing from environmental runtime context.")
        if not cls.OPENAI_API_KEY:
            raise ValueError("⚠️ CRITICAL: LLM Backbone context API keys are absent.")
