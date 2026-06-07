import json
import os
import urllib.error
import urllib.request
from typing import Iterator

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from notraffic.core.settings import Settings
from notraffic.support.auth import apply_session, capture_session
from notraffic.support.near_miss import assert_near_miss_payload


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session", autouse=True)
def app_is_available(settings: Settings) -> Iterator[None]:
    if _is_assignment_app_available(settings.base_url):
        yield
        return

    pytest.skip(
        "Traffic Management Platform is not reachable or does not expose the expected "
        f"near-miss payload at {settings.base_url}. Start the target app separately, "
        "or run with BASE_URL=http://host:port pytest."
    )


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Iterator[Browser]:
    headless = os.getenv("HEADLESS", "true").lower() != "false"
    slow_mo = int(os.getenv("SLOW_MO_MS", "0"))
    browser = playwright_instance.chromium.launch(headless=headless, slow_mo=slow_mo)
    yield browser
    browser.close()


@pytest.fixture()
def page(browser: Browser, settings: Settings) -> Iterator[Page]:
    context = browser.new_context(base_url=settings.base_url, accept_downloads=True)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def authenticated_page(page: Page, auth_session: dict[str, str]) -> Page:
    # Seed the captured session before any navigation so the page starts logged in.
    apply_session(page, auth_session)
    return page


@pytest.fixture(scope="session")
def api_request_context(playwright_instance: Playwright, settings: Settings):
    request_context = playwright_instance.request.new_context(base_url=settings.base_url)
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def auth_session(browser: Browser, settings: Settings) -> dict[str, str]:
    context = browser.new_context(base_url=settings.base_url)
    page = context.new_page()
    try:
        return capture_session(page, settings)
    finally:
        context.close()


def _is_assignment_app_available(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url}/data/near-miss.json?signalId=3", timeout=2) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
            assert_near_miss_payload(payload)
            return True
    except (AssertionError, json.JSONDecodeError, urllib.error.URLError, TimeoutError):
        return False
