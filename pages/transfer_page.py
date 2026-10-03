from decimal import Decimal

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class TransferPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.amount: Locator = page.locator("#amount")
        self.from_account: Locator = page.locator("#fromAccountId")
        self.to_account: Locator = page.locator("#toAccountId")
        self.transfer_button: Locator = page.locator('input[value="Transfer"]')
        self.result: Locator = page.locator("#showResult")

    def load(self) -> None:
        self.go_to("transfer.htm")
        expect(self.amount).to_be_visible()

    def transfer(self, amount: Decimal, from_account_id: str, to_account_id: str) -> None:
        self.amount.fill(f"{amount:.2f}")
        self.from_account.select_option(label=from_account_id)
        self.to_account.select_option(label=to_account_id)
        self.transfer_button.click()
        expect(self.result).to_contain_text("Transfer Complete")
