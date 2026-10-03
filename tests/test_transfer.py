from decimal import Decimal

import pytest
from playwright.sync_api import Page

from pages.accounts_page import OpenAccountPage
from pages.dashboard_page import DashboardPage
from pages.transfer_page import TransferPage
from utils.config import Settings
from utils.helpers import load_test_data


@pytest.mark.ui
@pytest.mark.stateful
def test_transfer_updates_both_account_balances(
    page: Page, settings: Settings, registered_customer: dict[str, str]
) -> None:
    dashboard = DashboardPage(page, settings.base_url)
    dashboard.load()
    source_account_id = dashboard.account_ids()[0]
    open_account = OpenAccountPage(page, settings.base_url)
    open_account.load()
    target_account_id = open_account.open_account("SAVINGS", source_account_id)

    dashboard.load()
    source_before = dashboard.balance_for(source_account_id)
    target_before = dashboard.balance_for(target_account_id)
    amount = Decimal(load_test_data("test_data.json")["transfer_amount"])

    transfer = TransferPage(page, settings.base_url)
    transfer.load()
    transfer.transfer(amount, source_account_id, target_account_id)

    dashboard.load()
    assert dashboard.balance_for(source_account_id) == source_before - amount
    assert dashboard.balance_for(target_account_id) == target_before + amount
