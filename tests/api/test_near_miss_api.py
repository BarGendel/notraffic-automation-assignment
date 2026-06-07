import pytest

from notraffic.api.near_miss_api import NearMissApi
from notraffic.support.near_miss import LEG_KEYS, assert_near_miss_payload

pytestmark = pytest.mark.api


def test_near_miss_endpoint_returns_200(api_request_context) -> None:
    response = NearMissApi(api_request_context).get_by_signal("3")

    assert response.status == 200


def test_near_miss_response_schema_is_valid(api_request_context) -> None:
    payload = NearMissApi(api_request_context).get_json_by_signal("3")

    assert_near_miss_payload(payload)


def test_near_miss_payload_contains_data(api_request_context) -> None:
    payload = NearMissApi(api_request_context).get_json_by_signal("3")

    assert any(payload[leg]["allRoadUsers"] > 0 for leg in LEG_KEYS)


def test_near_miss_allRoadUsers_equals_sum_of_subcategories(api_request_context) -> None:
    payload = NearMissApi(api_request_context).get_json_by_signal("3")

    for leg in LEG_KEYS:
        row = payload[leg]
        expected = row["onlyVehicles"] + row["bicycleInvolved"] + row["pedestrianInvolved"]
        assert row["allRoadUsers"] == expected, f"{leg}: {row['allRoadUsers']} != {expected}"


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-005: signalId is ignored — any ID returns Signal 3 data with HTTP 200.")
def test_near_miss_endpoint_rejects_unknown_signal_id(api_request_context) -> None:
    response = NearMissApi(api_request_context).get_by_signal("999")

    assert response.status in {400, 404}


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-002: GET /api/signals/ returns 500 — app falls back to 2 hardcoded signals, Signal 3 never appears.")
def test_signals_list_api_returns_all_signals(api_request_context) -> None:
    response = api_request_context.get("/api/signals/")

    assert response.status == 200
    signal_ids = [s["id"] for s in response.json()]
    assert 3 in signal_ids, f"Signal 3 missing — got: {signal_ids}"


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-002: GET /api/signals/{id} returns 500 — UI falls back to hardcoded 'Main & 5th' for every signal.")
def test_signal_detail_api_returns_correct_signal(api_request_context) -> None:
    response = api_request_context.get("/api/signals/3/")

    assert response.status == 200
    assert response.json().get("id") == 3


@pytest.mark.known_issue
@pytest.mark.skip(reason="BUG-002: GET /api/alerts/ returns 500 — Recent Alerts falls back to hardcoded data.")
def test_alerts_api_returns_200(api_request_context) -> None:
    response = api_request_context.get("/api/alerts/")

    assert response.status == 200
