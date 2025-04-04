AI-powered Playwright Test Automation Framework that:

* Reads test steps and expectations from an Excel sheet.
* Converts the test steps into "tasks" for an LLM (Gemini/OpenAI).
* Executes browser actions using playwright + LangChain Agent.
* Validates the results by comparing them to Excel-defined expectations.
* Automatically handles login before other tests.
* Outputs results as .json files for traceability.

**ai_agent.py**
Responsibilities:
* Read test steps from Excel.
* Compose test into a LangChain Agent.
* Ask AI (Gemini or GPT-4) to interpret the task.
* Validate if the AI output matches the Expected Result from Excel.
* If Cart, it also checks Expected Cart Items.

**Core Functions and their Purpose**
* __init__()	- Setup API keys, load LLM, initialize browser placeholders.
* initialize_llm()	- Chooses Gemini API (default) or GPT-4 as fallback. Temperature is set to 0.0 for stability.
* start_browser()	- Starts a single Playwright browser to be reused across multiple tests.
* load_test_cases() -	Dynamically fetches steps, expected results, expected cart items from Excel based on 
Test Name.
* is_loosely_matched()	- Fuzzy-matching logic that checks if expected keywords are present in the AI-generated 
result fields.
* run_test(test_name) -	Executes the task by asking the LLM to perform actions described in Excel. Validates results 
against Excel. Automatically handles login if needed.
* close_browser() -	Closes the browser after all tests finish.

Excel → AI Agent → LLM → Playwright Automation → Result → Fuzzy Assertion → Pass/Fail