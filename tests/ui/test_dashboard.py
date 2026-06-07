import pytest
from playwright.sync_api import expect

from notraffic.pages.dashboard_page import DashboardPage
from notraffic.pages.signal_detail_page import SignalDetailPage

pytestmark = [pytest.mark.ui]


@pytest.fixture()
def dashboard(authenticated_page, settings) -> DashboardPage:
    return DashboardPage(authenticated_page, settings)


@pytest.fixture()
def signal_detail(authenticated_page, settings) -> SignalDetailPage:
    return SignalDetailPage(authenticated_page, settings)


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-006: Back button navigates to /signals instead of /dashboard — hardcoded destination ignores browser history.")
def test_back_from_signal_detail_returns_to_dashboard(dashboard, signal_detail) -> None:
    dashboard.open()
    dashboard_url = dashboard.page.url

    dashboard.signal_items().first.click()
    signal_detail.expect_loaded()
    signal_detail.back_button.click()

    expect(dashboard.page).to_have_url(dashboard_url)
