import json

from playwright.sync_api import Page

from notraffic.core.settings import Settings
from notraffic.pages.login_page import LoginPage

# The app keeps auth in sessionStorage under these keys after a successful login.
SESSION_KEYS = ("traffic_auth_token", "traffic_auth_user")


def capture_session(page: Page, settings: Settings) -> dict[str, str]:
    """Log in through the UI once and return the values the app stores in sessionStorage."""
    login = LoginPage(page, settings)
    login.open()
    login.login()
    page.wait_for_url("**/dashboard")
    return page.evaluate(
        "(keys) => Object.fromEntries(keys.map(k => [k, sessionStorage.getItem(k)]))",
        list(SESSION_KEYS),
    )


def apply_session(page: Page, session: dict[str, str]) -> None:
    """Pre-authenticate a page by seeding the captured sessionStorage before any navigation."""
    page.add_init_script(
        f"""
        (() => {{
            const session = {json.dumps(session)};
            for (const [key, value] of Object.entries(session)) {{
                if (value !== null) sessionStorage.setItem(key, value);
            }}
        }})();
        """
    )
