from decimal import Decimal
from uuid import uuid4

import pytest
from faker import Faker
from playwright.sync_api import Page

from pages.bill_payment_page import BillPaymentPage
from pages.dashboard_page import DashboardPage
from utils.config import Settings
from utils.helpers import load_test_data

fake = Faker()


@pytest.mark.ui
@pytest.mark.stateful
def test_customer_can_pay_a_bill(
    page: Page, settings: Settings, registered_customer: dict[str, str]
) -> None:
    dashboard = DashboardPage(page, settings.base_url)
    dashboard.load()
    account_id = dashboard.account_ids()[0]
    balance_before = dashboard.balance_for(account_id)
    payee = {
        "name": f"Test Payee {uuid4().hex[:8]}",
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.postcode(),
        "phone": fake.numerify("##########"),
        "account_number": f"{uuid4().int % 10**8:08d}",
    }
    amount = Decimal(load_test_data("test_data.json")["bill_payment_amount"])

    bill_payment = BillPaymentPage(page, settings.base_url)
    bill_payment.load()
    bill_payment.pay_bill(payee, amount, account_id)

    assert bill_payment.result.is_visible()
    dashboard.load()
    assert dashboard.balance_for(account_id) == balance_before - amount
