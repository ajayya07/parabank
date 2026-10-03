from decimal import Decimal

import pytest
from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.transactions_page import TransactionsPage
from utils.config import Settings
from utils.helpers import load_test_data


@pytest.mark.ui
@pytest.mark.stateful
def test_transaction_search_returns_a_results_table(
    page: Page, settings: Settings, registered_customer: dict[str, str]
) -> None:
    dashboard = DashboardPage(page, settings.base_url)
    dashboard.load()
    account_id = dashboard.account_ids()[0]
    amount = Decimal(load_test_data("test_data.json")["transaction_search_amount"])

    transactions = TransactionsPage(page, settings.base_url)
    transactions.load()
    transactions.search_by_amount(account_id, amount)

    assert transactions.results.is_visible()
