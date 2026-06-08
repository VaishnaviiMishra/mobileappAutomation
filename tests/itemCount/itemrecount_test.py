"""
Item Count — Full Jewelry Recount Flow (store 14401).

Primary flow:
    step1  — Opening count → Jewelry → Start count
    step2–step12 — Attempt 1: 11 jewelry cases (fill counts → Next case / Review)
    reviewcount — Review Jewelry Count → scroll → Start Jewelry recount
    step13–step15 — Attempt 2 (same pattern)
    reviewcount — Start Jewelry recount → Attempt 3
    step16–step15 — Attempt 3 through Jewelry Case 11 → Review Jewelry counts
    reviewcount — Start Jewelry recount → Approve screen
    step18 — Submit without recount → success popup → Go to home

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.itemrecount_test -v
"""

from __future__ import annotations

import unittest

import allure

from pages.itemCount.itemrecount_page import ItemRecountPage
from tests.shared_session import SharedAppiumTestCase


def run_full_jewelry_recount_flow(test_case, item_recount: ItemRecountPage) -> None:
    """Shared recount flow body used by standalone and full-suite tests."""
    item_recount.open_from_home()

    if item_recount.is_opening_jewelry_completed():
        msg = "Recounting is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    item_recount.select_opening_jewelry()
    item_recount.tap_start_count()

    for attempt in range(1, ItemRecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Recount Attempt {attempt} ---")
        item_recount.complete_jewelry_cases_for_attempt()
        item_recount.verify_review_screen()
        item_recount.scroll_review_screen()
        item_recount.tap_start_jewelry_recount()

    print("\n--- Reached Final Approval Screen ---")
    item_recount.verify_approve_screen()

    submit_button = item_recount.wait.until_present(
        item_recount._resource(ItemRecountPage.SUBMIT_WITHOUT_RECOUNT_BTN_ID)
    )
    test_case.assertTrue(
        submit_button.is_displayed(),
        "Submit button should be visible so we have the option to finish.",
    )

    print("\nReached final step successfully. Actual submission is commented out for re-testing.")

    # --- TEMPORARILY DISABLED TO PREVENT ACTUAL SUBMISSION ---
    # item_recount.tap_submit_without_recount()
    # item_recount.wait_for_submit_success_popup()
    # test_case.assertTrue(item_recount.is_submit_success_popup_visible())
    # item_recount.tap_go_to_home_from_success_popup()
    # test_case.assertTrue(item_recount.is_on_hub_screen())


class TestItemCountRecountFlow(SharedAppiumTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.item_recount = ItemRecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Full jewelry recount flow (3 attempts, store 14401)")
    def test_01_full_jewelry_recount_flow(self) -> None:
        """Execute the 3-attempt recount loop and verify final submission option."""
        run_full_jewelry_recount_flow(self, self.item_recount)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestItemCountRecountFlow.__module__}.{TestItemCountRecountFlow.__qualname__}"
        ".test_01_full_jewelry_recount_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
