import pytest
from playwright.sync_api import expect

from notraffic.pages.signals_list_page import SignalsListPage

pytestmark = [pytest.mark.ui]


@pytest.fixture()
def signals_list(authenticated_page, settings) -> SignalsListPage:
    return SignalsListPage(authenticated_page, settings)


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-004: Signal 3 (Elm & 7th) is missing from the /signals list page.")
def test_signals_list_shows_all_signals(signals_list) -> None:
    signals_list.open()

    expect(signals_list.signal_link("Elm & 7th")).to_be_visible()
