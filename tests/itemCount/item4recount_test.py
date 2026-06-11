"""
Item Count — Closing Jewelry Recount Flow (Attempt 4 -> Unmatched).

Primary flow:
    step1  — Closing count → Jewelry → Start count
    step2–step12 — Attempt 1: Fill counts → Next case / Review
    reviewcount — Review Jewelry Count → scroll → Start Jewelry recount
    step13–step15 — Attempt 2 (same pattern)
    reviewcount — Start Jewelry recount → Attempt 3
    step16–step15 — Attempt 3 (same pattern)
    reviewcount — Start Jewelry recount → Approve screen
    Approve Screen — Tap 'Recount' to force Attempt 4 (Manager Recount)
    Attempt 4 — Fill counts -> Review Jewelry Counts
    Final Screen — Verify "Submit unmatched counts" -> Tap "Go to count home"

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.item4recount_test -v
"""

from __future__ import annotations

import unittest
import time
import allure

from pages.itemCount.item4recount_page import Item4RecountPage
from tests.shared_session import SharedAppiumTestCase


def run_closing_jewelry_attempt4_flow(test_case, item4_recount: Item4RecountPage) -> None:
    """Shared closing-count attempt-4 flow for standalone and full-suite tests."""
    item4_recount.open_from_home()

    if item4_recount.is_closing_jewelry_completed():
        msg = "Closing count is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    item4_recount.select_closing_jewelry()
    item4_recount.tap_start_count()

    for attempt in range(1, Item4RecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Recount Attempt {attempt} ---")
        item4_recount.complete_jewelry_cases_for_attempt()
        item4_recount.verify_review_screen()
        item4_recount.scroll_review_screen()
        item4_recount.tap_start_jewelry_recount()

    print("\n--- Reached Approve Screen (End of Attempt 3) ---")
    item4_recount.verify_approve_screen()

    print("\n--- Tapping Recount to enter Attempt 4 ---")
    item4_recount.tap_recount_on_approve_screen()

    print("\n--- Starting Recount Attempt 4 (Manager Recount) ---")
    item4_recount.complete_jewelry_cases_for_attempt()
    item4_recount.verify_review_screen()

    print("\n--- Verifying Final Unmatched Screen ---")
    submit_btn = item4_recount.wait.until_present(
        item4_recount._resource(Item4RecountPage.SUBMIT_UNMATCHED_BTN_ID)
    )
    test_case.assertTrue(
        submit_btn.is_displayed(),
        "Submit unmatched counts button should be visible.",
    )

    print("\nReaching final unmatched screen successfully. Submission is commented out.")

    # --- TEMPORARILY DISABLED TO PREVENT ACTUAL SUBMISSION ---
    # item4_recount.tap_submit_unmatched_counts()
    # item4_recount.wait_for_submit_success_popup()
    # test_case.assertTrue(item4_recount.is_submit_success_popup_visible())
    # item4_recount.tap_go_to_home_from_success_popup()

    print("\n--- Tapping 'Go to count home' ---")
    item4_recount.tap_go_to_count_home()
    
    # Give the app 2 seconds to actually load and render the Item Count Hub
    time.sleep(2)
    
    # Keep the original assertion: it MUST be the hub screen!
    test_case.assertTrue(
        item4_recount.is_on_hub_screen(),
        "Should have successfully navigated back to the Item Count hub.",
    )

class TestItem4RecountFlow(SharedAppiumTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.item4_recount = Item4RecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Closing jewelry 4th attempt (Unmatched) flow")
    def test_01_closing_jewelry_attempt4_flow(self) -> None:
        """Execute the 4-attempt closing recount loop and verify unmatched submission option."""
        run_closing_jewelry_attempt4_flow(self, self.item4_recount)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestItem4RecountFlow.__module__}.{TestItem4RecountFlow.__qualname__}"
        ".test_01_closing_jewelry_attempt4_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
