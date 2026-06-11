"""
Item Count — Full Premium Watch Recount Flow.

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.premium_watch_test -v
"""

from __future__ import annotations

import unittest
import allure

from pages.itemCount.premium_watch_page import PremiumWatchRecountPage
from tests.shared_session import SharedAppiumTestCase

# Specific credentials dedicated to this test flow
PW_EMP_ID = "500000016"
PW_PASSWORD = "222222"
PW_IP = "10.40.236.3"


def run_full_pw_recount_flow(test_case, pw_page: PremiumWatchRecountPage) -> None:
    pw_page.open_from_home()

    if pw_page.is_additional_pw_completed():
        msg = "Premium Watch count is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    pw_page.select_additional_pw()
    pw_page.tap_start_count()

    for attempt in range(1, PremiumWatchRecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Premium Watch Recount Attempt {attempt} ---")
        pw_page.complete_pw_counts_for_attempt()
        pw_page.verify_review_screen()
        pw_page.scroll_review_screen() # Just a 1-sec pause, no actual scrolling
        pw_page.tap_start_pw_recount()

    print("\n--- Reached Final Approval Screen ---")
    pw_page.verify_approve_screen()

    submit_button = pw_page.wait.until_present(
        pw_page._resource(PremiumWatchRecountPage.SUBMIT_WITHOUT_RECOUNT_BTN_ID)
    )
    test_case.assertTrue(
        submit_button.is_displayed(),
        "Submit without recount button should be visible so we have the option to finish.",
    )

    print("\nReached final step successfully. Actual submission is commented out for re-testing.")
    # pw_page.tap_submit_without_recount()


class TestPremiumWatchRecountFlow(SharedAppiumTestCase):
    
    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(PW_EMP_ID, PW_PASSWORD, PW_IP)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.pw_page = PremiumWatchRecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Full premium watch recount flow (3 attempts)")
    def test_01_full_pw_recount_flow(self) -> None:
        run_full_pw_recount_flow(self, self.pw_page)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestPremiumWatchRecountFlow.__module__}.{TestPremiumWatchRecountFlow.__qualname__}"
        ".test_01_full_pw_recount_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())