import unittest

from src.agents.execution_agent import OptionsExecutionAgent


class TestExecutionAgent(unittest.IsolatedAsyncioTestCase):
    async def test_position_manager_tracks_entry_and_exit(self):
        agent = OptionsExecutionAgent(dry_run=True)

        trade = {
            "strategy": "BULL_CALL_DEBIT_SPREAD",
            "underlying": "SPY",
            "confidence": 0.9,
            "max_risk": 5.0,
            "net_debit": 1.25,
            "legs": [
                {"side": "BUY", "type": "CALL", "strike": 540.0, "expiry": "20260115"},
                {"side": "SELL", "type": "CALL", "strike": 545.0, "expiry": "20260115"},
            ],
        }

        result = await agent.handle_trade_decision(trade)
        self.assertIn(result["status"], {"DRY_RUN", "FILLED", "PENDING"})
        self.assertTrue(agent.has_open_position("SPY"))

        exit_result = await agent.close_position("SPY", "target", exit_price=542.0)
        self.assertEqual(exit_result["status"], "CLOSED")
        self.assertFalse(agent.has_open_position("SPY"))

    async def test_exit_logic_hits_stop_and_target(self):
        agent = OptionsExecutionAgent(dry_run=True)
        agent.positions["SPY"] = {
            "symbol": "SPY",
            "strategy": "BULL_CALL_DEBIT_SPREAD",
            "is_open": True,
            "entry_price": 100.0,
            "max_risk": 5.0,
            "confidence": 0.9,
            "stop_loss_pct": 0.10,
            "take_profit_pct": 0.20,
            "legs": [],
        }

        stop_result = await agent.evaluate_exit_conditions("SPY", 89.0)
        self.assertEqual(stop_result["status"], "CLOSED")
        self.assertEqual(stop_result["reason"], "stop_loss")

        agent.positions["SPY"] = {
            "symbol": "SPY",
            "strategy": "BULL_CALL_DEBIT_SPREAD",
            "is_open": True,
            "entry_price": 100.0,
            "max_risk": 5.0,
            "confidence": 0.9,
            "stop_loss_pct": 0.10,
            "take_profit_pct": 0.20,
            "legs": [],
        }

        target_result = await agent.evaluate_exit_conditions("SPY", 121.0)
        self.assertEqual(target_result["status"], "CLOSED")
        self.assertEqual(target_result["reason"], "target")

    async def test_close_position_submits_real_alpaca_close_order(self):
        class FakeClient:
            def __init__(self):
                self.closed = []

            def close_position(self, symbol):
                self.closed.append(symbol)
                return {"symbol": symbol, "status": "closed"}

        agent = OptionsExecutionAgent(dry_run=False)
        agent.client = FakeClient()
        agent.positions["SPY"] = {
            "symbol": "SPY",
            "strategy": "BULL_CALL_DEBIT_SPREAD",
            "is_open": True,
            "entry_price": 100.0,
            "max_risk": 5.0,
            "confidence": 0.9,
            "stop_loss_pct": 0.10,
            "take_profit_pct": 0.20,
            "legs": [],
        }

        result = await agent.close_position("SPY", "target", exit_price=110.0)

        self.assertEqual(result["status"], "CLOSED")
        self.assertEqual(agent.client.closed, ["SPY"])
        self.assertFalse(agent.has_open_position("SPY"))


if __name__ == "__main__":
    unittest.main()
