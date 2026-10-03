from decimal import Decimal

import pytest
from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.loan_page import LoanPage
from utils.config import Settings
from utils.helpers import load_test_data


@pytest.mark.ui
@pytest.mark.stateful
def test_customer_can_submit_a_loan_request(
    page: Page, settings: Settings, registered_customer: dict[str, str]
) -> None:
    dashboard = DashboardPage(page, settings.base_url)
    dashboard.load()
    account_id = dashboard.account_ids()[0]
    loan_data = load_test_data("test_data.json")

    loan = LoanPage(page, settings.base_url)
    loan.load()
    status = loan.request_loan(
        amount=Decimal(loan_data["loan_amount"]),
        down_payment=Decimal(loan_data["loan_down_payment"]),
        from_account_id=account_id,
    )

    assert status in {"Approved", "Denied"}
