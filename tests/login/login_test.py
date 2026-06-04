"""
Login page — layout verification and credential entry tests.

Usage:
    .venv/bin/python3 -m unittest tests.login.login_test -v
"""

from __future__ import annotations

import unittest

from pages.login.login_page import LoginPage
from tests.shared_session import SharedAppiumTestCase, EMPLOYEE_ID, PASSWORD, IP_ADDRESS


class TestLoginPage(SharedAppiumTestCase):
    """Tests for the login screen and IP modal UI elements."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.login_page = cls.login

    def test_login_layout(self) -> None:
        """Verify all static UI elements on the login screen are visible."""
        self.login_page.launch_app()

        self.assertTrue(self.login_page.header_title.is_displayed())
        self.assertTrue(self.login_page.stg_environment_badge.is_displayed())
        self.assertTrue(self.login_page.login_title.is_displayed())
        self.assertTrue(self.login_page.login_subtitle.is_displayed())
        self.assertTrue(self.login_page.employee_id_label.is_displayed())
        self.assertTrue(self.login_page.employee_id_input.is_displayed())
        self.assertTrue(self.login_page.password_label.is_displayed())
        self.assertTrue(self.login_page.password_input.is_displayed())
        self.assertTrue(self.login_page.show_password_toggle.is_displayed())
        self.assertTrue(self.login_page.login_button.is_displayed())
        self.assertTrue(self.login_page.app_version_footer.is_displayed())

    def test_ip_modal_layout(self) -> None:
        """Verify all static UI elements on the IP modal are visible."""
        self.login_page.launch_app()
        self.login_page.enter_credentials(EMPLOYEE_ID, PASSWORD)
        self.login_page.click_log_in()
        self.login_page.wait_for_ip_modal()

        self.assertTrue(self.login_page.ip_modal_root.is_displayed())
        self.assertTrue(self.login_page.ip_environment_badge.is_displayed())
        self.assertTrue(self.login_page.ip_modal_title.is_displayed())
        self.assertTrue(self.login_page.ip_modal_instruction.is_displayed())
        self.assertTrue(self.login_page.ip_address_label.is_displayed())
        self.assertTrue(self.login_page.ip_address_input.is_displayed())
        self.assertTrue(self.login_page.ip_continue_button.is_displayed())

    def test_credentials_and_ip_flow(self) -> None:
        """End-to-end: launch → credentials → IP → Continue."""
        self.login_page.launch_app()
        self.login_page.enter_credentials(EMPLOYEE_ID, PASSWORD)
        self.login_page.click_log_in()
        self.login_page.wait_for_ip_modal()
        self.login_page.ensure_ip_address_and_continue(IP_ADDRESS)

        screen = self.home.wait_for_post_login_screen()
        self.assertIn(screen, ("data_sync", "home"))


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_login_layout",
        "test_ip_modal_layout",
        "test_credentials_and_ip_flow",
    ):
        suite.addTest(loader.loadTestsFromName(
            f"{TestLoginPage.__module__}.{TestLoginPage.__qualname__}.{name}"
        ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
