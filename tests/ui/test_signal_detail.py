import datetime
import re

import pytest
from playwright.sync_api import expect

from notraffic.api.near_miss_api import NearMissApi
from notraffic.pages.signal_detail_page import SignalDetailPage
from notraffic.support.near_miss import (
    COLUMN_LABELS,
    assert_near_miss_row_shape,
    expected_ui_rows_from_payload,
    parse_near_miss_csv,
)

pytestmark = [pytest.mark.ui, pytest.mark.e2e]

SIGNAL_ID = "3"


@pytest.fixture()
def signal(authenticated_page, settings) -> SignalDetailPage:
    return SignalDetailPage(authenticated_page, settings)


@pytest.fixture()
def near_miss_api(api_request_context) -> NearMissApi:
    return NearMissApi(api_request_context)


def test_signal_detail_page_renders_required_elements(signal) -> None:
    signal.open(SIGNAL_ID)

    name = signal.name.inner_text().strip()
    status = signal.status.inner_text().strip()

    assert len(name) > 0
    assert re.search(r"Status:\s+(online|offline|maintenance)", status, re.IGNORECASE), f"Unexpected status: {status!r}"
    assert re.search(r"Phase:\s+\w+", status, re.IGNORECASE), f"Unexpected phase: {status!r}"
    expect(signal.intersection_image).to_be_visible()
    expect(signal.traffic_light_config).to_be_visible()
    expect(signal.save_traffic_light_button).to_be_visible()


def test_near_miss_table_matches_api(signal, near_miss_api) -> None:
    signal.open(SIGNAL_ID)
    payload = near_miss_api.get_json_by_signal(SIGNAL_ID)

    assert signal.search_results_rows() == expected_ui_rows_from_payload(payload)
    assert signal.search_results_date_range() == payload["dateTimeRange"]


def test_near_miss_tables_are_comparable_by_leg_and_column(signal) -> None:
    signal.open(SIGNAL_ID)
    search_rows = signal.search_results_rows()
    compare_rows = signal.compare_rows()

    assert_near_miss_row_shape(search_rows)
    assert_near_miss_row_shape(compare_rows)

    matching = {
        leg: [COLUMN_LABELS[i] for i in range(len(COLUMN_LABELS)) if search_rows[leg][i] == compare_rows[leg][i]]
        for leg in search_rows
    }
    assert set(matching) == {"NLeg", "SLeg", "ELeg", "WLeg"}
    for leg, cols in matching.items():
        assert all(col in COLUMN_LABELS for col in cols), f"{leg}: unexpected column: {cols}"


def test_csv_export_matches_displayed_near_miss_tables(signal) -> None:
    signal.open(SIGNAL_ID)
    search_rows = signal.search_results_rows()
    compare_rows = signal.compare_rows()
    date_range = signal.search_results_date_range()

    sections = parse_near_miss_csv(signal.download_csv_text())

    search = sections["Search Results - Near-Miss Events by leg"]
    compare = sections["Compare to - Near-Miss Events by leg"]
    assert search["headers"] == COLUMN_LABELS
    assert compare["headers"] == COLUMN_LABELS
    assert search["date_range"] == date_range
    assert search["rows"] == search_rows
    assert compare["rows"] == compare_rows


def test_csv_filename_includes_signal_id_and_date(signal) -> None:
    signal.open(SIGNAL_ID)
    today = datetime.date.today().isoformat()

    assert signal.csv_download_filename() == f"near-miss-tables-{SIGNAL_ID}-{today}.csv"


def test_pdf_export_downloads_a_valid_pdf(signal) -> None:
    signal.open(SIGNAL_ID)
    pdf_bytes = signal.download_pdf_bytes()

    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF"


def test_cycle_seconds_validates_range(signal) -> None:
    signal.open(SIGNAL_ID)
    cycle = signal.cycle_input
    save = signal.save_config_button

    expect(cycle).to_have_attribute("min", re.compile(r"^30$"))
    expect(cycle).to_have_attribute("max", re.compile(r"^300$"))

    cycle.fill("20")
    save.click()
    assert cycle.evaluate("el => el.validity.rangeUnderflow"), "Expected range underflow for value 20"
    assert "30" in cycle.evaluate("el => el.validationMessage")

    cycle.fill("301")
    save.click()
    assert cycle.evaluate("el => el.validity.rangeOverflow"), "Expected range overflow for value 301"
    assert "300" in cycle.evaluate("el => el.validationMessage")


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-008: CSV does not quote fields containing commas — the 'Compare to' date range ('24 Feb, 12:00 AM - 24 Feb, 11:59 PM') splits across columns, so the CSV value no longer matches the displayed value.")
def test_csv_compare_date_range_matches_ui(signal) -> None:
    signal.open(SIGNAL_ID)
    ui_compare_range = signal.compare_date_range()

    sections = parse_near_miss_csv(signal.download_csv_text())
    compare = sections["Compare to - Near-Miss Events by leg"]

    assert compare["date_range"] == ui_compare_range, (
        f"CSV compare date range {compare['date_range']!r} != UI {ui_compare_range!r}"
    )


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-007: Search parameter Time range inputs do not drive the displayed Search Results range — inputs read 14/03 00:00–23:59 but the table shows '14 Mar 06:00 - 15 Mar 23:59'.")
def test_search_results_range_reflects_search_parameters(signal) -> None:
    signal.open(SIGNAL_ID)
    params = signal.search_params_time_range()
    displayed = signal.search_results_date_range()

    assert params["from_time"] in displayed, f"From time {params['from_time']!r} not reflected in {displayed!r}"
    assert params["to_time"] in displayed, f"To time {params['to_time']!r} not reflected in {displayed!r}"


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-003: All signal detail pages show hardcoded 'Main & 5th / online / green' regardless of signal ID.")
def test_each_signal_page_shows_its_own_data(signal) -> None:
    signal.open("2")
    expect(signal.name).to_have_text("Oak & 3rd")

    signal.open("3")
    expect(signal.name).to_have_text("Elm & 7th")
