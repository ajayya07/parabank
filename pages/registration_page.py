from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class RegistrationPage(BasePage):
    FIELD_NAMES = {
        "first_name": "customer.firstName",
        "last_name": "customer.lastName",
        "street": "customer.address.street",
        "city": "customer.address.city",
        "state": "customer.address.state",
        "zip_code": "customer.address.zipCode",
        "phone": "customer.phoneNumber",
        "ssn": "customer.ssn",
        "username": "customer.username",
        "password": "customer.password",
    }

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.success_message: Locator = page.get_by_text(
            "Your account was created successfully"
        )

    def load(self) -> None:
        self.go_to("register.htm")

    def register(self, customer: dict[str, str]) -> None:
        for key, field_name in self.FIELD_NAMES.items():
            self.page.locator(f'input[name="{field_name}"]').fill(customer[key])
        self.page.locator('input[name="repeatedPassword"]').fill(customer["password"])
        self.page.locator('input[value="Register"]').click()
