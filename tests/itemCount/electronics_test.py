"""
Item Count — Full Electronics Recount Flow.

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.electronics_test -v
"""

from __future__ import annotations

import unittest
import allure

from pages.itemCount.electronics_page import ElectronicsRecountPage
from tests.shared_session import SharedAppiumTestCase

# Specific credentials dedicated to this test flow
ELEC_EMP_ID = "500000016"
ELEC_PASSWORD = "222222"
ELEC_IP = "10.40.236.3"


def run_full_electronics_recount_flow(test_case, elec_page: ElectronicsRecountPage) -> None:
    elec_page.open_from_home()

    if elec_page.is_additional_electronics_completed():
        msg = "Electronics count is already done for the day. Try again tomorrow."
        print(f"\n{msg}")
        allure.dynamic.description(msg)
        return

    elec_page.select_additional_electronics()
    elec_page.tap_start_count()

    for attempt in range(1, ElectronicsRecountPage.MAX_RECOUNT_ATTEMPTS + 1):
        print(f"\n--- Starting Electronics Recount Attempt {attempt} ---")
        elec_page.complete_electronics_counts_for_attempt()
        elec_page.verify_review_screen()
        elec_page.scroll_review_screen()
        elec_page.tap_start_electronics_recount()

    print("\n--- Reached Final Approval Screen ---")
    elec_page.verify_approve_screen()

    submit_button = elec_page.wait.until_present(
        elec_page._resource(ElectronicsRecountPage.SUBMIT_WITHOUT_RECOUNT_BTN_ID)
    )
    test_case.assertTrue(
        submit_button.is_displayed(),
        "Submit without recount button should be visible so we have the option to finish.",
    )

    print("\nReached final step successfully. Actual submission is commented out for re-testing.")
    # elec_page.tap_submit_without_recount()


class TestElectronicsRecountFlow(SharedAppiumTestCase):
    
    @classmethod
    def _login_once(cls) -> None:
        cls._login_with_credentials(ELEC_EMP_ID, ELEC_PASSWORD, ELEC_IP)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.elec_page = ElectronicsRecountPage(cls.driver, cls.home)

    def setUp(self) -> None:
        self.home.navigate_to_dashboard_via_menu()

    @allure.epic("4. Item Count (Auditing and counting)")
    @allure.feature("Full electronics recount flow (3 attempts)")
    def test_01_full_electronics_recount_flow(self) -> None:
        run_full_electronics_recount_flow(self, self.elec_page)


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestElectronicsRecountFlow.__module__}.{TestElectronicsRecountFlow.__qualname__}"
        ".test_01_full_electronics_recount_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())