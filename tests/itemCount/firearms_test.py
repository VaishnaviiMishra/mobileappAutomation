"""
Item Count — Full Firearms Recount Flow.

Primary flow:
    step1  — Opening count → Firearms → Start count
    Attempt 1: Fill counts (Handguns, Long Guns, etc.) → Review Firearms counts
    reviewcount — Review Firearms Count → scroll → Start Firearms recount
    Attempt 2 (same pattern)
    Attempt 3 (same pattern)
    reviewcount — Start Firearms recount → Approve screen
    Approve Screen — Verify 'Submit without recount' option is visible

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.firearms_test -v
"""

from __future__ import annotations

import unittest
import allure

from pages.itemCount.firearms_page import FirearmsRecountPage
from tests.shared_session import SharedAppiumTestCase

# Specific credentials dedicated to this test flow
FIREARMS_EMP_ID = "500000016"
FIREARMS_PASSWORD = "222222"
FIREARMS_IP = "10.40.236.3"


def run_full_firearms_recount_flow(test_case, firearms_page: FirearmsRecountPage) -> None:
    """Shared recount flow body used by standalone tests."""
    firearms_page.open_from_home()

    firearms_page.select_opening_firearms()
    firearms_page.tap_start_count()

    for attempt in range(1, FirearmsRecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Firearms Recount Attempt {attempt} ---")
        
        # Firearms are on a single page, so we don't need to iterate through 'Next case'
        firearms_page.complete_firearms_counts_for_attempt()
        
        firearms_page.verify_review_screen()
        firearms_page.scroll_review_screen()
        firearms_page.tap_start_firearms_recount()

    print("\n--- Reached Final Approval Screen ---")
    firearms_page.verify_approve_screen()

    submit_button = firearms_page.wait.until_present(
        firearms_page._resource(FirearmsRecountPage.SUBMIT_WITHOUT_RECOUNT_BTN_ID)
    )
    test_case.assertTrue(
        submit_button.is_displayed(),
        "Submit without recount button should be visible so we have the option to finish.",
    )

    print("\nReached final step successfully. Actual submission is commented out for re-testing.")

    # --- TEMPORARILY DISABLED TO PREVENT ACTUAL SUBMISSION ---
    # firearms_page.tap_submit_without_recount()


class TestFirearmsRecountFlow(SharedAppiumTestCase):
    
    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(FIREARMS_EMP_ID, FIREARMS_PASSWORD, FIREARMS_IP)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.firearms_page = FirearmsRecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Full firearms recount flow (3 attempts)")
    def test_01_full_firearms_recount_flow(self) -> None:
        """Execute the 3-attempt Firearms recount loop and verify final submission option."""
        run_full_firearms_recount_flow(self, self.firearms_page)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestFirearmsRecountFlow.__module__}.{TestFirearmsRecountFlow.__qualname__}"
        ".test_01_full_firearms_recount_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())