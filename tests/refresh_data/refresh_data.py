"""
Refresh data flows (long-running): Product MDM and Item Locations.

Profile menu (accountlogo) → confirm (datamdmQ / refreshlocationQ) → Data Sync (datasync / datasyncretailer).

Not part of the default ``run_tests.py`` suite. Run with::

    python run_refresh_test.py
"""

from __future__ import annotations
import sys
import allure
from allure_commons.types import AttachmentType
import unittest

from pages.refresh.refresh_data_page import RefreshDataPage
from tests.shared_session import SharedAppiumTestCase


class TestRefreshData(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.refresh = RefreshDataPage(cls.driver, cls.home)

    def tearDown(self) -> None:
        # Flows return to home; avoid Back during Data Sync.
        # However, we still want a screenshot if it fails!
        outcome = getattr(self, '_outcome', None)
        if outcome:
            errors = getattr(outcome, 'errors', [])
            for test_name, error in errors:
                if error:
                    try:
                        allure.attach(
                            self.driver.get_screenshot_as_png(),
                            name="Refresh_Data_Failure_Screen",
                            attachment_type=AttachmentType.PNG
                        )
                    except Exception as e:
                        print(f"Failed to capture screenshot: {e}")
                    break

    @allure.epic("1. User Action (App state, settings, auth)")
    @allure.feature("Profile menu layout verification")
    def test_01_account_menu_ui(self) -> None:
        """Verify profile menu layout (accountlogo.xml) without starting refresh."""
        print("\n--- Opening Profile Menu from Dashboard ---")
        self.refresh.open_profile_menu_from_home()
        
        print("\n--- Verifying Account Menu UI Layout ---")
        self.refresh.verify_account_menu_layout()
        
        print("\n--- Closing Profile Menu ---")
        self.refresh.close_profile_menu()
        self.assertTrue(self.home.is_home_visible(), "Home should be visible after closing profile menu.")
        print("--- Returned to Home Successfully ---")

    @allure.epic("1. User Action (App state, settings, auth)")
    @allure.feature("Refresh Product MDM data sync flow")
    def test_02_refresh_product_mdm_data_flow(self) -> None:
        """
        Refresh Product MDM Data → Yes → Data Sync until Downloaded → Close.

        Can take 5–15+ minutes (EZPAWNPAL_MDM_REFRESH_TIMEOUT, default 900s).
        """
        print("\n--- Starting Product MDM Data Refresh Flow ---")
        self.refresh.run_refresh_product_mdm_flow()
        
        print("\n--- MDM Refresh Complete. Verifying Return to Dashboard ---")
        self.assertTrue(self.home.is_home_visible(), "Home should be visible after MDM refresh.")

    @allure.epic("1. User Action (App state, settings, auth)")
    @allure.feature("Refresh Item Locations data sync flow")
    def test_03_refresh_item_locations_data_flow(self) -> None:
        """
        Refresh Item Locations Data → Yes → Data Sync until Downloaded → Close.

        Can take 5–15+ minutes (EZPAWNPAL_LOCATIONS_REFRESH_TIMEOUT, default 900s).
        """
        print("\n--- Starting Item Locations Data Refresh Flow ---")
        self.refresh.run_refresh_item_locations_flow()
        
        print("\n--- Item Locations Refresh Complete. Verifying Return to Dashboard ---")
        self.assertTrue(
            self.home.is_home_visible(),
            "Home should be visible after Item Locations refresh.",
        )


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_01_account_menu_ui",
        "test_02_refresh_product_mdm_data_flow",
        "test_03_refresh_item_locations_data_flow",
    ):
        suite.addTest(
            loader.loadTestsFromName(
                f"{TestRefreshData.__module__}.{TestRefreshData.__qualname__}.{name}"
            )
        )
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
