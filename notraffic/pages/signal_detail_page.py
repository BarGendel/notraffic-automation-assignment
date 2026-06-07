from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from notraffic.core.settings import Settings


class SignalDetailPage:
    def __init__(self, page: Page, settings: Settings):
        self.page = page
        self.settings = settings
        self.root = page.get_by_test_id("signal-detail-page")
        self.name = page.get_by_test_id("signal-name")
        self.status = page.get_by_test_id("signal-status")
        self.intersection_image = page.get_by_alt_text("Traffic intersection in the United States")
        self.traffic_light_config = page.locator(".traffic-light-config-section")
        self.save_traffic_light_button = page.get_by_role("button", name="Save traffic light configuration")
        self.save_config_button = page.get_by_test_id("signal-save")
        self.cycle_input = page.get_by_test_id("signal-cycle-input")
        self.csv_button = page.get_by_test_id("download-csv")
        self.pdf_button = page.get_by_test_id("download-pdf")
        self.back_button = page.locator("button.back")
        self.search_results_section = page.get_by_test_id("near-miss-table")
        self.compare_section = page.get_by_test_id("search-results")

    def open(self, signal_id: str) -> "SignalDetailPage":
        self.page.goto(self.settings.url(f"/signals/{signal_id}"))
        self.expect_loaded()
        return self

    def expect_loaded(self) -> None:
        expect(self.root).to_be_visible(timeout=15_000)
        expect(self.search_results_section).to_be_visible(timeout=15_000)

    def search_results_rows(self) -> dict[str, list[str]]:
        return self._read_near_miss_rows(self.search_results_section)

    def compare_rows(self) -> dict[str, list[str]]:
        return self._read_near_miss_rows(self.compare_section)

    def search_results_date_range(self) -> str:
        return self.search_results_section.locator(".near-miss-date-range").inner_text().strip()

    def compare_date_range(self) -> str:
        return self.compare_section.locator(".near-miss-date-range").inner_text().strip()

    def search_params_time_range(self) -> dict[str, str]:
        # First half-block in the panel is the "Time range" group (second is "Compare to").
        block = self.page.locator(".search-params-panel .search-params-block-half").first
        dates = block.locator("input.search-params-date-only")
        times = block.locator("input.search-params-time-only")
        return {
            "from_date": dates.nth(0).input_value(),
            "from_time": times.nth(0).input_value(),
            "to_date": dates.nth(1).input_value(),
            "to_time": times.nth(1).input_value(),
        }

    def download_pdf_bytes(self) -> bytes:
        return self._download(self.pdf_button).read_bytes()

    def download_csv_text(self) -> str:
        return self._download(self.csv_button).read_text(encoding="utf-8")

    def csv_download_filename(self) -> str:
        with self.page.expect_download() as download_info:
            self.csv_button.click()
        return download_info.value.suggested_filename

    def _download(self, trigger: Locator) -> Path:
        with self.page.expect_download() as download_info:
            trigger.click()
        path = download_info.value.path()
        assert path is not None
        return Path(path)

    @staticmethod
    def _read_near_miss_rows(section: Locator) -> dict[str, list[str]]:
        rows: dict[str, list[str]] = {}
        table_rows = section.locator("tbody tr")
        for index in range(table_rows.count()):
            row = table_rows.nth(index)
            leg = row.locator("th").inner_text().strip()
            values = [value.strip() for value in row.locator("td .near-miss-cell-inner").all_inner_texts()]
            rows[leg] = values
        return rows
