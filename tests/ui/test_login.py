import re

import pytest
from playwright.sync_api import expect

from notraffic.pages.login_page import LoginPage

pytestmark = [pytest.mark.ui]


@pytest.fixture()
def login_page(page, settings) -> LoginPage:
    return LoginPage(page, settings)


def test_valid_login_redirects_to_dashboard(login_page) -> None:
    login_page.open()
    login_page.login()

    expect(login_page.page).to_have_url(re.compile(r".*/dashboard$"))


def test_invalid_login_shows_error(login_page) -> None:
    login_page.open()
    login_page.login(username="wrong@test.com", password="wrongpassword")

    expect(login_page.error_alert).to_be_visible()


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-001: Login error message exposes valid credentials — 'Try qa@test.com / test1234'.")
def test_login_error_does_not_expose_credentials(login_page, settings) -> None:
    login_page.open()
    login_page.login(username="wrong@test.com", password="wrongpassword")

    error_text = login_page.error_alert.inner_text()
    assert settings.username not in error_text, f"Error exposes email: {error_text!r}"
    assert settings.password not in error_text, f"Error exposes password: {error_text!r}"
