import sys
import os
import pytest
from agent.ai_agent import AIAgent

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.mark.asyncio
@pytest.mark.order(2)
async def test_cart():
    ai_agent = AIAgent()
    result = await ai_agent.run_test("Cart")
    assert result, "❌ Cart Test Failed! Mismatch with expected result or missing items (see logs)."
