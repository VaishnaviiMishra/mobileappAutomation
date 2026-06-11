"""
Assign Item Location wrong barcode scan — wrong-store modal and recovery flow.

Usage:
    .venv/bin/python3 -m unittest tests.itemLocator.assignitem_scan_error -v
"""

from __future__ import annotations

import unittest

import allure

from pages.itemLocator.assignitem_scan_error import AssignItemScanErrorPage
from tests.shared_session import SharedAppiumTestCase


class TestAssignItemScanError(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.assign_error = AssignItemScanErrorPage(cls.driver, cls.home)

    @allure.epic("3. Item Locator (Moving and finding inventory)")
    @allure.feature("Assign location wrong-store barcode error and recovery")
    def test_assign_item_wrong_store_scan_flow(self) -> None:
        """Scan wrong barcode in Assign Item Location, verify modal, then recover."""
        print("\n--- Starting Assign Item Location (Wrong Store Scan) Flow ---")
        item_id = self.assign_error.complete_assign_scan_to_wrong_store_modal()
        self.assertTrue(len(item_id) > 0)
        print(f"--- Invalid Scanned Item ID: {item_id} ---")

        print("\n--- Verifying Wrong Store Modal UI Elements ---")
        self.assertTrue(self.assign_error.wrong_store_badge.is_displayed())
        self.assertTrue(self.assign_error.wrong_store_title.is_displayed())
        self.assertTrue(self.assign_error.wrong_store_message.is_displayed())
        self.assertTrue(self.assign_error.scan_different_item_button.is_displayed())

        print("\n--- Tapping 'Scan a different item' for Recovery ---")
        self.assign_error.click_scan_different_item()
        self.assign_error.wait_for_assign_scan_screen()
        print("--- Successfully Recovered to Scan Screen ---")

def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestAssignItemScanError.__module__}.{TestAssignItemScanError.__qualname__}.test_assign_item_wrong_store_scan_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
