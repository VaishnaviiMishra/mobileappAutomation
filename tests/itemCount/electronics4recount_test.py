"""
Item Count — Additional Electronics Recount Flow (Attempt 4 -> Unmatched).

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.electronics4recount_test -v
"""

from __future__ import annotations

import unittest
import time
import allure

from pages.itemCount.electronics4recount_page import Electronics4RecountPage
from tests.shared_session import SharedAppiumTestCase

# Specific credentials dedicated to this test flow
ELEC_EMP_ID = "500000016"
ELEC_PASSWORD = "222222"
ELEC_IP = "10.40.236.3"


def run_additional_electronics_attempt4_flow(test_case, elec4_recount: Electronics4RecountPage) -> None:
    elec4_recount.open_from_home()

    if elec4_recount.is_additional_electronics_completed():
        msg = "Electronics count is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    elec4_recount.select_additional_electronics()
    elec4_recount.tap_start_count()

    for attempt in range(1, Electronics4RecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Recount Attempt {attempt} ---")
        elec4_recount.complete_electronics_counts_for_attempt()
        elec4_recount.verify_review_screen()
        elec4_recount.scroll_review_screen()
        elec4_recount.tap_start_electronics_recount()

    print("\n--- Reached Approve Screen (End of Attempt 3) ---")
    elec4_recount.verify_approve_screen()

    print("\n--- Tapping Recount to enter Attempt 4 ---")
    elec4_recount.tap_recount_on_approve_screen()

    print("\n--- Starting Recount Attempt 4 (Manager Recount) ---")
    elec4_recount.complete_electronics_counts_for_attempt()
    elec4_recount.verify_review_screen()

    print("\n--- Verifying Final Unmatched Screen ---")
    submit_btn = elec4_recount.wait.until_present(
        elec4_recount._resource(Electronics4RecountPage.SUBMIT_UNMATCHED_BTN_ID)
    )
    test_case.assertTrue(
        submit_btn.is_displayed(),
        "Submit unmatched counts button should be visible.",
    )

    print("\nReaching final unmatched screen successfully. Submission is commented out.")
    # elec4_recount.tap_submit_unmatched_counts()

    print("\n--- Tapping 'Go to count home' ---")
    elec4_recount.tap_go_to_count_home()
    
    # Give the app 2 seconds to actually load and render the Item Count Hub
    time.sleep(2)
    
    test_case.assertTrue(
        elec4_recount.is_on_hub_screen(),
        "Should have successfully navigated back to the Item Count hub.",
    )


class TestElectronics4RecountFlow(SharedAppiumTestCase):

    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(ELEC_EMP_ID, ELEC_PASSWORD, ELEC_IP)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.elec4_recount = Electronics4RecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Additional electronics 4th attempt (Unmatched) flow")
    def test_01_additional_electronics_attempt4_flow(self) -> None:
        run_additional_electronics_attempt4_flow(self, self.elec4_recount)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestElectronics4RecountFlow.__module__}.{TestElectronics4RecountFlow.__qualname__}"
        ".test_01_additional_electronics_attempt4_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())