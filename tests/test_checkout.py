import pytest
import asyncio
import sys
import os

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.ai_agent import AIAgent  # ✅ Use absolute import
from tasks.checkout_tasks import task_checkout  # ✅ Use absolute import

@pytest.mark.asyncio
@pytest.mark.order(3)
async def test_checkout():
    ai_agent = AIAgent()
    result = await ai_agent.run_test(task_checkout)

    expected_status = "completed"
    actual_status = result.checkout_status if result else "None"

    # Convert both values to lowercase before assertion
    expected_status = expected_status.lower()
    actual_status = actual_status.lower()

    # Print and return assertion string
    assertion_message = f"Expected: {expected_status}, Actual: {actual_status}"
    print(f"🔍 Checkout Test: {assertion_message}")

    assert actual_status == expected_status, f"❌ Checkout Test Failed! {assertion_message}"

