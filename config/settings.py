import os
from dotenv import load_dotenv

load_dotenv()


class TradingConfig:
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    IS_PAPER = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3.6-flash")
    LLM_ENABLED = bool(GEMINI_API_KEY)

    # Financial Controls
    MAX_RISK = float(os.getenv("MAX_RISK_PER_TRADE", "5.00"))
    MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.75"))
    MIN_REWARD_TO_RISK = float(os.getenv("MIN_REWARD_TO_RISK", "2.5"))
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "250.00"))
    TRADING_DRY_RUN = os.getenv("TRADING_DRY_RUN", "false").lower() == "true"

    # Options-first market watchlist
    DEFAULT_OPTION_WATCHLIST = [
        item.strip().upper()
        for item in os.getenv("OPTION_WATCHLIST", "SPY,QQQ,IWM").split(",")
        if item.strip()
    ]

    @classmethod
    def validate(cls):
        if not cls.API_KEY or not cls.SECRET_KEY:
            raise ValueError("⚠️ CRITICAL: Alpaca credentials are missing from the runtime environment.")
        if not cls.IS_PAPER:
            raise ValueError("⚠️ PAPER-ONLY MODE REQUIRED. Set ALPACA_IS_PAPER=true for this bot.")
        if cls.GEMINI_API_KEY:
            print("[⚙️ Model] Gemini key detected. LLM mode enabled.")
        else:
            print("[⚙️ Model] No Gemini key detected. Running in deterministic fallback mode.")
        return True
