"""
Shared Appium session — one app launch and one login per test class.

Between test methods, ``tearDown`` returns to MODULES home via hamburger
→ Dashboard without quitting the driver.
"""

from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

import allure
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options

from pages.common.appium_wait import is_fatal_driver_error
from pages.login.home_page import HomePage
from pages.login.login_page import LoginPage

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EMPLOYEE_ID = "500000011"
PASSWORD = "222222"
IP_ADDRESS = "10.10.10.140"
# EMPLOYEE_ID = "500000016"
# PASSWORD = "222222"
# IP_ADDRESS = "10.40.236.3"

class SharedAppiumTestCase(unittest.TestCase):
    driver: webdriver.Remote
    login: LoginPage
    home: HomePage

    _session_logged_in: bool = False
    post_login_path: str | None = None

    @classmethod
    def _safe_quit_driver(cls) -> None:
        if getattr(cls, "driver", None) is not None:
            try:
                cls.driver.quit()
            except Exception:
                pass
            cls.driver = None

    @classmethod
    def _start_driver(cls) -> None:
        caps_path = PROJECT_ROOT / "ezpawnpal.json"
        with caps_path.open(encoding="utf-8") as f:
            caps = json.load(f)

        options = UiAutomator2Options()
        for key, value in caps.items():
            options.set_capability(key, value)

        server_url = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
        cls.driver = webdriver.Remote(server_url, options=options)
        cls.login = LoginPage(cls.driver)
        cls.home = HomePage(cls.driver)

    @classmethod
    def _login_with_credentials(cls, employee_id: str, password: str, ip_address: str) -> None:
        if cls._session_logged_in:
            return
        last_error: BaseException | None = None
        for attempt in range(2):
            try:
                cls.post_login_path = cls.login.complete_login_flow(
                    employee_id, password, ip_address, home=cls.home,
                )
                cls._session_logged_in = True
                return
            except Exception as exc:
                last_error = exc
                if attempt == 0 and is_fatal_driver_error(exc):
                    cls._safe_quit_driver()
                    cls._start_driver()
                    continue
                raise
        if last_error:
            raise last_error

    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(EMPLOYEE_ID, PASSWORD, IP_ADDRESS)

    @classmethod
    def setUpClass(cls) -> None:
        cls._session_logged_in = False
        cls.post_login_path = None
        cls._start_driver()
        cls._login_once()

    def setUp(self) -> None:
        # Data Sync may appear after login while earlier tests are still running.
        self.home.wait_for_home_ready()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._safe_quit_driver()
        cls._session_logged_in = False

    def tearDown(self) -> None:
        # 1. Take a screenshot if the test failed
        outcome = getattr(self, '_outcome', None)
        if outcome:
            errors = getattr(outcome, 'errors', [])
            for test_name, error in errors:
                if error:
                    try:
                        allure.attach(
                            self.driver.get_screenshot_as_png(),
                            name="Failure_Screen",
                            attachment_type=AttachmentType.PNG
                        )
                    except Exception as e:
                        print(f"Failed to capture screenshot: {e}")
                    break  # One screenshot is enough

        # 2. Safe Dashboard Reset
        # This ensures EVERY test finishes by putting the app exactly 
        # where the next test expects it to be!
        try:
            self.home.navigate_to_dashboard_via_menu()
        except Exception:
            pass
