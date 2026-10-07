# ParaBank browser and API automation

An extensible Python automation framework for the [ParaBank demo banking application](https://parabank.parasoft.com/parabank/index.htm), built with Playwright, pytest, and requests. Its structure and ParaBank-specific coverage were informed by [banking-playwright-project](https://github.com/sukanyagit2026/banking-playwright-project); the page objects, configuration, fixtures, and tests here are implemented for this repository.

> ParaBank is a public test application, not a real bank. UI tests that change data create a unique customer for each test instead of using the shared demo account. The demo account is reserved for read-only login and overview checks. The public service is shared and may be slow or temporarily unavailable.

## Coverage

- Login, invalid login, and customer registration
- Account overview and data-driven checking/savings account creation
- Transfers with account-balance verification
- Bill payments
- Transaction search
- Loan request result handling
- Read-only REST API checks for login, customers, accounts, and transactions
- Chromium, Firefox, and WebKit execution, HTML reports, and failure artifacts in GitHub Actions

## Project layout

```text
pages/                    Page Objects: selectors/actions for each ParaBank screen
tests/                    UI, API, and AI-helper unit tests
test_data/                JSON inputs for data-driven tests
utils/                    Environment settings, API client, and shared helpers
ai_assistant/             Optional local Ollama and cloud test-design helpers
.github/workflows/        Browser/API CI and GitHub Pages deployment
conftest.py               Shared pytest fixtures and browser setup
pytest.ini                Test discovery, markers, and Playwright artifacts
requirements.txt           Python packages for the tests and helpers
docs/                     Static project guide published through GitHub Pages
```

## Setup

Requires Python 3.10 or newer.

```powershell
cd C:\Users\admin\parabank
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
Copy-Item .env.example .env
```

If you haven't created a virtual environment yet, run `python -m venv .venv` first. You can use `.\.venv\Scripts\python.exe` directly if PowerShell blocks venv activation. On macOS/Linux, activate with `source .venv/bin/activate` or use the venv's Python executable directly. Edit `.env` only when targeting a different ParaBank deployment; do not commit credentials or local environment files.

## Run tests

```powershell
# Read-only API checks (no browser)
.\.venv\Scripts\python.exe -m pytest -m api

# Safe read-only UI checks in headless Chromium
.\.venv\Scripts\python.exe -m pytest -m "ui and not stateful" --browser chromium -k "not invalid_credentials"

# The same UI checks with a visible browser
.\.venv\Scripts\python.exe -m pytest -m "ui and not stateful" --browser chromium --headed -k "not invalid_credentials"

# Run one test file, or collect test names without running them
.\.venv\Scripts\python.exe -m pytest tests/test_accounts.py --browser chromium
.\.venv\Scripts\python.exe -m pytest --collect-only -q
```

To run the full suite, including state-changing tests, use `.\.venv\Scripts\python.exe -m pytest`. Stateful tests register customers and can change data on ParaBank's shared public demo. Registration and invalid-login behavior on that server have been inconsistent; see the scenario table below. Do not use real banking credentials or sensitive data.

To create a standalone HTML report:

```powershell
New-Item -ItemType Directory -Force reports
.\.venv\Scripts\python.exe -m pytest -m api --html=reports/api-report.html --self-contained-html
```

`pytest.ini` is the pytest-playwright configuration entry point; the Python Playwright pytest plugin does not consume the Node.js `playwright.config.py` format.

### Test scenarios

| Scenario | Test | What it checks |
|---|---|---|
| Demo login | `tests/test_login.py` | Uses the shared demo account and checks that the account overview loads. Read-only. |
| Invalid login | `tests/test_login.py` | Checks the invalid-credentials response. The public demo has been observed accepting the invalid credentials, so this test currently fails against that server; exclude it with `-k "not invalid_credentials"`. |
| Registration | `tests/test_login.py` plus `registered_customer` | Submits the registration form and expects success. The shared public service has sometimes reported generated usernames as already taken, causing dependent stateful tests to error during setup. |
| Account overview | `tests/test_accounts.py` | Reads account IDs from the demo overview. Read-only. |
| Open checking/savings | `tests/test_accounts.py` | Creates a fresh customer and opens both account types using a parameterized test. Stateful. |
| Transfer | `tests/test_transfer.py` | Opens a savings account, transfers a small amount, and checks both balances. Stateful. |
| Bill payment | `tests/test_bill_payment.py` | Pays a generated payee and checks the completion message. Does not assume the public app's displayed balance changes immediately. Stateful. |
| Transaction search | `tests/test_transactions.py` | Searches an account by amount and checks that the results table appears. Stateful setup. |
| Loan request | `tests/test_loan.py` | Submits a loan request and checks for an Approved or Denied result. Stateful setup. |
| REST API | `tests/test_api.py` | Checks API login, customer accounts, account detail, and transaction response shape. No browser. |
| AI helper contracts | `tests/test_ai_assistant.py` | Offline unit tests for redaction, JSON validation, local/cloud request behavior, and CLI output. Does not call an AI model. |

### How a UI test runs

1. Pytest discovers `test_*.py` files under `tests/`; markers and `-k` filter which tests execute.
2. The Playwright pytest plugin provides a browser, context, and `Page`. `configure_page` sets timeouts.
3. Fixtures requested in the test signature prepare prerequisites. `demo_login` is for read-only checks; `registered_customer` submits a new-customer form for stateful tests.
4. The test creates a Page Object with the `Page` and configured base URL.
5. Page Object methods navigate, find controls, fill forms, click, and wait for results. The test asserts visible outcomes or data.
6. Pytest closes the browser. `pytest.ini` configures traces, screenshots, and video retention on failure.

### Python and Playwright concepts

- **Functions/type hints:** each test function describes a scenario; annotations document expected values such as `Page` and `Decimal`.
- **Classes and Page Object Model:** page classes group screen-specific selectors and actions, keeping test intent separate from UI details.
- **Inheritance:** page objects reuse `BasePage` navigation behavior.
- **Fixtures:** pytest injects setup based on test function parameters and runs setup before the test body.
- **Locators and actions:** `locator`, `fill`, `click`, and `select_option` target and interact with web elements.
- **Web-first assertions:** Playwright `expect` waits for the desired state instead of checking too early.
- **Parameterized tests:** one account test runs for CHECKING and SAVINGS.
- **JSON/configuration:** test inputs are separate from code; URL and timeout values are configurable.
- **API testing:** `requests.Session` tests REST endpoints without launching a browser.
- **Money:** `Decimal` avoids binary floating-point errors in balance comparisons.

Recommended code-reading path: `tests/test_login.py` → the `demo_login` fixture in `conftest.py` → `pages/login_page.py`; next follow `tests/test_accounts.py` into the dashboard/account Page Objects, then `tests/test_api.py` into `utils/api_client.py`.

## Optional AI tools: local or cloud

The optional `ai_assistant` package can explain pytest failures, draft test cases, and suggest Playwright locators. It never edits source files, executes generated tests, or changes locators automatically. Normal pytest runs do not require Ollama or an AI account.

**For a computer with limited RAM/CPU, use Ollama Cloud for test-case generation.** This mode does not install a local model and does not require Ollama. It requires an Ollama account, a direct API key, internet access, and an available cloud model. Check the account's usage/pricing and model availability first. The feature description and prompt are sent to Ollama Cloud; don't include secrets or private information. See [Ollama Cloud docs](https://docs.ollama.com/cloud) and [API key docs](https://docs.ollama.com/api/authentication).

In a Windows PowerShell terminal, create an API key in Ollama settings and enter it without echoing it. Set the model name to one listed for direct API use in your account:

```powershell
$secureKey = Read-Host "Ollama API key" -AsSecureString
$env:OLLAMA_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
$env:OLLAMA_CLOUD_MODEL = "gemma4:31b" # Replace if this model is not available to your account
.\.venv\Scripts\python.exe -m ai_assistant generate-tests --cloud --feature "A customer can transfer funds between their own accounts"
```

The key exists only in that terminal's environment and is cleared when the terminal closes. Do not place it in source control, screenshots, or a plain `.env` file. Ollama's direct Cloud API is fixed to `https://ollama.com/api/chat`, uses bearer authentication, and accepts the cloud model name configured above. Ollama Cloud does not currently support JSON-schema structured output; the helper prompts for JSON and validates the returned fields. AI drafts can be wrong and must be reviewed.

The `--cloud` flag is only available for `generate-tests`. Failure explanations and locator/DOM suggestions stay **local-only**. If you uninstall Ollama, cloud test generation and regular tests continue to work, but those two local AI features will not work until you reinstall and run a local model.

For local AI use, install [Ollama for Windows](https://ollama.com/download/windows), then pull a model, for example `ollama pull qwen2.5-coder:3b`. The default local endpoint is `http://127.0.0.1:11434`. Local mode is the default for generation and is required for failure explanations and locator suggestions:

```powershell
# Draft test cases locally instead of in the cloud
.\.venv\Scripts\python.exe -m ai_assistant generate-tests --feature "A customer can transfer funds"

# Save a JUnit report, then ask the local model to explain failures
New-Item -ItemType Directory -Force reports
.\.venv\Scripts\python.exe -m pytest -m "ui and not stateful" --junitxml=reports/ui-results.xml
.\.venv\Scripts\python.exe -m ai_assistant explain --junit reports/ui-results.xml

# Suggest locators from local failure text and a saved DOM snapshot
.\.venv\Scripts\python.exe -m ai_assistant suggest-locator --failure-file reports/locator-error.txt --dom-file reports/dom-snapshot.html
```

The helpers apply best-effort redaction to credentials, email, phone, SSN, and HTML input values. This is not guaranteed complete; use only data you are allowed to process, keep locator snapshots focused, and inspect saved inputs/outputs.

## Configuration

Settings are read from environment variables (and an optional local `.env` file):

| Variable | Default | Purpose |
|---|---|---|
| `PARABANK_BASE_URL` | `https://parabank.parasoft.com/parabank` | Application context URL |
| `PARABANK_DEMO_USERNAME` | `john` | Read-only demo login |
| `PARABANK_DEMO_PASSWORD` | `demo` | Read-only demo login |
| `PARABANK_TIMEOUT_MS` | `15000` | Playwright action timeout |
| `PARABANK_API_TIMEOUT_SECONDS` | `15` | REST request timeout |

State-changing UI tests register unique customers through the website. ParaBank does not provide a public customer-deletion endpoint, so these demo records remain on the shared server.

## CI

GitHub Actions runs UI tests against Chromium, Firefox, and WebKit sequentially to avoid overloading the public demo server. API tests run once separately. Reports and failure artifacts are uploaded to each workflow run. CI does not use Ollama, cloud model credentials, or AI-generated tests.

## Project website

The `docs/` directory contains a static learning site describing the project, its architecture, and how to run the tests. It is deployed to GitHub Pages by `.github/workflows/pages.yml` whenever changes are pushed to `main`.

To enable hosting:

1. Push the project to GitHub and open **Settings -> Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push a change to `main`, or manually run the **Deploy project website** workflow from the **Actions** tab.

After the first successful deployment, the site is available at `https://ajayya07.github.io/parabank/`. When using a fork, replace `ajayya07` with your GitHub username and `parabank` with the repository name. GitHub Pages hosts the project guide only; the tests themselves run on your computer or in GitHub Actions against the configured ParaBank application.

## Install on your computer

`requirements.txt` lists the Python packages needed to run this project. With Python 3.10 or newer installed, clone the repository and run these commands from its root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
Copy-Item .env.example .env
python -m pytest
```

On macOS/Linux, activate the virtual environment with `source .venv/bin/activate`; the remaining commands are the same. `python -m playwright install` downloads the browser binaries. To install only the browser you need, use `python -m playwright install chromium` (or `firefox` or `webkit`). See the [project website](docs/index.html) for a guided overview and additional test commands.
