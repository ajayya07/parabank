from decimal import Decimal

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class BillPaymentPage(BasePage):
    PAYEE_FIELDS = {
        "name": "payee.name",
        "street": "payee.address.street",
        "city": "payee.address.city",
        "state": "payee.address.state",
        "zip_code": "payee.address.zipCode",
        "phone": "payee.phoneNumber",
        "account_number": "payee.accountNumber",
    }

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.amount: Locator = page.locator('input[name="amount"]')
        self.from_account: Locator = page.locator('select[name="fromAccountId"]')
        self.send_button: Locator = page.locator('input[value="Send Payment"]')
        self.result: Locator = page.get_by_text("Bill Payment Complete")

    def load(self) -> None:
        self.go_to("billpay.htm")
        expect(self.amount).to_be_visible()

    def pay_bill(
        self, payee: dict[str, str], amount: Decimal, from_account_id: str
    ) -> None:
        for key, field_name in self.PAYEE_FIELDS.items():
            self.page.locator(f'input[name="{field_name}"]').fill(payee[key])
        self.page.locator('input[name="verifyAccount"]').fill(payee["account_number"])
        self.amount.fill(f"{amount:.2f}")
        self.from_account.select_option(label=from_account_id)
        self.send_button.click()
        expect(self.result).to_be_visible()
