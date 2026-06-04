"""
Login error scenarios — invalid employee ID, password, and IP address.

Usage:
    .venv/bin/python3 -m unittest tests.login.loginerrors -v
"""

from __future__ import annotations

import json
import os
import unittest
import sys
import allure
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options

from pages.login.loginerrors import LoginErrorsPage
from tests.shared_session import EMPLOYEE_ID, IP_ADDRESS, PASSWORD, PROJECT_ROOT


class TestLoginErrors(unittest.TestCase):
    """Verify login validation errors for employee ID, password, and IP."""

    driver: webdriver.Remote
    login_errors: LoginErrorsPage

    @classmethod
    def setUpClass(cls) -> None:
        caps_path = PROJECT_ROOT / "ezpawnpal.json"
        with caps_path.open(encoding="utf-8") as f:
            caps = json.load(f)

        options = UiAutomator2Options()
        for key, value in caps.items():
            options.set_capability(key, value)

        server_url = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
        cls.driver = webdriver.Remote(server_url, options=options)
        cls.login_errors = LoginErrorsPage(cls.driver)

    @classmethod
    def tearDownClass(cls) -> None:
        if getattr(cls, "driver", None) is not None:
            cls.driver.quit()
            cls.driver = None

    @classmethod
    def tearDownClass(cls) -> None:
        if getattr(cls, "driver", None) is not None:
            cls.driver.quit()
            cls.driver = None

    # ADD THIS NEW METHOD HERE:
    def tearDown(self) -> None:
        outcome = getattr(self, '_outcome', None)
        if outcome:
            errors = getattr(outcome, 'errors', [])
            for test_name, error in errors:
                if error:
                    try:
                        allure.attach(
                            self.driver.get_screenshot_as_png(),
                            name="Login_Error_Failure_Screen",
                            attachment_type=AttachmentType.PNG
                        )
                    except Exception as e:
                        print(f"Failed to capture screenshot: {e}")
                    break

    def test_login_error_scenarios(self) -> None:
        """Use the same login flow, but with invalid values per scenario."""

        with self.subTest(scenario="invalid employee ID"):
            self.login_errors.launch_app()
            self.login_errors.enter_credentials(
                LoginErrorsPage.INVALID_EMPLOYEE_ID,
                PASSWORD,
            )
            self.login_errors.click_log_in()
            self.login_errors.wait_for_ip_modal()
            self.login_errors.enter_ip_on_modal_and_continue(IP_ADDRESS)
            error = self.login_errors.wait_for_employee_not_found_error()
            self.assertTrue(error.is_displayed())

        with self.subTest(scenario="invalid password"):
            self.login_errors.launch_app()
            self.login_errors.enter_credentials(
                EMPLOYEE_ID,
                LoginErrorsPage.INVALID_PASSWORD,
            )
            self.login_errors.click_log_in()
            self.login_errors.wait_for_ip_modal()
            self.login_errors.enter_ip_on_modal_and_continue(IP_ADDRESS)
            error = self.login_errors.wait_for_password_incorrect_error()
            self.assertTrue(error.is_displayed())

        with self.subTest(scenario="invalid IP address"):
            self.login_errors.launch_app()
            self.login_errors.enter_credentials(EMPLOYEE_ID, PASSWORD)
            self.login_errors.click_log_in()
            self.login_errors.wait_for_ip_modal()
            self.login_errors.enter_ip_on_modal_and_continue(
                LoginErrorsPage.INVALID_IP_ADDRESS,
            )
            error = self.login_errors.wait_for_ip_location_error()
            self.assertTrue(error.is_displayed())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestLoginErrors.__module__}.{TestLoginErrors.__qualname__}.test_login_error_scenarios"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
