import asyncio
import json
import os
from statistics import median
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

try:
    from alpaca.data.historical.option import OptionHistoricalDataClient
    from alpaca.data.historical.stock import StockHistoricalDataClient
    from alpaca.data.requests import OptionChainRequest, StockLatestTradeRequest
except ImportError:  # pragma: no cover
    OptionHistoricalDataClient = None  # type: ignore[assignment]
    StockHistoricalDataClient = None  # type: ignore[assignment]
    OptionChainRequest = None  # type: ignore[assignment]
    StockLatestTradeRequest = None  # type: ignore[assignment]


class OptionsSpreadResearcher:
    """
    Live data-first research layer for defined-risk option setups.
    It uses real Alpaca option-chain snapshots and only returns a trade when the
    signal clears a strict quality and confidence gate.
    """

    VALID_STRATEGIES = {
        "BULL_PUT_SPREAD",
        "BEAR_CALL_SPREAD",
        "IRON_CONDOR",
        "BULL_CALL_DEBIT_SPREAD",
        "BEAR_PUT_DEBIT_SPREAD",
        "HOLD",
    }

    MIN_CONFIDENCE = 0.65

    def __init__(self, llm_client: Optional[Any] = None, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash")
        gemini_key = os.getenv("GEMINI_API_KEY")
        legacy_openai_key = os.getenv("OPENAI_API_KEY")
        self.api_key = gemini_key or legacy_openai_key

        base_url = None
        if gemini_key:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        self.client = llm_client or (
            OpenAI(api_key=self.api_key, base_url=base_url) if OpenAI and self.api_key else None
        )
        self.llm_enabled = bool(self.api_key and self.client)

        self.alpaca_api_key = os.getenv("ALPACA_API_KEY")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.alpaca_is_paper = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"

        self.data_client = None
        self.stock_data_client = None
        if OptionHistoricalDataClient and self.alpaca_api_key and self.alpaca_secret_key:
            self.data_client = OptionHistoricalDataClient(
                api_key=self.alpaca_api_key,
                secret_key=self.alpaca_secret_key,
            )
        if StockHistoricalDataClient and self.alpaca_api_key and self.alpaca_secret_key:
            self.stock_data_client = StockHistoricalDataClient(
                api_key=self.alpaca_api_key,
                secret_key=self.alpaca_secret_key,
            )

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _mid_price_from_snapshot(self, payload: Dict[str, Any]) -> Optional[float]:
        quote = payload.get("latest_quote") or {}
        bid = self._safe_float(quote.get("bid_price"))
        ask = self._safe_float(quote.get("ask_price"))
        if bid and ask and ask >= bid:
            return (bid + ask) / 2.0

        trade = payload.get("latest_trade") or {}
        price = self._safe_float(trade.get("price"))
        if price:
            return price
        return None

    def _option_expiry_from_symbol(self, option_symbol: str) -> str:
        option_symbol = (option_symbol or "").upper()
        if len(option_symbol) >= 9 and option_symbol[0:2].isalpha():
            try:
                return option_symbol[3:9]
            except Exception:
                pass
        return "UNKNOWN"

    def _option_side_from_symbol(self, option_symbol: str) -> str:
        symbol = (option_symbol or "").upper()
        match = next((ch for ch in symbol[::-1][:9] if ch in {"C", "P"}), None)
        if match == "C":
            return "CALL"
        if match == "P":
            return "PUT"
        return "UNKNOWN"

    def _option_strike_from_symbol(self, option_symbol: str) -> Optional[float]:
        symbol = (option_symbol or "").upper()
        if len(symbol) < 10:
            return None
        try:
            type_index = max(i for i, ch in enumerate(symbol) if ch in {"C", "P"})
            digits = symbol[type_index + 1:]
            if len(digits) != 8 or not digits.isdigit():
                return None
            return float(int(digits)) / 1000.0
        except ValueError:
            return None

    def _parse_snapshot(self, option_symbol: str, snapshot: Any) -> Optional[Dict[str, Any]]:
        if hasattr(snapshot, "model_dump"):
            payload = snapshot.model_dump()
        elif hasattr(snapshot, "dict"):
            payload = snapshot.dict()
        elif isinstance(snapshot, dict):
            payload = dict(snapshot)
        else:
            payload = dict(getattr(snapshot, "__dict__", {}))

        if not payload:
            return None

        symbol = str(payload.get("symbol") or option_symbol).upper()
        strike = payload.get("strike_price")
        if strike is None:
            strike = self._option_strike_from_symbol(symbol)
        iv = payload.get("implied_volatility")
        if iv is None and hasattr(snapshot, "implied_volatility"):
            iv = getattr(snapshot, "implied_volatility")
        if strike is None or iv is None:
            return None

        mid_price = self._mid_price_from_snapshot(payload)
        if mid_price is None:
            return None

        return {
            "symbol": symbol,
            "expiry": self._option_expiry_from_symbol(symbol),
            "strike": float(strike),
            "iv": float(iv),
            "volume": self._safe_int(payload.get("volume")),
            "open_interest": self._safe_int(payload.get("open_interest")),
            "mid_price": float(mid_price),
            "type": self._option_side_from_symbol(symbol),
        }

    async def analyze_options_chain(self, ticker: str) -> dict:
        """Analyze the live option chain and return a research proposal or HOLD."""
        symbol = (ticker or "SPY").upper()
        print(f"[🔬 Research Agent] Fetching live option-chain data for {symbol}...")

        chain = await self._fetch_option_chain_snapshot(symbol)
        iv_rank = self._calculate_iv_rank(chain)

        proposal = await self._build_strategy_proposal(symbol, chain, iv_rank)
        proposal = self._apply_quality_gate(symbol, chain, proposal, iv_rank)

        proposal.setdefault("underlying", symbol)
        proposal.setdefault("spot_price", chain.get("spot_price", 0.0))
        proposal.setdefault("iv_rank", iv_rank)
        proposal.setdefault("direction", "NEUTRAL")

        print(
            f"[🔬 Research Agent] {symbol} | spot=${chain.get('spot_price', 0.0):.2f} | "
            f"IV Rank={iv_rank:.2f}% | strategy={proposal.get('strategy')} | conf={proposal.get('confidence', 0.0):.2f}"
        )
        return proposal

    async def _fetch_option_chain_snapshot(self, ticker: str) -> Dict[str, Any]:
        """Fetch the live option chain from Alpaca and normalize the real response object."""
        symbol = (ticker or "SPY").upper()

        if not self.data_client or not OptionChainRequest:
            raise RuntimeError(
                "Alpaca option data is unavailable. Ensure ALPACA_API_KEY, ALPACA_SECRET_KEY, "
                "and the alpaca-py SDK are configured correctly."
            )

        req = OptionChainRequest(underlying_symbol=symbol)
        raw_chain = self.data_client.get_option_chain(req)

        if not isinstance(raw_chain, dict) or not raw_chain:
            raise RuntimeError(f"Alpaca returned an empty option chain for {symbol}.")

        if self.stock_data_client and StockLatestTradeRequest:
            stock_trade = self.stock_data_client.get_stock_latest_trade(
                StockLatestTradeRequest(symbol_or_symbols=[symbol])
            )
            if isinstance(stock_trade, dict):
                stock_payload = stock_trade.get(symbol, {})
                if hasattr(stock_payload, "model_dump"):
                    stock_payload = stock_payload.model_dump()
                elif hasattr(stock_payload, "dict"):
                    stock_payload = stock_payload.dict()
                if hasattr(stock_payload, "get"):
                    stock_price = self._safe_float(stock_payload.get("price"))
                else:
                    stock_price = self._safe_float(getattr(stock_payload, "price", 0.0))
            else:
                stock_price = self._safe_float(getattr(stock_trade, "price", 0.0))
        else:
            stock_price = 0.0

        parsed_calls: List[Dict[str, Any]] = []
        parsed_puts: List[Dict[str, Any]] = []
        iv_values: List[float] = []

        for option_symbol, snapshot in raw_chain.items():
            parsed = self._parse_snapshot(option_symbol, snapshot)
            if parsed is None:
                continue
            iv_values.append(parsed["iv"])
            item = {
                "symbol": parsed["symbol"],
                "expiry": parsed["expiry"],
                "strike": parsed["strike"],
                "iv": parsed["iv"],
                "volume": parsed["volume"],
                "open_interest": parsed["open_interest"],
                "mid_price": parsed["mid_price"],
            }
            if parsed["type"] == "CALL":
                parsed_calls.append(item)
            elif parsed["type"] == "PUT":
                parsed_puts.append(item)

        if not iv_values:
            raise ValueError(f"No valid option snapshots with IV data were returned for {symbol}.")

        valid_options = sorted(parsed_calls + parsed_puts, key=lambda item: item["strike"])
        if not valid_options:
            raise ValueError(f"No valid call/put options were returned for {symbol}.")

        spot_price = stock_price if stock_price > 0 else float(median([item["mid_price"] for item in valid_options]))
        current_iv = median(iv_values)
        liquidity_score = self._calculate_liquidity_score(valid_options)
        trend_score = self._calculate_trend_score(parsed_calls, parsed_puts)

        return {
            "symbol": symbol,
            "spot_price": float(spot_price),
            "current_iv": float(current_iv),
            "iv_values": [float(iv) for iv in iv_values],
            "calls": sorted(parsed_calls, key=lambda item: item["strike"])[:12],
            "puts": sorted(parsed_puts, key=lambda item: item["strike"])[:12],
            "liquidity_score": liquidity_score,
            "trend_score": trend_score,
        }

    def _calculate_liquidity_score(self, options: List[Dict[str, Any]]) -> float:
        if not options:
            return 0.0

        volume_values = [max(item.get("volume", 0), 0) for item in options]
        avg_volume = sum(volume_values) / len(volume_values)
        avg_bid_ask = []
        for item in options:
            if item.get("mid_price") is not None:
                avg_bid_ask.append(item.get("mid_price", 0.0))

        volume_component = min(avg_volume / 150.0, 1.0)
        price_component = min(len(avg_bid_ask) / max(len(options), 1), 1.0)
        return round(max(0.0, min(1.0, (volume_component * 0.7) + (price_component * 0.3))), 3)

    def _calculate_trend_score(self, calls: List[Dict[str, Any]], puts: List[Dict[str, Any]]) -> float:
        call_volume = sum(max(item.get("volume", 0), 0) for item in calls)
        put_volume = sum(max(item.get("volume", 0), 0) for item in puts)
        total_volume = max(call_volume + put_volume, 1)
        delta = (call_volume - put_volume) / total_volume
        return round(max(0.0, min(1.0, 0.5 + (delta * 0.5))), 3)

    def _calculate_iv_rank(self, chain: Dict[str, Any]) -> float:
        """Compute a 0-100 IV rank from the live option-chain IV distribution."""
        iv_values = [float(v) for v in chain.get("iv_values") or []]
        current_iv = float(chain.get("current_iv", 0.0 or iv_values[-1] if iv_values else 0.0))

        if not iv_values:
            return 50.0

        low = min(iv_values)
        high = max(iv_values)
        if high == low:
            return 50.0

        rank = ((current_iv - low) / (high - low)) * 100.0
        return round(max(0.0, min(100.0, rank)), 2)

    def _apply_quality_gate(
        self,
        ticker: str,
        chain: Dict[str, Any],
        proposal: Dict[str, Any],
        iv_rank: float,
    ) -> Dict[str, Any]:
        """Filter weak live setups and force HOLD unless the live data is compelling."""
        strategy = str(proposal.get("strategy", "HOLD")).upper()
        confidence = float(proposal.get("confidence", 0.0))
        liquidity = float(chain.get("liquidity_score", 0.0))
        trend = float(chain.get("trend_score", 0.0))

        if strategy not in self.VALID_STRATEGIES:
            strategy = "HOLD"

        passes_liquidity = liquidity >= 0.5
        passes_trend = trend >= 0.45
        passes_confidence = confidence >= self.MIN_CONFIDENCE
        passes_iv = 20.0 <= iv_rank <= 85.0

        if not (passes_liquidity and passes_trend and passes_confidence and passes_iv):
            return {
                "strategy": "HOLD",
                "direction": "NEUTRAL",
                "confidence": 0.0,
                "rationale": (
                    "Signal rejected by the live-data quality gate: insufficient liquidity, weak trend read, "
                    "lack of confidence, or IV regime outside the allowed range."
                ),
                "legs": [],
                "net_credit": None,
                "net_debit": None,
                "max_risk": None,
                "iv_rank": iv_rank,
                "underlying": ticker.upper(),
            }

        proposal["strategy"] = strategy
        proposal["confidence"] = max(0.0, min(1.0, confidence))
        proposal["rationale"] = proposal.get("rationale", "Live option chain and IV rank passed the research gate.")
        proposal["iv_rank"] = iv_rank
        proposal["underlying"] = ticker.upper()
        return proposal

    def _build_prompt(self, ticker: str, chain: Dict[str, Any], iv_rank: float) -> str:
        """Craft a strict prompt with the actual live market snapshot."""
        return f"""
You are a disciplined options research agent.

Your goal is to decide whether a defined-risk options spread is justified by the live market snapshot.
Do not invent any options prices, expiries, or direction that are not present in the data.

Hard rules:
- Prefer defined-risk spreads and avoid naked trades.
- Reject the trade if the data is illiquid or weak.
- If IV rank > 70, premium-selling spreads are more attractive, but only if liquidity and trend are supportive.
- If IV rank < 30, avoid premium selling and favor defensive debit spreads or HOLD.
- Return JSON only; no markdown.
- Allowed strategies: BULL_PUT_SPREAD, BEAR_CALL_SPREAD, IRON_CONDOR, BULL_CALL_DEBIT_SPREAD, BEAR_PUT_DEBIT_SPREAD, HOLD.

Live context:
- ticker: {ticker}
- spot_price: {chain['spot_price']}
- current_iv: {chain['current_iv']}
- iv_rank: {iv_rank}
- liquidity_score: {chain.get('liquidity_score', 0.0)}
- trend_score: {chain.get('trend_score', 0.0)}
- calls: {json.dumps(chain['calls'])}
- puts: {json.dumps(chain['puts'])}

Return JSON with this exact schema:
{{
  "strategy": "<allowed strategy>",
  "direction": "<BULLISH|BEARISH|NEUTRAL>",
  "confidence": <0.0 to 1.0>,
  "rationale": "<short reason>",
  "legs": [
    {{"side": "SELL|BUY", "type": "CALL|PUT", "strike": <number>, "expiry": "<string>"}}
  ],
  "net_credit": <number or null>,
  "net_debit": <number or null>,
  "max_risk": <number or null>
}}
"""

    def _build_tool_schema(self) -> List[Dict[str, Any]]:
        """Strict OpenAI tool-calling schema for a more AI-native options workflow."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "score_option_setup",
                    "description": "Score a live option setup for risk, liquidity, and conviction before turning it into a trade signal.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "iv_rank": {"type": "number"},
                            "liquidity_score": {"type": "number"},
                            "trend_score": {"type": "number"},
                            "direction": {"type": "string", "enum": ["BULLISH", "BEARISH", "NEUTRAL"]},
                        },
                        "required": ["symbol", "iv_rank", "liquidity_score", "trend_score", "direction"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "propose_option_spread",
                    "description": "Produce the final options spread recommendation from the scored live chain.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "strategy": {"type": "string"},
                            "direction": {"type": "string"},
                            "confidence": {"type": "number"},
                            "rationale": {"type": "string"},
                            "legs": {"type": "array"},
                            "max_risk": {"type": "number"},
                        },
                        "required": ["symbol", "strategy", "direction", "confidence", "rationale", "legs"],
                    },
                },
            },
        ]

    def _extract_ai_json(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract the model payload, preferring tool-call output or JSON content."""
        try:
            message = getattr(response.choices[0], "message", None)
            if message is None:
                return None

            if getattr(message, "tool_calls", None):
                tool_call = message.tool_calls[0]
                args = getattr(tool_call, "function", None)
                if args is not None:
                    raw_args = getattr(args, "arguments", None)
                    if isinstance(raw_args, str):
                        return json.loads(raw_args)
                    if isinstance(raw_args, dict):
                        return raw_args

            content = getattr(message, "content", None)
            if content:
                return json.loads(content)
        except Exception:
            return None
        return None

    async def _build_strategy_proposal(self, ticker: str, chain: Dict[str, Any], iv_rank: float) -> Dict[str, Any]:
        """Use the AI model as the primary strategy engine, with a conservative fallback if the model fails."""
        prompt = self._build_prompt(ticker, chain, iv_rank)

        if self.client is None:
            return self._fallback_strategy(ticker, chain, iv_rank)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an autonomous volatility and options research specialist. "
                            "Use only the provided live market data, keep all risk controls strict, "
                            "and only propose defined-risk options trades when the setup is high conviction. "
                            "If the data is weak, return HOLD with confidence 0.0."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                tools=self._build_tool_schema(),
                tool_choice="auto",
                max_tokens=500,
            )

            parsed = self._extract_ai_json(response)
            if parsed is None:
                return self._fallback_strategy(ticker, chain, iv_rank)

            normalized = self._normalize_response(parsed, iv_rank)
            if normalized.get("strategy") == "HOLD" and normalized.get("confidence", 0.0) == 0.0:
                return normalized

            if normalized.get("strategy") not in self.VALID_STRATEGIES:
                return self._fallback_strategy(ticker, chain, iv_rank)

            return normalized
        except Exception:
            return self._fallback_strategy(ticker, chain, iv_rank)

    def _normalize_response(self, payload: Dict[str, Any], iv_rank: float) -> Dict[str, Any]:
        """Normalize any LLM payload into a safe schema."""
        strategy = str(payload.get("strategy", "HOLD")).upper()
        if strategy not in self.VALID_STRATEGIES:
            strategy = "HOLD"

        confidence = self._safe_float(payload.get("confidence"), 0.0)
        confidence = max(0.0, min(1.0, confidence))

        return {
            "strategy": strategy,
            "direction": str(payload.get("direction", "NEUTRAL")).upper(),
            "confidence": confidence,
            "rationale": str(payload.get("rationale", "Strategy chosen from live IV context.")),
            "legs": payload.get("legs", []),
            "net_credit": payload.get("net_credit"),
            "net_debit": payload.get("net_debit"),
            "max_risk": payload.get("max_risk"),
            "iv_rank": iv_rank,
            "underlying": payload.get("underlying", "UNKNOWN"),
        }

    def _fallback_strategy(self, ticker: str, chain: Dict[str, Any], iv_rank: float) -> Dict[str, Any]:
        """No synthetic trade logic. If the environment cannot produce a valid live signal, the agent returns HOLD."""
        return {
            "strategy": "HOLD",
            "direction": "NEUTRAL",
            "confidence": 0.0,
            "rationale": "No valid live option-chain signal cleared the research gate; the system is holding instead of forcing a synthetic trade.",
            "legs": [],
            "net_credit": None,
            "net_debit": None,
            "max_risk": None,
            "iv_rank": iv_rank,
            "underlying": ticker.upper(),
        }


class MarketResearcher:
    """Backward-compatible wrapper for older scripts expecting a simple signal."""

    def __init__(self, *args, **kwargs):
        self._impl = OptionsSpreadResearcher(*args, **kwargs)

    async def analyze_market(self, symbol: str) -> str:
        proposal = await self._impl.analyze_options_chain(symbol)
        return proposal.get("strategy", "HOLD")


__all__ = ["OptionsSpreadResearcher", "MarketResearcher"]
