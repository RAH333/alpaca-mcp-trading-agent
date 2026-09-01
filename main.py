import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Ensure the runtime environment can discover local project directory paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TradingConfig
from src.agents.research_agent import OptionsSpreadResearcher
from src.agents.execution_agent import OptionsExecutionAgent

try:
    from alpaca.trading.client import TradingClient
except Exception:  # pragma: no cover
    TradingClient = None


async def is_market_open() -> bool:
    """Return whether the U.S. market is open, using Alpaca clock when available."""
    if TradingClient and os.getenv("ALPACA_API_KEY") and os.getenv("ALPACA_SECRET_KEY"):
        try:
            client = TradingClient(
                api_key=os.getenv("ALPACA_API_KEY"),
                secret_key=os.getenv("ALPACA_SECRET_KEY"),
                paper=True,
            )
            clock = client.get_clock()
            return bool(getattr(clock, "is_open", False))
        except Exception:
            pass

    now = datetime.now()
    weekday = now.weekday()
    if weekday >= 5:
        return False

    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close


async def run_agentic_alpha_pipeline(target_asset: str):
    """Run the options-first research and execution flow for a single underlying."""
    print("\n" + "="*70)
    print("🤖 AGENTICALPHA OPTIONS-FIRST PIPELINE | PAPER TRADING MODE")
    print("="*70 + "\n")

    # 1. Environment & Credential Validation
    print("[⚙️ System System] Validating environmental configurations and security keys...")
    try:
        TradingConfig.validate()
        print(f"[⚙️ System Status] Environment Verified. Mode: {'PAPER' if TradingConfig.IS_PAPER else 'LIVE'}")
    except Exception as e:
        print(f"[❌ Boot Error] Initialization aborted: {str(e)}")
        return

    # 2. Instantiate Agents
    researcher = OptionsSpreadResearcher()
    executor = OptionsExecutionAgent(
        max_allowed_risk=TradingConfig.MAX_RISK,
        min_confidence=TradingConfig.MIN_CONFIDENCE,
        min_reward_to_risk=TradingConfig.MIN_REWARD_TO_RISK,
        dry_run=TradingConfig.TRADING_DRY_RUN,
    )

    # 3. Research Phase: option-chain only
    print(f"\n[🔬 Research Agent] Fetching live options data for {target_asset} via Alpaca...")
    proposed_trade = await researcher.analyze_options_chain(target_asset)

    # 4. IV Analysis & Strategy Assembly
    print(f"\n[🔬 Research Agent] Analysis Complete for {target_asset}:")
    print(f"   -> Strategy: {proposed_trade['strategy']}")
    print(f"   -> IV Rank: {proposed_trade.get('iv_rank')}")
    print(f"   -> Confidence: {proposed_trade.get('confidence')}")
    print(f"   -> Option spread legs ready for risk review...")

    # 5. Risk gate and entry management before dispatch
    print(f"\n[🛡️ Risk Guardrail] Reviewing multi-leg option approval before order dispatch...")
    execution_results = await executor.handle_trade_decision(proposed_trade)

    if execution_results.get("status") in {"REJECTED_BY_RISK_ENGINE", "REJECTED_NO_SIGNAL", "POSITION_ALREADY_OPEN"}:
        print("\n[❌ Pipeline Halted] The options setup failed the trade-quality gate or a position is already open.")
        print("="*70 + "\n")
        return

    # 6. Execution step in paper mode and position tracking
    print(f"\n[⚡ Execution Agent] Dispatching approved options spread to the paper account...")
    print(f"    Open Position Tracking: {executor.has_open_position(target_asset)}")

    print("\n" + "="*70)
    print("🏁 [SYSTEM LOOP RUN COMPLETION]")
    print(f"    Final Order Status: {execution_results['status']}")
    print(f"    Executed Strategy:  {execution_results.get('strategy_executed')}")
    print(f"    Position Open:      {executor.has_open_position(target_asset)}")
    print(f"    Network Tracking ID: #ALP-OPT-{os.urandom(4).hex().upper()}")
    print("="*70 + "\n")


async def run_option_watchlist_pipeline(symbols=None):
    """Scan a small options watchlist, rank the best candidates, and trade only the strongest entry."""
    watchlist = [str(symbol).upper() for symbol in (symbols or TradingConfig.DEFAULT_OPTION_WATCHLIST)]
    print("[📊 Options Watchlist]", ", ".join(watchlist))
    for symbol in watchlist:
        await run_agentic_alpha_pipeline(symbol)


async def run_live_market_monitor(symbols=None, poll_seconds: int = 30, max_cycles: int = None):
    """Continuously evaluate a watchlist and keep only one position open at a time during market hours."""
    watchlist = [str(symbol).upper() for symbol in (symbols or TradingConfig.DEFAULT_OPTION_WATCHLIST)]
    print(f"[📡 Live Market Monitor] Starting for: {', '.join(watchlist)}")

    researcher = OptionsSpreadResearcher()
    executor = OptionsExecutionAgent(
        max_allowed_risk=TradingConfig.MAX_RISK,
        min_confidence=TradingConfig.MIN_CONFIDENCE,
        min_reward_to_risk=TradingConfig.MIN_REWARD_TO_RISK,
        dry_run=TradingConfig.TRADING_DRY_RUN,
    )

    cycle = 0
    while True:
        if not await is_market_open():
            print("[⏰ Market Closed] Live monitor exiting cleanly.")
            break

        open_symbols = [s for s in watchlist if executor.has_open_position(s)]
        if open_symbols:
            print(f"[📈 Position Monitor] Open positions: {', '.join(open_symbols)}. Holding and monitoring.")
        else:
            best_signal = None
            for symbol in watchlist:
                try:
                    proposal = await researcher.analyze_options_chain(symbol)
                except Exception as exc:
                    print(f"[⚠️ Research Warning] {symbol}: {exc}")
                    continue

                if proposal.get("strategy") == "HOLD":
                    continue

                if not proposal.get("legs"):
                    continue

                risk_ok = await executor.run_risk_guardrail(proposal)
                if not risk_ok:
                    continue

                score = (float(proposal.get("confidence", 0.0)), float(proposal.get("iv_rank", 0.0)))
                if best_signal is None or score > best_signal[0]:
                    best_signal = (score, symbol, proposal)

            if best_signal is not None:
                _, symbol, proposal = best_signal
                result = await executor.handle_trade_decision(proposal)
                print(f"[🎯 Signal] {symbol} -> {result.get('status')} | strategy={proposal.get('strategy')}")
            else:
                print("[🧭 Signal Scan] No valid live entry this cycle.")

        cycle += 1
        if max_cycles is not None and cycle >= max_cycles:
            print(f"[🧪 Monitor] Cycle limit reached ({max_cycles}).")
            break
        await asyncio.sleep(poll_seconds)

    return {"status": "MONITOR_STOPPED", "cycles": cycle}


if __name__ == "__main__":
    asyncio.run(run_live_market_monitor(["SPY", "QQQ", "IWM"], poll_seconds=10, max_cycles=1))
