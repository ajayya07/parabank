import pytest
from playwright.sync_api import Page, expect

from pages.accounts_page import OpenAccountPage
from pages.dashboard_page import DashboardPage
from utils.config import Settings
from utils.helpers import load_test_data


@pytest.mark.ui
@pytest.mark.smoke
def test_dashboard_lists_demo_customer_accounts(demo_login: Page, settings: Settings) -> None:
    dashboard = DashboardPage(demo_login, settings.base_url)
    dashboard.load()
    assert dashboard.account_ids()


@pytest.mark.ui
@pytest.mark.stateful
@pytest.mark.parametrize(
    "account_type", load_test_data("test_data.json")["account_types"]
)
def test_customer_can_open_an_account(
    page: Page, settings: Settings, registered_customer: dict[str, str], account_type: str
) -> None:
    dashboard = DashboardPage(page, settings.base_url)
    dashboard.load()
    existing_account_id = dashboard.account_ids()[0]

    open_account = OpenAccountPage(page, settings.base_url)
    open_account.load()
    new_account_id = open_account.open_account(account_type, existing_account_id)

    assert new_account_id
    dashboard.load()
    assert new_account_id in dashboard.account_ids()
