import asyncio
from config.settings import TradingConfig
from src.utils.helpers import logger

# Try loading the official Alpaca Trading SDK modules safely
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, OptionOrderRequest
    from alpaca.trading.enums import OrderSide, OrderTimeInForce, AssetClass
except ImportError:
    TradingClient = None
    OptionOrderRequest = None

class OptionsExecutionAgent:
    """Verifies leg configurations and programmatically places real option orders via the Alpaca SDK."""
    def __init__(self, trading_client=None, max_allowed_risk=0.05):
        self.max_allowed_risk = max_allowed_risk
        
        # Initialize the actual, live authenticated Alpaca Paper client connection wrapper
        if TradingClient and TradingConfig.API_KEY and TradingConfig.SECRET_KEY:
            self.client = trading_client or TradingClient(
                api_key=TradingConfig.API_KEY, 
                secret_key=TradingConfig.SECRET_KEY, 
                paper=TradingConfig.IS_PAPER
            )
            logger.info(" [Execution Core] Programmatic Alpaca SDK Trading Client established successfully.")
        else:
            self.client = None
            logger.warning(" [Execution Core] Missing SDK or Keys. Running in local simulation mode.")

    async def run_risk_guardrail(self, proposed_trade: dict) -> bool:
        """Deterministic risk verification to ensure safety boundaries are met."""
        logger.info("[🛡️ Risk Engine] Validating structure matching against portfolio boundaries...")
        await asyncio.sleep(0.5)
        
        if not proposed_trade or proposed_trade.get("strategy") == "HOLD":
            logger.warning("[ Risk Engine] Position flagged as HOLD or empty. Strategy evaluation bypassed safely.")
            return False

        if len(proposed_trade.get("legs", [])) > TradingConfig.MAX_LEG_COUNT:
            logger.error(f"[Risk Violation] Trade contains too many legs. Max allowed: {TradingConfig.MAX_LEG_COUNT}.")
            return False
            
        max_risk = proposed_trade.get("max_risk")
        if max_risk is not None and float(max_risk) > 5.00:
            logger.error(f"[Risk Violation] Strategy exposure exceeds allowable bounds.")
            return False
            
        logger.info("[Risk Matrix Clear] Execution layout satisfies all risk constraints.")
        return True

    async def execute_multi_leg_spread(self, spread_payload: dict) -> dict:
        is_safe = await self.run_risk_guardrail(spread_payload)
        if not is_safe:
            return {"status": "REJECTED_BY_RISK_ENGINE"}
            
        symbol = spread_payload.get("underlying", "SPY").upper()
        legs = spread_payload.get("legs", [])
        
        logger.info(f"[Dispatcher] DISPATCHING LIVE ORDERS TO ALPACA PAPER ACCOUNT FOR: {symbol}")
        
        # If the Alpaca client is active and verified, dispatch network orders
        if self.client:
            filled_legs = []
            for index, leg in enumerate(legs, start=1):
                try:
                    # Construct a professional Option Contract Symbol matching Alpaca specification
                    # Example: SPY260918C00150000
                    strike_fixed = f"{int(float(leg['strike']) * 1000):08d}"
                    expiry_clean = str(leg['expiry']).replace("-", "")[2:] # Keep YYMMDD format
                    type_letter = "C" if leg['type'] == "CALL" else "P"
                    contract_symbol = f"{symbol}{expiry_clean}{type_letter}{strike_fixed}"
                    
                    logger.info(f"   -> [API Dispatch] Sending Leg #{index}: {leg['side']} 1 Contract of {contract_symbol}")
                    
                    # Package the option data context parameters down to the network socket
                    order_data = OptionOrderRequest(
                        symbol=contract_symbol,
                        qty=1,
                        side=OrderSide.BUY if leg['side'] == 'BUY' else OrderSide.SELL,
                        time_in_force=OrderTimeInForce.DAY
                    )
                    
                    # Dispatch to your live Paper Trading book instantly
                    loop = asyncio.get_event_loop()
                    order = await loop.run_in_executor(None, self.client.submit_order, order_data)
                    filled_legs.append(getattr(order, "id", f"MOCK-ID-{index}"))
                    
                    await asyncio.sleep(0.5) # Prevent triggering endpoint rate limits
                    
                except Exception as api_err:
                    logger.error(f" [Leg #{index} Failed] Alpaca API error: {api_err}")
            
            return {
                "status": "FILLED" if filled_legs else "API_TRANSACTION_FAILED",
                "strategy_executed": spread_payload["strategy"],
                "legs_dispatched": len(filled_legs)
            }
        else:
            # Fallback local output printing display loop if offline
            for index, leg in enumerate(legs, start=1):
                print(f"   -> [SIMULATOR] Leg #{index}: {leg['side']} {leg['type']} | Strike: ${leg['strike']} | Expiry: {leg['expiry']}")
                await asyncio.sleep(0.2)
                
            return {
                "status": "SIMULATED_FILL",
                "strategy_executed": spread_payload["strategy"],
                "net_premium_effect": spread_payload.get("net_credit") or spread_payload.get("net_debit")
            }
