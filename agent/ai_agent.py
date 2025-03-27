import os
import re
import pandas as pd
from playwright.async_api import async_playwright
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from models.test_result_model import TestResult
from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException

# Load environment variables
load_dotenv()

class AIAgent:
    def __init__(self, test_case_file="test_cases.xlsx"):
        self.gemini_api_key = SecretStr(os.getenv("GEMINI_API_KEY"))
        self.openai_api_key = SecretStr(os.getenv("OPENAI_API_KEY"))
        self.test_case_file = test_case_file
        self.logged_in = False
        self.browser = None
        self.page = None

        self.llm = self.initialize_llm()
        self.controller = Controller(output_model=TestResult)

    def initialize_llm(self):
        if not self.gemini_api_key and not self.openai_api_key:
            raise ValueError("❌ Both GEMINI_API_KEY and OPENAI_API_KEY are missing!")

        try:
            if self.gemini_api_key:
                print("✅ Using Google Gemini API")
                return ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    api_key=self.gemini_api_key.get_secret_value(),
                    temperature=0.0  # Low variability
                )
            raise ValueError("GEMINI_API_KEY not found.")
        except Exception as e:
            print(f"⚠️ Gemini error: {e}, trying OpenAI...")
            if self.openai_api_key:
                print("✅ Using OpenAI GPT-4")
                return ChatOpenAI(
                    model="gpt-4",
                    api_key=self.openai_api_key.get_secret_value(),
                    temperature=0.0
                )
            raise ValueError("❌ No valid LLM key found.")

    async def start_browser(self):
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
            print("✅ Browser started")

    def load_test_cases(self, test_name):
        try:
            df = pd.read_excel(self.test_case_file)

            steps = df[df["Test Name"] == test_name]["Step Description"].tolist()
            result_rows = df[(df["Test Name"] == test_name) & df["Expected Result"].notna()]
            expected_result = result_rows["Expected Result"].values[0] if not result_rows.empty else None

            cart_row = df[(df["Test Name"] == test_name) & df["Expected Cart Items"].notna()]
            expected_cart_items = cart_row["Expected Cart Items"].values[0].split(", ") if not cart_row.empty else []

            if not steps:
                raise ValueError(f"❌ No steps for {test_name}")

            return "\n".join(steps), expected_result, expected_cart_items
        except Exception as e:
            print(f"⚠️ Error loading Excel: {e}")
            return None, None, []

    def is_loosely_matched(self, expected, result_obj):
        """Fuzzy match expected keywords against result fields."""
        expected_words = re.findall(r'\w+', expected.lower())

        all_fields = " ".join([
            getattr(result_obj, "confirmation_message", ""),
            getattr(result_obj, "login_status", ""),
            getattr(result_obj, "checkout_status", "")
        ]).lower()

        return any(word in all_fields for word in expected_words)

    async def run_test(self, test_name):
        await self.start_browser()

        steps, expected_result, expected_cart_items = self.load_test_cases(test_name)
        if not steps:
            return False

        # 🔐 Perform login once if needed
        if test_name.lower() != "login" and not self.logged_in:
            print("🔹 Login before task...")
            login_steps, _, _ = self.load_test_cases("Login")
            if not login_steps:
                print("❌ Missing login steps")
                return False
            login_agent = Agent(task=login_steps, llm=self.llm, controller=self.controller, use_vision=True)
            try:
                login_result = await login_agent.run()
                login_json = login_result.final_result()
                print(f"🔍 Login Output: {login_json}")
                if "success" in login_json.lower():
                    self.logged_in = True
                    print("✅ Logged in successfully")
                else:
                    return False
            except Exception as e:
                print(f"❌ Login error: {e}")
                return False

        # 🚀 Run main task
        print(f"🔹 Running: {test_name}")
        agent = Agent(task=steps, llm=self.llm, controller=self.controller, use_vision=True)

        try:
            history = await agent.run()
            result = TestResult.model_validate_json(history.final_result())
            history.save_to_file(f'agent_results_{test_name}.json')
            print(f"🔍 Task Result: {result}")

            # ✅ Expected result fuzzy validation
            if expected_result:
                if not self.is_loosely_matched(expected_result, result):
                    print(f"❌ Test FAILED! Expected: {expected_result}, Got: {result.confirmation_message}")
                    return False
                print("✅ Test PASSED! Expected result matched.")

            # ✅ Cart items validation
            if test_name.lower() == "cart" and expected_cart_items:
                actual_items = result.cart_items if isinstance(result.cart_items, list) else []
                print(f"🔍 Cart Items Found: {actual_items}")
                print(f"🔍 Expected Cart Items: {expected_cart_items}")
                missing = [
                    item for item in expected_cart_items
                    if item.lower() not in [i.lower() for i in actual_items]
                ]
                if missing:
                    print(f"❌ Missing items: {missing}")
                    return False
                print("✅ All cart items matched")

            return True
        except Exception as e:
            print(f"❌ Task failed: {e}")
            return False

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            print("✅ Browser closed")
