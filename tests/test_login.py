import sys
import os
import pytest
from agent.ai_agent import AIAgent

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_login():
    ai_agent = AIAgent()
    result = await ai_agent.run_test("Login")
    assert result, "❌ Login Test Failed! Mismatch with expected result in Excel."
