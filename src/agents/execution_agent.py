import asyncio
from config.settings import TradingConfig
from src.utils.helpers import logger

class OptionsExecutionAgent:
    """Verifies leg configuration parameters and simulates direct execution."""
    def __init__(self, trading_client=None, max_allowed_risk=0.05):
        self.client = trading_client
        self.max_allowed_risk = max_allowed_risk

    async def run_risk_guardrail(self, proposed_trade: dict) -> bool:
        """Deterministic risk verification to ensure safety boundaries are met."""
        logger.info("[Risk Engine] Validating structure matching against portfolio boundaries...")
        await asyncio.sleep(0.5)
        
        # Safety Check: If the trade is empty or labeled as HOLD, skip risk calculations safely
        if not proposed_trade or proposed_trade.get("strategy") == "HOLD":
            logger.warning("[Risk Engine] Position flagged as HOLD or empty. Bypassing metrics validation.")
            return False

        if len(proposed_trade.get("legs", [])) > TradingConfig.MAX_LEG_COUNT:
            logger.error(f"[Risk Violation] Trade contains too many legs. Max allowed: {TradingConfig.MAX_LEG_COUNT}.")
            return False
            
        # Fixed: Safe extraction preventing NoneType math comparison crashes
        max_risk = proposed_trade.get("max_risk")
        if max_risk is None or float(max_risk) > 5.00:
            logger.error(f"[Risk Violation] Strategy exposure (${max_risk}) exceeds allowable bounds.")
            return False
            
        logger.info("[Risk Matrix Clear] Execution layout satisfies all risk constraints.")
        return True

    async def execute_multi_leg_spread(self, spread_payload: dict) -> dict:
        is_safe = await self.run_risk_guardrail(spread_payload)
        if not is_safe:
            return {"status": "REJECTED_BY_RISK_ENGINE"}
            
        logger.info(f"[Dispatcher] Routing orders to live books for target ticker: {spread_payload['underlying']}")
        
        for index, leg in enumerate(spread_payload.get("legs", []), start=1):
            print(f"   -> Leg #{index}: {leg['side']} {leg['type']} | Strike: ${leg['strike']} | Expiry: {leg['expiry']}")
            await asyncio.sleep(0.3)
            
        return {
            "status": "FILLED",
            "strategy_executed": spread_payload["strategy"],
            "net_premium_effect": spread_payload.get("net_credit") or spread_payload.get("net_debit")
        }
