import pytest
import requests

from utils.api_client import ParaBankApiClient
from utils.config import Settings


@pytest.mark.api
@pytest.mark.smoke
def test_api_login_returns_demo_customer(
    api_client: ParaBankApiClient, settings: Settings
) -> None:
    response = api_client.login(settings.demo_username, settings.demo_password)

    assert response.status_code == requests.codes.ok
    customer = response.json()
    assert customer["firstName"] == "John"
    assert isinstance(customer["id"], int)


@pytest.mark.api
def test_api_rejects_invalid_login(api_client: ParaBankApiClient) -> None:
    response = api_client.login("invalid-user", "invalid-password")

    assert response.status_code != requests.codes.ok


@pytest.mark.api
def test_customer_accounts_and_transactions_are_available(
    api_client: ParaBankApiClient, settings: Settings
) -> None:
    login_response = api_client.login(settings.demo_username, settings.demo_password)
    assert login_response.status_code == requests.codes.ok
    customer_id = login_response.json()["id"]

    accounts_response = api_client.customer_accounts(customer_id)
    assert accounts_response.status_code == requests.codes.ok
    accounts = accounts_response.json()
    assert accounts
    account_id = accounts[0]["id"]
    assert accounts[0]["customerId"] == customer_id
    assert "balance" in accounts[0]

    account_response = api_client.get(f"accounts/{account_id}")
    assert account_response.status_code == requests.codes.ok
    assert account_response.json()["id"] == account_id

    transactions_response = api_client.get(
        f"accounts/{account_id}/transactions/amount/0"
    )
    assert transactions_response.status_code == requests.codes.ok
    assert isinstance(transactions_response.json(), list)
