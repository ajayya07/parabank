from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
import requests
from faker import Faker
from playwright.sync_api import Page, expect

from pages.registration_page import RegistrationPage
from utils.api_client import ParaBankApiClient
from utils.config import Settings

fake = Faker()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_environment()


@pytest.fixture
def browser_context_args(browser_context_args: dict, settings: Settings) -> dict:
    return {
        **browser_context_args,
        "locale": "en-US",
        "viewport": {"width": 1440, "height": 1000},
    }


@pytest.fixture(autouse=True)
def configure_page(request: pytest.FixtureRequest, settings: Settings) -> None:
    if request.node.get_closest_marker("ui"):
        page: Page = request.getfixturevalue("page")
        page.set_default_timeout(settings.timeout_ms)
        page.set_default_navigation_timeout(max(settings.timeout_ms, 30_000))


@pytest.fixture
def api_client(settings: Settings) -> Iterator[ParaBankApiClient]:
    client = ParaBankApiClient(
        api_base_url=settings.api_base_url,
        timeout_seconds=settings.api_timeout_seconds,
    )
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def random_customer() -> dict[str, str]:
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.postcode(),
        "phone": fake.numerify("##########"),
        "ssn": fake.numerify("###-##-####"),
        "username": f"pw_{uuid4().hex}",
        "password": f"Pw{uuid4().hex[:14]}!",
    }


@pytest.fixture
def registered_customer(
    page: Page, settings: Settings, random_customer: dict[str, str]
) -> dict[str, str]:
    registration = RegistrationPage(page, settings.base_url)
    registration.load()
    registration.register(random_customer)
    expect(registration.success_message).to_be_visible(timeout=settings.timeout_ms)
    return random_customer


@pytest.fixture
def demo_login(page: Page, settings: Settings) -> Page:
    from pages.login_page import LoginPage

    login = LoginPage(page, settings.base_url)
    login.load()
    login.login(settings.demo_username, settings.demo_password)
    expect(page.locator("#leftPanel")).to_be_visible()
    return page
