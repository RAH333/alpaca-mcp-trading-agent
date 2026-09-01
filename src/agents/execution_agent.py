import asyncio
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from alpaca.data.historical.option import OptionHistoricalDataClient
    from alpaca.data.requests import OptionChainRequest
except ImportError:  # pragma: no cover
    OptionHistoricalDataClient = None  # type: ignore[assignment]
    OptionChainRequest = None  # type: ignore[assignment]

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.enums import OrderClass, OrderSide, OrderType, TimeInForce
    from alpaca.trading.requests import MarketOrderRequest, OptionLegRequest
except ImportError:  # pragma: no cover
    TradingClient = None  # type: ignore[assignment]
    MarketOrderRequest = None  # type: ignore[assignment]
    OptionLegRequest = None  # type: ignore[assignment]
    OrderClass = None  # type: ignore[assignment]
    OrderSide = None  # type: ignore[assignment]
    OrderType = None  # type: ignore[assignment]
    TimeInForce = None  # type: ignore[assignment]


class OptionsExecutionAgent:
    """
    Safe paper-only execution path for multi-leg options spreads.
    It validates the research output, manages the lifecycle of an open position,
    and exits with a defined target/stop or on a manual close.
    """

    def __init__(
        self,
        trading_client=None,
        max_allowed_risk: float = 5.0,
        min_confidence: float = 0.75,
        min_reward_to_risk: float = 2.5,
        dry_run: Optional[bool] = None,
    ):
        self.client = trading_client or self._build_client_if_possible()
        self.max_allowed_risk = float(max_allowed_risk)
        self.min_confidence = float(min_confidence)
        self.min_reward_to_risk = float(min_reward_to_risk)
        env_dry_run = os.getenv("TRADING_DRY_RUN", "false").lower() == "true"
        self.dry_run = env_dry_run if dry_run is None else bool(dry_run)
        self.paper_mode = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trade_log: List[Dict[str, Any]] = []

    def _build_client_if_possible(self):
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        if not TradingClient or not api_key or not secret_key:
            return None
        return TradingClient(api_key=api_key, secret_key=secret_key, paper=True)

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _normalize_expiry(self, expiry: Any) -> str:
        if expiry is None:
            raise ValueError("Every option leg requires an expiry.")
        expiry_str = str(expiry).strip()
        if expiry_str.isdigit() and len(expiry_str) == 6:
            return expiry_str
        expiry_str = expiry_str.replace("-", "")
        if expiry_str.isdigit() and len(expiry_str) == 8:
            return expiry_str[2:8]
        if expiry_str.isdigit() and len(expiry_str) == 6:
            return expiry_str
        raise ValueError(f"Unsupported option expiry format: {expiry!r}")

    def _resolve_valid_expiry(self, underlying: str, expiry: Any) -> str:
        expiry_code = self._normalize_expiry(expiry)

        if not OptionHistoricalDataClient or not OptionChainRequest:
            return expiry_code

        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        if not api_key or not secret_key:
            return expiry_code

        try:
            client = OptionHistoricalDataClient(api_key=api_key, secret_key=secret_key)
            chain = client.get_option_chain(OptionChainRequest(underlying_symbol=str(underlying or "").upper()))
            valid_expiries = {
                str(symbol)[3:9]
                for symbol in (chain or {}).keys()
                if isinstance(symbol, str) and len(symbol) >= 9 and str(symbol)[:3].upper() == str(underlying or "").upper()[:3]
            }
            if expiry_code in valid_expiries:
                return expiry_code

            try:
                target = datetime.strptime(f"20{expiry_code[0:2]}-{expiry_code[2:4]}-{expiry_code[4:6]}", "%Y-%m-%d")
            except Exception:
                return expiry_code

            def _day_delta(candidate: str) -> int:
                try:
                    candidate_dt = datetime.strptime(f"20{candidate[0:2]}-{candidate[2:4]}-{candidate[4:6]}", "%Y-%m-%d")
                    return abs((candidate_dt - target).days)
                except Exception:
                    return 10**9

            sorted_expiries = sorted(valid_expiries, key=_day_delta)
            if sorted_expiries:
                return sorted_expiries[0]
        except Exception:
            pass

        return expiry_code

    def _build_option_symbol(self, underlying: str, strike: Any, expiry: Any, option_type: str) -> str:
        underlying = str(underlying or "").upper().strip()
        option_type = str(option_type or "").upper().strip()
        if option_type not in {"CALL", "PUT"}:
            raise ValueError(f"Unsupported option type: {option_type!r}")

        expiry_code = self._resolve_valid_expiry(underlying, expiry)
        strike_price = self._safe_float(strike)
        strike_digits = int(round(strike_price * 1000))
        return f"{underlying}{expiry_code}{option_type[0]}{strike_digits:08d}"

    def _reward_to_risk(self, proposed_trade: Dict[str, Any]) -> float:
        max_risk = self._safe_float(proposed_trade.get("max_risk"), 0.0)
        if max_risk <= 0:
            return 0.0

        net_credit = self._safe_float(proposed_trade.get("net_credit"), 0.0)
        net_debit = self._safe_float(proposed_trade.get("net_debit"), 0.0)

        if net_credit > 0:
            return net_credit / max_risk
        if net_debit > 0:
            return (max_risk / net_debit) if net_debit > 0 else 0.0
        return 0.0

    def has_open_position(self, symbol: str) -> bool:
        key = str(symbol or "").upper()
        position = self.positions.get(key)
        return bool(position and position.get("is_open"))

    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self.positions.get(str(symbol or "").upper())

    async def run_risk_guardrail(self, proposed_trade: dict) -> bool:
        """Reject weak or overly risky trades before they reach the order book."""
        if not isinstance(proposed_trade, dict):
            print("[❌ Risk Rejected] Proposed trade must be a dictionary payload.")
            return False

        strategy = str(proposed_trade.get("strategy", "HOLD")).upper()
        if strategy == "HOLD":
            print("[❌ Risk Rejected] Strategy is HOLD and cannot be executed.")
            return False

        underlying = str(proposed_trade.get("underlying") or "").upper()
        if underlying and self.has_open_position(underlying):
            print(f"[⚠️ Risk Rejected] {underlying} already has an open position.")
            return False

        confidence = self._safe_float(proposed_trade.get("confidence"), 0.0)
        max_risk = self._safe_float(proposed_trade.get("max_risk"), 0.0)
        rr = self._reward_to_risk(proposed_trade)

        if confidence < self.min_confidence:
            print(f"[❌ Risk Rejected] Confidence {confidence:.2f} is below minimum {self.min_confidence:.2f}.")
            return False

        if max_risk <= 0:
            print("[❌ Risk Rejected] Max risk is missing or non-positive.")
            return False

        if max_risk > self.max_allowed_risk:
            print(f"[❌ Risk Rejected] Max risk ${max_risk:.2f} exceeds allowed ${self.max_allowed_risk:.2f}.")
            return False

        if rr < self.min_reward_to_risk:
            print(f"[❌ Risk Rejected] Reward-to-risk {rr:.2f} is below minimum {self.min_reward_to_risk:.2f}.")
            return False

        print("[✅ Risk Passed] Trade cleared the live risk gate and is safe to consider for paper execution.")
        return True

    def _build_multileg_order_request(self, spread_payload: Dict[str, Any]):
        """Build a real Alpaca MLEG order request from the research payload."""
        if not OrderClass or not OrderType or not TimeInForce or not OptionLegRequest:
            raise RuntimeError("Alpaca trading SDK is unavailable or not configured.")

        underlying = str(spread_payload.get("underlying") or "SPY").upper()
        legs: List[OptionLegRequest] = []

        for leg in spread_payload.get("legs", []):
            leg_type = str(leg.get("type", "CALL")).upper()
            leg_side = str(leg.get("side", "BUY")).upper()
            strike = leg.get("strike")
            expiry = leg.get("expiry")
            symbol = leg.get("symbol") or self._build_option_symbol(underlying, strike, expiry, leg_type)

            if leg_side == "BUY":
                order_side = OrderSide.BUY
            elif leg_side == "SELL":
                order_side = OrderSide.SELL
            else:
                raise ValueError(f"Unsupported leg side: {leg_side!r}")

            legs.append(
                OptionLegRequest(
                    symbol=symbol,
                    ratio_qty=1,
                    side=order_side,
                )
            )

        return MarketOrderRequest(
            qty=1,
            order_class=OrderClass.MLEG,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
            client_order_id=f"agenticalpha-{os.urandom(4).hex()}",
            legs=legs,
        )

    async def handle_trade_decision(self, proposed_trade: dict) -> Dict[str, Any]:
        """Validate the signal, enter the position if it passes, and record state."""
        if not isinstance(proposed_trade, dict):
            return {"status": "REJECTED_INVALID_PAYLOAD"}

        strategy = str(proposed_trade.get("strategy", "HOLD")).upper()
        underlying = str(proposed_trade.get("underlying") or "").upper()
        if strategy == "HOLD":
            return {"status": "REJECTED_NO_SIGNAL", "strategy_executed": strategy, "underlying": underlying}

        if underlying and self.has_open_position(underlying):
            return {
                "status": "POSITION_ALREADY_OPEN",
                "strategy_executed": strategy,
                "underlying": underlying,
                "position": self.positions[underlying],
            }

        approved = await self.run_risk_guardrail(proposed_trade)
        if not approved:
            return {"status": "REJECTED_BY_RISK_ENGINE", "strategy_executed": strategy, "underlying": underlying}

        execution_result = await self.execute_multi_leg_spread(proposed_trade)
        if execution_result.get("status") in {"DRY_RUN", "FILLED", "PENDING"}:
            entry_price = self._safe_float(proposed_trade.get("entry_price"), self._safe_float(proposed_trade.get("net_debit"), 0.0) or self._safe_float(proposed_trade.get("max_risk"), 0.0))
            self.positions[underlying] = {
                "symbol": underlying,
                "strategy": strategy,
                "is_open": True,
                "entry_price": entry_price,
                "entry_status": execution_result.get("status"),
                "max_risk": self._safe_float(proposed_trade.get("max_risk"), 0.0),
                "confidence": self._safe_float(proposed_trade.get("confidence"), 0.0),
                "legs": proposed_trade.get("legs", []),
                "opened_at": __import__("datetime").datetime.utcnow().isoformat(),
            }
            self.trade_log.append(
                {
                    "symbol": underlying,
                    "strategy": strategy,
                    "status": "ENTRY_OPEN",
                    "confidence": self._safe_float(proposed_trade.get("confidence"), 0.0),
                    "max_risk": self._safe_float(proposed_trade.get("max_risk"), 0.0),
                    "entry_price": entry_price,
                }
            )
            execution_result["position_opened"] = True
            execution_result["position"] = self.positions[underlying]
            execution_result["underlying"] = underlying
            return execution_result

        return execution_result

    async def close_position(self, symbol: str, reason: str = "manual", exit_price: Optional[float] = None) -> Dict[str, Any]:
        key = str(symbol or "").upper()
        position = self.positions.get(key)
        if not position or not position.get("is_open"):
            return {"status": "NO_OPEN_POSITION", "symbol": key, "reason": reason}

        entry_price = self._safe_float(position.get("entry_price"), 0.0)
        exit_value = self._safe_float(exit_price, entry_price)
        pnl = exit_value - entry_price

        broker_result = None
        if self.client and not self.dry_run:
            try:
                broker_result = self.client.close_position(key)
            except Exception as exc:
                print(f"[⚠️ Close Warning] Alpaca close failed for {key}: {exc}")
                broker_result = {"status": "ERROR", "message": str(exc)}

        self.positions[key]["is_open"] = False
        self.positions[key]["exit_price"] = exit_value
        self.positions[key]["exit_reason"] = reason
        self.positions[key]["pnl"] = pnl

        self.trade_log.append(
            {
                "symbol": key,
                "status": "EXIT",
                "reason": reason,
                "entry_price": entry_price,
                "exit_price": exit_value,
                "pnl": pnl,
                "broker_result": broker_result,
            }
        )

        return {
            "status": "CLOSED",
            "symbol": key,
            "reason": reason,
            "entry_price": entry_price,
            "exit_price": exit_value,
            "pnl": pnl,
            "broker_result": broker_result,
        }

    async def evaluate_exit_conditions(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """Close a position when a stop, target, or expiry condition is reached."""
        key = str(symbol or "").upper()
        position = self.positions.get(key)
        if not position or not position.get("is_open"):
            return {"status": "NO_OPEN_POSITION", "symbol": key}

        entry_price = self._safe_float(position.get("entry_price"), 0.0)
        stop_loss_pct = self._safe_float(position.get("stop_loss_pct"), 0.10)
        take_profit_pct = self._safe_float(position.get("take_profit_pct"), 0.20)
        current = self._safe_float(current_price, entry_price)

        stop_loss_price = entry_price * (1.0 - stop_loss_pct)
        take_profit_price = entry_price * (1.0 + take_profit_pct)

        if current <= stop_loss_price:
            return await self.close_position(key, "stop_loss", exit_price=current)
        if current >= take_profit_price:
            return await self.close_position(key, "target", exit_price=current)

        return {"status": "OPEN", "symbol": key, "current_price": current}

    async def execute_multi_leg_spread(self, spread_payload: dict):
        """Execute a research-approved spread in paper trading or return a dry-run result."""
        if not isinstance(spread_payload, dict):
            return {"status": "REJECTED_INVALID_PAYLOAD"}

        strategy = str(spread_payload.get("strategy", "HOLD")).upper()
        if strategy == "HOLD":
            return {"status": "REJECTED_NO_SIGNAL", "strategy_executed": strategy}

        is_safe = await self.run_risk_guardrail(spread_payload)
        if not is_safe:
            return {"status": "REJECTED_BY_RISK_ENGINE", "strategy_executed": strategy}

        try:
            order_request = self._build_multileg_order_request(spread_payload)
        except Exception as exc:
            print(f"[⚠️ Execution Warning] Could not build market order: {exc}")
            return {
                "status": "REJECTED_BAD_LEGS",
                "strategy_executed": strategy,
                "message": str(exc),
            }

        if not self.client or self.dry_run:
            return {
                "status": "DRY_RUN",
                "strategy_executed": strategy,
                "order_request": getattr(order_request, "model_dump", lambda: order_request.__dict__)(),
                "net_premium_effect": spread_payload.get("net_credit") or spread_payload.get("net_debit"),
            }

        try:
            account = self.client.get_account()
            if getattr(account, "status", "") != "ACTIVE":
                return {"status": "ACCOUNT_INACTIVE", "strategy_executed": strategy}

            order = self.client.submit_order(order_request)
            return {
                "status": "FILLED",
                "strategy_executed": strategy,
                "order_id": getattr(order, "id", None),
                "order_status": getattr(order, "status", None),
                "net_premium_effect": spread_payload.get("net_credit") or spread_payload.get("net_debit"),
            }
        except Exception as exc:
            print(f"[❌ Execution Error] Alpaca order submission failed: {exc}")
            return {
                "status": "ERROR",
                "strategy_executed": strategy,
                "message": str(exc),
            }


__all__ = ["OptionsExecutionAgent"]

