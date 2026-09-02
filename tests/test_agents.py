import pytest
from src.agents.research_agent import OptionsSpreadResearcher
from src.agents.execution_agent import OptionsExecutionAgent

@pytest.mark.asyncio
async def test_research_agent_generation():
    researcher = OptionsSpreadResearcher()
    result = await researcher.analyze_options_chain("SPY")
    
    assert "strategy" in result
    assert "underlying" in result
    assert result["underlying"] == "SPY"
    assert len(result["legs"]) > 0

@pytest.mark.asyncio
async def test_risk_guardrail_pass():
    executor = OptionsExecutionAgent(max_allowed_risk=0.05)
    
    safe_trade = {
        "underlying": "SPY",
        "max_risk": 2.50
    }
    
    is_safe = await executor.run_risk_guardrail(safe_trade)
    assert is_safe is True

@pytest.mark.asyncio
async def test_risk_guardrail_breach():
    executor = OptionsExecutionAgent(max_allowed_risk=0.05)
    
    dangerous_trade = {
        "underlying": "SPY",
        "max_risk": 12.50 # Way too high, should fail verification checks
    }
    
    is_safe = await executor.run_risk_guardrail(dangerous_trade)
    assert is_safe is False
  
