"""
Label confirmation — re-scan setup label and verify CURRENT LABEL persisted.

Must run after test_09 in the full suite (or set
``LabelConfimationPage.expected_location_from_setup``).

Usage:
    .venv/bin/python3 -m unittest tests.itemLocator.label_confimation -v
"""

from __future__ import annotations

import unittest

import allure

from pages.itemLocator.label_confimation import LabelConfimationPage
from pages.itemLocator.label_location_assign import LabelLocationAssignPage
from tests.shared_session import SharedAppiumTestCase


class TestLabelConfimation(SharedAppiumTestCase):
    expected_setup_location: str | None = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.confirm_page = LabelConfimationPage(cls.driver, cls.home)

    @allure.epic("3. Item Locator (Moving and finding inventory)")
    @allure.feature("Verify CURRENT LABEL matches last setup change")
    def test_current_label_matches_last_setup_change(self) -> None:
        """Re-scan label → CURRENT LABEL must match what test_09 assigned."""
        print("\n--- Preparing to Verify Setup Location Persistence ---")
        expected = (
            self.expected_setup_location
            or LabelConfimationPage.expected_location_from_setup
        )
        if not expected:
            print("\n--- Test Skipped: No Expected Location Saved in Memory ---")
            self.skipTest(
                "No expected location: run test_09 first or set "
                "LabelConfimationPage.expected_location_from_setup."
            )

        print(f"\n--- Expected Location to Match: {expected} ---")
        print("\n--- Executing Label Verification Scan ---")
        actual = self.confirm_page.verify_current_label_matches(expected)
        print(f"\n--- Verified Match! Actual Label Read: {actual} ---")
        print("\n--- Returning to Dashboard via Hamburger Menu ---")
        self.assertEqual(
            LabelLocationAssignPage._normalize_label_key(actual),
            LabelLocationAssignPage._normalize_label_key(expected),
        )
        
        # FIX: Use the hamburger menu to return to the Dashboard
        # This ensures the next test (item recount) starts on the correct screen
        self.home.navigate_to_dashboard_via_menu()
        self.assertTrue(self.home.is_home_visible())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestLabelConfimation.__module__}.{TestLabelConfimation.__qualname__}"
        ".test_current_label_matches_last_setup_change"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())