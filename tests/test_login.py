import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.config import Settings
from utils.helpers import load_test_data


@pytest.mark.ui
@pytest.mark.smoke
def test_demo_customer_can_log_in(demo_login: Page) -> None:
    expect(demo_login.locator("#accountTable")).to_be_visible()


@pytest.mark.ui
def test_invalid_credentials_show_an_error(page: Page, settings: Settings) -> None:
    credentials = load_test_data("test_data.json")["invalid_login"]
    login = LoginPage(page, settings.base_url)
    login.load()
    login.login(credentials["username"], credentials["password"])
    expect(login.login_error).to_be_visible()


@pytest.mark.ui
@pytest.mark.stateful
def test_new_customer_can_register(registered_customer: dict[str, str]) -> None:
    assert registered_customer["username"].startswith("pw_")
