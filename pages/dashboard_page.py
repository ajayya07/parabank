from decimal import Decimal

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.helpers import parse_money


class DashboardPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.account_rows: Locator = page.locator("#accountTable tbody tr")
        self.account_links: Locator = page.locator(
            "#accountTable tbody tr td:first-child a"
        )

    def load(self) -> None:
        self.go_to("overview.htm")
        expect(self.account_links.first).to_be_visible()

    def account_ids(self) -> list[str]:
        return self.account_links.all_text_contents()

    def balance_for(self, account_id: str) -> Decimal:
        account_link = self.page.locator(f'a:text-is("{account_id}")')
        row = self.account_rows.filter(has=account_link)
        return parse_money(row.locator("td").nth(1).inner_text())
