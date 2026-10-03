from decimal import Decimal

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class LoanPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.amount: Locator = page.locator("#amount")
        self.down_payment: Locator = page.locator("#downPayment")
        self.from_account: Locator = page.locator("#fromAccountId")
        self.apply_button: Locator = page.locator('input[value="Apply Now"]')
        self.status: Locator = page.locator("#loanStatus")

    def load(self) -> None:
        self.go_to("requestloan.htm")
        expect(self.amount).to_be_visible()

    def request_loan(
        self, amount: Decimal, down_payment: Decimal, from_account_id: str
    ) -> str:
        self.amount.fill(f"{amount:.2f}")
        self.down_payment.fill(f"{down_payment:.2f}")
        self.from_account.select_option(label=from_account_id)
        self.apply_button.click()
        expect(self.status).to_be_visible()
        return self.status.inner_text().strip()
