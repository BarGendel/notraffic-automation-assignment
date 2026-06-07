# NoTraffic Automation Assignment

Python + pytest + Playwright tests for page `http://localhost:3000/signals/3`, API `http://localhost:3000/data/near-miss.json?signalId=3`, and login (`qa@test.com` / `test1234`).

## Structure

```text
notraffic/   API helpers, settings, page objects, shared assertions
tests/       api/ and ui/ tests
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Run

Start the app separately, then:

```bash
pytest                                   # headless, against http://localhost:3000
BASE_URL=http://host:port pytest         # another environment
HEADLESS=false SLOW_MO_MS=500 pytest     # watch the browser
```

### Test report

```bash
pytest --html=report.html --self-contained-html   # writes a shareable report.html
```

Runs 13 active tests + 10 skipped `@known_issue` tests (one per bug). If the app is unreachable, active tests are skipped, not failed.

Scenarios, bugs, and execution-time estimate: `QA_AUTOMATION_SUMMARY.md`.
