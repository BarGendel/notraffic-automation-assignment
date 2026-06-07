# QA Automation Summary

Scope: page `http://localhost:3000/signals/3`, API `http://localhost:3000/data/near-miss.json?signalId=3`, login.
13 active tests, 10 skipped (one per documented bug).

## 1. Test Scenarios

**API (`tests/api/`)**
- Near-miss endpoint returns 200 for signal 3.
- Payload schema is valid: exact top-level and per-leg keys, integer counts, valid timestamp.
- Payload contains real data (not all zeros).
- Business invariant holds: `allRoadUsers = onlyVehicles + bicycleInvolved + pedestrianInvolved`.

**Login (`tests/ui/test_login.py`)**
- Valid credentials log in and redirect to the dashboard (positive).
- Invalid credentials show an error and do not log in (negative).

**Signal detail `/signals/3` (`tests/ui/test_signal_detail.py`)**
- Page renders name, status/phase line, intersection image, config table, save button.
- Search Results table values and date range match the API payload (UI matches API).
- Search Results and Compare-to tables line up by the same legs and columns.
- CSV export headers, rows, and date range match the displayed tables.
- CSV filename is `near-miss-tables-{signalId}-{YYYY-MM-DD}.csv`.
- PDF export downloads a non-empty file with a valid `%PDF` header.
- Cycle (seconds) input enforces range 30–300 (edge).

## 2. Bugs Discovered

Each bug has a skipped `@known_issue` test that documents it.

- **BUG-001 (Critical, security):** Login error message leaks valid credentials ("Try qa@test.com / test1234").
- **BUG-002 (Critical):** All `/api/` endpoints (`/api/signals/`, `/api/signals/{id}`, `/api/alerts/`) return 500; app falls back to hardcoded data. Root cause of BUG-003 and BUG-004.
- **BUG-003 (Critical):** Every signal detail page shows the same hardcoded "Main & 5th / online / green" regardless of the ID in the URL. Opening `/signals/3` should show "Elm & 7th", but it shows "Main & 5th" — identical to `/signals/1` and `/signals/2`.
- **BUG-004 (Critical):** Signal 3 (Elm & 7th) is missing from the `/signals` list (only 2 of 3 shown).
- **BUG-005 (Critical, data integrity):** `near-miss.json` ignores `signalId` — any ID (1, 2, 999) returns signal 3's data with HTTP 200, so users see wrong near-miss numbers with no error.
- **BUG-006 (High):** The Back button always navigates to `/signals` instead of the previous page. Open a signal from the dashboard and click Back: you expect to return to `/dashboard`, but you land on `/signals`. The destination is hardcoded and ignores browser history.
- **BUG-007 (High):** Changing the Time range date/time inputs has no effect on the table. The inputs read `14/03/2026 00:00 – 14/03/2026 23:59`, but the Search Results table still shows `14 Mar 06:00 - 15 Mar 23:59`. The data never refetches or re-filters — the search controls are decorative.
- **BUG-008 (High, export):** The exported CSV does not wrap comma-containing fields in quotes (RFC 4180). The "Compare to" date range shown on screen as `24 Feb, 12:00 AM - 24 Feb, 11:59 PM` is written unquoted, so its commas split it across 4 separate columns and the CSV value no longer matches the UI.

## 3. Total Execution Time Estimate

- **Automated suite (pytest, headless): ~18 seconds for all 23 tests.**
- **Manual execution of the same scenarios: ~45 minutes for a single careful pass** — and that pass is error-prone.


## How To Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
pytest
```

