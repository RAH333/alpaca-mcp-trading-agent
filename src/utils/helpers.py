import sys
import logging
from datetime import datetime

# Initialize uniform logging matrix for hackathon evaluation visibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DeltaGuardRuntime")

class UniversalFormatters:
    @staticmethod
    def format_market_payload(ticker: str, spot_price: float, iv_rank: float) -> str:
        """Standardizes market metrics into structured telemetry text across all tokenizers."""
        return (
            f"=== MARKET TELEMETRY RECEIPT ===\n"
            f"TIMESTAMP   : {datetime.now().isoformat()}\n"
            f"UNDERLYING  : {ticker}\n"
            f"SPOT PRICE  : ${spot_price:.2f}\n"
            f"IMPLIED VOLATILITY RANK: {iv_rank}%\n"
            f"================================"
        )

    @staticmethod
    def clean_json_markdown(raw_string: str) -> str:
        """Strips out standard markdown block decorations before passing to raw string compilers."""
        return raw_string.replace("```json", "").replace("```", "").strip()
