import re

from playwright.sync_api import Locator, Page, expect

from notraffic.core.settings import Settings


class DashboardPage:
    PATH = "/dashboard"

    def __init__(self, page: Page, settings: Settings):
        self.page = page
        self.settings = settings
        self.traffic_signals_heading = page.get_by_role("heading", name=re.compile("Traffic signals", re.IGNORECASE))

    def open(self) -> "DashboardPage":
        self.page.goto(self.settings.url(self.PATH))
        self.expect_loaded()
        return self

    def expect_loaded(self) -> None:
        expect(self.traffic_signals_heading).to_be_visible(timeout=15_000)

    def signal_items(self) -> Locator:
        return self.page.locator("[data-testid^='signal-link-']")
