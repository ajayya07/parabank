from decimal import Decimal

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class TransactionsPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.account: Locator = page.locator("#accountId")
        self.amount: Locator = page.locator("#amount")
        self.find_by_amount_button: Locator = page.locator("#findByAmount")
        self.results: Locator = page.locator("#transactionTable")
        self.result_rows: Locator = page.locator("#transactionTable tbody tr td a")

    def load(self) -> None:
        self.go_to("findtrans.htm")
        expect(self.account).to_be_visible()

    def search_by_amount(self, account_id: str, amount: Decimal) -> None:
        self.account.select_option(value=account_id)
        self.amount.fill(f"{amount:.2f}")
        self.find_by_amount_button.click()
        expect(self.results).to_be_visible()
