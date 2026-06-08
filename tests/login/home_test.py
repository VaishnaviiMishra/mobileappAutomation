"""
Home page and Data Sync popup — layout verification tests.

Usage:
    .venv/bin/python3 -m unittest tests.login.home_test -v
"""

from __future__ import annotations

import unittest

import allure

from pages.login.home_page import HomePage
from tests.shared_session import SharedAppiumTestCase


class TestHomePage(SharedAppiumTestCase):
    """Tests for the post-login home screen and Data Sync popup UI."""

    @allure.epic("1. User Action (App state, settings, auth)")
    @allure.feature("MODULES dashboard layout verification")
    def test_home_layout(self) -> None:
        """Verify all static UI elements on the home screen are visible."""
        self.assertTrue(self.home.is_home_visible(), "Should be on home screen.")

        self.assertTrue(self.home.hamburger_button.is_displayed())
        self.assertTrue(self.home.header_title.is_displayed())
        self.assertTrue(self.home.profile_button.is_displayed())
        self.assertTrue(self.home.welcome_message.is_displayed())
        self.assertTrue(self.home.store_line.is_displayed())
        self.assertTrue(self.home.modules_heading.is_displayed())
        self.assertTrue(self.home.item_count_module.is_displayed())
        self.assertTrue(self.home.item_locator_module.is_displayed())
        self.assertTrue(self.home.retail_item_manager_module.is_displayed())
        self.assertTrue(self.home.drop_collection_module.is_displayed())
        self.assertTrue(self.home.app_version_footer.is_displayed())

    @allure.epic("1. User Action (App state, settings, auth)")
    @allure.feature("Data Sync popup layout verification")
    def test_data_sync_layout_if_visible(self) -> None:
        """If Data Sync popup appears, verify its elements before dismissing."""
        if not self.home.is_data_sync_visible():
            self.skipTest("Data Sync popup not visible in this session.")

        self.assertTrue(self.home.data_sync_title.is_displayed())
        self.assertTrue(self.home.product_mdm_label.is_displayed())
        self.assertTrue(self.home.item_locations_label.is_displayed())

        downloaded = self.home.get_downloaded_elements()
        self.assertGreaterEqual(
            len(downloaded), 2,
            "Expected at least two 'Downloaded' statuses (Product MDM and Item Locations).",
        )
        self.assertTrue(self.home.data_sync_close_button.is_displayed())

        self.home.dismiss_data_sync_popup()
        self.assertTrue(self.home.is_home_visible())

    @allure.epic("1. User Action (App state, settings, auth)")
    @allure.feature("Post-login path handling (Data Sync or home)")
    def test_post_login_path(self) -> None:
        """Verify the post-login path was handled correctly."""
        self.assertIn(self.post_login_path, ("data_sync", "home"))
        self.assertTrue(self.home.is_home_visible())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_home_layout",
        "test_data_sync_layout_if_visible",
        "test_post_login_path",
    ):
        suite.addTest(loader.loadTestsFromName(
            f"{TestHomePage.__module__}.{TestHomePage.__qualname__}.{name}"
        ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
