import pytest
import asyncio
import sys
import os

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent.ai_agent import AIAgent  # ✅ Use absolute import
from tasks.login_tasks import task_login  # ✅ Use absolute import

@pytest.mark.asyncio
@pytest.mark.order(1)
@pytest.mark.dependency(name="test_login")
async def test_login(request):
    ai_agent = AIAgent()
    result = await ai_agent.run_test(task_login)

    expected_status = "success"
    actual_status = result.login_status if result else "None"

    # Convert both values to lowercase before assertion
    expected_status = expected_status.lower()
    actual_status = actual_status.lower()

    # Print and return assertion string
    assertion_message = f"Expected: {expected_status}, Actual: {actual_status}"
    print(f"🔍 Login Test: {assertion_message}")

    assert actual_status == expected_status, f"❌ Login Failed! {assertion_message}"

    # ✅ **Explicitly register the test result for pytest-dependency**
    request.node.add_marker(pytest.mark.dependency())
