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
pages/                  Page objects for login, registration, accounts, transfers, bill pay, transactions, and loans
tests/                  UI and REST API tests
test_data/              Data-driven test inputs
utils/                  Environment configuration, REST client, and shared helpers
.github/workflows/      Cross-browser CI workflow
conftest.py             Browser, API, and test-customer fixtures
pytest.ini              pytest and browser artifact defaults
requirements.txt        Python dependencies
```

## Setup

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install
Copy-Item .env.example .env
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`. Edit `.env` only when targeting a different ParaBank deployment; do not commit credentials or local environment files.

## Run tests

```powershell
pytest
pytest -m ui
pytest -m api
pytest tests/test_transfer.py --browser chromium
pytest -m ui --browser firefox
pytest --headed --slowmo 300
```

To create a standalone HTML report:

```powershell
pytest -m ui --html=reports/ui-report.html --self-contained-html
```

`pytest.ini` is the pytest-playwright configuration entry point; the Python Playwright pytest plugin does not consume the Node.js `playwright.config.py` format.

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

GitHub Actions runs UI tests against Chromium, Firefox, and WebKit sequentially to avoid overloading the public demo server. Read-only API checks run separately. Each UI run uploads an HTML report plus screenshots, video, and traces for failures.

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
