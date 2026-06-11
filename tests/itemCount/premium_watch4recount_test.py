"""
Item Count — Additional Premium Watch Recount Flow (Attempt 4 -> Unmatched).

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.premium_watch4recount_test -v
"""

from __future__ import annotations

import unittest
import time
import allure

from pages.itemCount.premium_watch4recount_page import PremiumWatch4RecountPage
from tests.shared_session import SharedAppiumTestCase

# Specific credentials dedicated to this test flow
PW_EMP_ID = "500000016"
PW_PASSWORD = "222222"
PW_IP = "10.40.236.3"


def run_additional_pw_attempt4_flow(test_case, pw4_recount: PremiumWatch4RecountPage) -> None:
    pw4_recount.open_from_home()

    if pw4_recount.is_additional_pw_completed():
        msg = "Premium Watch count is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    pw4_recount.select_additional_pw()
    pw4_recount.tap_start_count()

    for attempt in range(1, PremiumWatch4RecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Recount Attempt {attempt} ---")
        pw4_recount.complete_pw_counts_for_attempt()
        pw4_recount.verify_review_screen()
        pw4_recount.scroll_review_screen()
        pw4_recount.tap_start_pw_recount()

    print("\n--- Reached Approve Screen (End of Attempt 3) ---")
    pw4_recount.verify_approve_screen()

    print("\n--- Tapping Recount to enter Attempt 4 ---")
    pw4_recount.tap_recount_on_approve_screen()

    print("\n--- Starting Recount Attempt 4 (Manager Recount) ---")
    pw4_recount.complete_pw_counts_for_attempt()
    pw4_recount.verify_review_screen()

    print("\n--- Verifying Final Unmatched Screen ---")
    submit_btn = pw4_recount.wait.until_present(
        pw4_recount._resource(PremiumWatch4RecountPage.SUBMIT_UNMATCHED_BTN_ID)
    )
    test_case.assertTrue(
        submit_btn.is_displayed(),
        "Submit unmatched counts button should be visible.",
    )

    print("\nReaching final unmatched screen successfully. Submission is commented out.")
    # pw4_recount.tap_submit_unmatched_counts()

    print("\n--- Tapping 'Go to count home' ---")
    pw4_recount.tap_go_to_count_home()
    
    time.sleep(2)
    
    test_case.assertTrue(
        pw4_recount.is_on_hub_screen(),
        "Should have successfully navigated back to the Item Count hub.",
    )


class TestPremiumWatch4RecountFlow(SharedAppiumTestCase):

    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(PW_EMP_ID, PW_PASSWORD, PW_IP)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.pw4_recount = PremiumWatch4RecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Additional premium watch 4th attempt (Unmatched) flow")
    def test_01_additional_pw_attempt4_flow(self) -> None:
        run_additional_pw_attempt4_flow(self, self.pw4_recount)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestPremiumWatch4RecountFlow.__module__}.{TestPremiumWatch4RecountFlow.__qualname__}"
        ".test_01_additional_pw_attempt4_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())