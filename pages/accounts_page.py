from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class OpenAccountPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.account_type: Locator = page.locator("#type")
        self.funding_account: Locator = page.locator("#fromAccountId")
        self.open_button: Locator = page.locator('input[value="Open New Account"]')
        self.result: Locator = page.locator("#openAccountResult")
        self.new_account_id: Locator = page.locator("#newAccountId")

    def load(self) -> None:
        self.go_to("openaccount.htm")
        expect(self.account_type).to_be_visible()

    def open_account(self, account_type: str, funding_account_id: str | None = None) -> str:
        self.account_type.select_option(label=account_type)
        if funding_account_id is not None:
            self.funding_account.select_option(label=funding_account_id)
        self.open_button.click()
        expect(self.new_account_id).to_be_visible()
        return self.new_account_id.inner_text().strip()
