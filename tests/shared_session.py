"""
Shared Appium session — one app launch and one login per test class.

Between test methods, ``tearDown`` returns to MODULES home via hamburger
→ Dashboard without quitting the driver.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

import allure
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options

from pages.login.home_page import HomePage
from pages.login.login_page import LoginPage

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EMPLOYEE_ID = "500000011"
PASSWORD = "222222"
IP_ADDRESS = "10.10.10.140"


class SharedAppiumTestCase(unittest.TestCase):
    driver: webdriver.Remote
    login: LoginPage
    home: HomePage

    _session_logged_in: bool = False
    post_login_path: str | None = None

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
    def _login_once(cls) -> None:
        if cls._session_logged_in:
            return
        cls.login.complete_login_flow(EMPLOYEE_ID, PASSWORD, IP_ADDRESS)
        cls.post_login_path = cls.home.handle_post_login_either_path()
        cls._session_logged_in = True

    @classmethod
    def setUpClass(cls) -> None:
        cls._session_logged_in = False
        cls.post_login_path = None
        cls._start_driver()
        cls._login_once()

    @classmethod
    def tearDownClass(cls) -> None:
        if getattr(cls, "driver", None) is not None:
            cls.driver.quit()
            cls.driver = None
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