"""
Item Count — Opening Firearms Recount Flow (Attempt 4 -> Unmatched).

Primary flow:
    step1  — Opening count → Firearms → Start count
    Attempt 1: Fill counts → Review Firearms counts → Start Firearms recount
    Attempt 2 (same pattern)
    Attempt 3 (same pattern)
    Approve Screen — Tap 'Recount' to force Attempt 4 (Manager Recount)
    Attempt 4 — Fill counts -> Review Firearms Counts
    Final Screen — Verify "Submit unmatched counts" -> Tap "Go to count home"

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.firearms4recount_test -v
"""

from __future__ import annotations

import unittest
import time
import allure

from pages.itemCount.firearms4recount_page import Firearms4RecountPage
from tests.shared_session import SharedAppiumTestCase

# Specific credentials dedicated to this test flow
FIREARMS_EMP_ID = "500000016"
FIREARMS_PASSWORD = "222222"
FIREARMS_IP = "10.40.236.3"


def run_opening_firearms_attempt4_flow(test_case, firearms4_recount: Firearms4RecountPage) -> None:
    """Shared opening-firearms attempt-4 flow for standalone and full-suite tests."""
    firearms4_recount.open_from_home()

    if firearms4_recount.is_opening_firearms_completed():
        msg = "Opening firearms count is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    firearms4_recount.select_opening_firearms()
    firearms4_recount.tap_start_count()

    for attempt in range(1, Firearms4RecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Recount Attempt {attempt} ---")
        firearms4_recount.complete_firearms_counts_for_attempt()
        firearms4_recount.verify_review_screen()
        firearms4_recount.scroll_review_screen()
        firearms4_recount.tap_start_firearms_recount()

    print("\n--- Reached Approve Screen (End of Attempt 3) ---")
    firearms4_recount.verify_approve_screen()

    print("\n--- Tapping Recount to enter Attempt 4 ---")
    firearms4_recount.tap_recount_on_approve_screen()

    print("\n--- Starting Recount Attempt 4 (Manager Recount) ---")
    firearms4_recount.complete_firearms_counts_for_attempt()
    firearms4_recount.verify_review_screen()

    print("\n--- Verifying Final Unmatched Screen ---")
    submit_btn = firearms4_recount.wait.until_present(
        firearms4_recount._resource(Firearms4RecountPage.SUBMIT_UNMATCHED_BTN_ID)
    )
    test_case.assertTrue(
        submit_btn.is_displayed(),
        "Submit unmatched counts button should be visible.",
    )

    print("\nReaching final unmatched screen successfully. Submission is commented out.")

    # --- TEMPORARILY DISABLED TO PREVENT ACTUAL SUBMISSION ---
    # firearms4_recount.tap_submit_unmatched_counts()

    print("\n--- Tapping 'Go to count home' ---")
    firearms4_recount.tap_go_to_count_home()
    
    # Give the app 2 seconds to actually load and render the Item Count Hub
    time.sleep(2)
    
    # Keep the original assertion: it MUST be the hub screen!
    test_case.assertTrue(
        firearms4_recount.is_on_hub_screen(),
        "Should have successfully navigated back to the Item Count hub.",
    )


class TestFirearms4RecountFlow(SharedAppiumTestCase):

    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(FIREARMS_EMP_ID, FIREARMS_PASSWORD, FIREARMS_IP)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.firearms4_recount = Firearms4RecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Opening firearms 4th attempt (Unmatched) flow")
    def test_01_opening_firearms_attempt4_flow(self) -> None:
        """Execute the 4-attempt opening firearms recount loop and verify unmatched submission option."""
        run_opening_firearms_attempt4_flow(self, self.firearms4_recount)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestFirearms4RecountFlow.__module__}.{TestFirearms4RecountFlow.__qualname__}"
        ".test_01_opening_firearms_attempt4_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())