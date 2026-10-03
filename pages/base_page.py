from playwright.sync_api import Locator, Page


class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def go_to(self, path: str) -> None:
        self.page.goto(f"{self.base_url}/{path.lstrip('/')}")

    def menu_link(self, name: str) -> Locator:
        return self.page.locator("#leftPanel").get_by_role("link", name=name)

    def navigate_from_menu(self, name: str) -> None:
        self.menu_link(name).click()
