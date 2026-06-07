import re

from playwright.sync_api import Locator, Page

from notraffic.core.settings import Settings


class SignalsListPage:
    PATH = "/signals"

    def __init__(self, page: Page, settings: Settings):
        self.page = page
        self.settings = settings

    def open(self) -> "SignalsListPage":
        self.page.goto(self.settings.url(self.PATH))
        return self

    def signal_link(self, name: str) -> Locator:
        return self.page.get_by_role("link", name=re.compile(name, re.IGNORECASE))
