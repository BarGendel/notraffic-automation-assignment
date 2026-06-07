import csv
from datetime import datetime
from io import StringIO
from typing import Any

LEG_KEYS = ("nLeg", "sLeg", "eLeg", "wLeg")
LEG_LABELS = {
    "nLeg": "NLeg",
    "sLeg": "SLeg",
    "eLeg": "ELeg",
    "wLeg": "WLeg",
}
COLUMN_KEYS = (
    "allRoadUsers",
    "onlyVehicles",
    "bicycleInvolved",
    "pedestrianInvolved",
)
COLUMN_LABELS = [
    "All road users",
    "Only vehicles",
    "Bicycle involved",
    "Pedestrian involved",
]
REQUIRED_TOP_LEVEL_KEYS = {
    "dateTimeRange",
    "nLeg",
    "sLeg",
    "eLeg",
    "wLeg",
    "updatedAt",
}


def assert_near_miss_payload(payload: dict[str, Any]) -> None:
    assert set(payload) == REQUIRED_TOP_LEVEL_KEYS, (
        f"Unexpected top-level keys: {set(payload) ^ REQUIRED_TOP_LEVEL_KEYS}"
    )

    assert isinstance(payload.get("dateTimeRange"), str)
    assert payload["dateTimeRange"].strip()

    updated_at = payload.get("updatedAt")
    assert isinstance(updated_at, str)
    datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

    for leg in LEG_KEYS:
        assert leg in payload
        row = payload[leg]
        assert isinstance(row, dict)
        assert set(row) == set(COLUMN_KEYS), f"{leg}: unexpected keys {set(row) ^ set(COLUMN_KEYS)}"

        for column in COLUMN_KEYS:
            value = row.get(column)
            assert isinstance(value, int)
            assert value >= 0

        assert row["allRoadUsers"] == (
            row["onlyVehicles"] + row["bicycleInvolved"] + row["pedestrianInvolved"]
        )


def expected_ui_rows_from_payload(payload: dict[str, Any]) -> dict[str, list[str]]:
    return {
        LEG_LABELS[leg]: [str(payload[leg][column]) for column in COLUMN_KEYS]
        for leg in LEG_KEYS
    }


def assert_near_miss_row_shape(rows: dict[str, list[str]]) -> None:
    assert set(rows) == set(LEG_LABELS.values())
    for values in rows.values():
        assert len(values) == len(COLUMN_LABELS)
        assert all(value.isdigit() for value in values)


def parse_near_miss_csv(csv_text: str) -> dict[str, dict[str, Any]]:
    rows = list(csv.reader(StringIO(csv_text)))
    sections: dict[str, dict[str, Any]] = {}
    index = 0

    while index < len(rows):
        row = rows[index]
        if not row:
            index += 1
            continue

        if row[0] != "Section":
            index += 1
            continue

        section_name = row[1]
        date_range = rows[index + 1][1]
        index += 2

        while index < len(rows) and not rows[index]:
            index += 1

        header = rows[index]
        index += 1

        section_rows: dict[str, list[str]] = {}
        while index < len(rows) and rows[index] and rows[index][0] != "Section":
            section_rows[rows[index][0]] = rows[index][1:]
            index += 1

        sections[section_name] = {
            "date_range": date_range,
            "headers": header[1:],
            "rows": section_rows,
        }

    return sections
