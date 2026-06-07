from playwright.sync_api import Page

from notraffic.core.settings import Settings


class LoginPage:
    def __init__(self, page: Page, settings: Settings):
        self.page = page
        self.settings = settings
        self.email_input = page.get_by_test_id("login-email")
        self.password_input = page.get_by_test_id("login-password")
        self.submit_button = page.get_by_test_id("login-submit")
        self.error_alert = page.get_by_role("alert")

    def open(self) -> None:
        self.page.goto(self.settings.url("/login"), wait_until="domcontentloaded")

    def login(self, username: str | None = None, password: str | None = None) -> None:
        self.email_input.fill(username or self.settings.username)
        self.password_input.fill(password or self.settings.password)
        self.submit_button.click()

