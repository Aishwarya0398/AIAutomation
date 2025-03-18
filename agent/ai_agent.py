import os
import importlib
import pkgutil
from playwright.async_api import async_playwright
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from models.test_result_model import TestResult
import tasks  # Import the 'tasks' package dynamically
from tasks.login_tasks import task_login  # Ensure login task is available
from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException  # Correct exception

# Load environment variables from .env file
load_dotenv()


class AIAgent:
    def __init__(self):
        self.gemini_api_key = SecretStr(os.getenv("GEMINI_API_KEY"))
        self.openai_api_key = SecretStr(os.getenv("OPENAI_API_KEY"))

        if not self.gemini_api_key and not self.openai_api_key:
            raise ValueError("❌ Both GEMINI_API_KEY and OPENAI_API_KEY are missing! Provide at least one.")

        try:
            if self.gemini_api_key:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    api_key=self.gemini_api_key.get_secret_value()
                )
                print("✅ Using Google Gemini API")
            else:
                raise ValueError("GEMINI_API_KEY not found.")
        except (OutputParserException, ValueError, Exception) as e:
            print(f"⚠️ Google Gemini API Error: {e}. Switching to OpenAI GPT-4...")
            if self.openai_api_key:
                self.llm = ChatOpenAI(model="gpt-4", api_key=self.openai_api_key.get_secret_value())
                print("✅ Using OpenAI GPT-4 as fallback.")
            else:
                raise ValueError("❌ Both GEMINI_API_KEY and OPENAI_API_KEY are missing! Provide at least one.")

        self.controller = Controller(output_model=TestResult)
        self.browser = None
        self.page = None
        self.logged_in = False  # Track login status

    async def start_browser(self):
        """Start Playwright browser session ONCE for all tests."""
        if not self.browser:  # ✅ Prevent reopening browser
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
            print("✅ Browser started and ready for tests.")

    async def run_test(self, task):
        """✅ Runs a test while keeping the browser open across multiple tasks."""

        await self.start_browser()  # ✅ Ensures browser starts only once

        if task == task_login:
            print("🔹 Running Login Test...")
        else:
            # ✅ Perform login only ONCE in the same browser session
            if not self.logged_in:
                print("🔹 Performing Login Before Task Execution (Reusing Browser)...")

                # ✅ Run login task inside the same browser
                login_agent = Agent(task=task_login, llm=self.llm, controller=self.controller, use_vision=True)

                try:
                    login_result = await login_agent.run()
                    if "Success" in login_result.final_result():
                        self.logged_in = True
                        print("✅ Login successful. Session maintained.")
                    else:
                        raise Exception("❌ Login Failed.")
                except Exception as e:
                    print(f"⚠️ Login Error: {e}")
                    return None  # Stop execution if login fails

        print(f"🔹 Running Task: {task}")
        agent = Agent(task=task, llm=self.llm, controller=self.controller, use_vision=True)

        try:
            history = await agent.run()
            history.save_to_file('agent_results.json')
            print(f"🔍 Task Result: {history.final_result()}")
            return TestResult.model_validate_json(history.final_result())
        except Exception as e:
            print(f"⚠️ Task Execution Failed: {e}")
            return None

    async def close_browser(self):
        """Close the browser AFTER all tests."""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            print("✅ Browser closed successfully.")

