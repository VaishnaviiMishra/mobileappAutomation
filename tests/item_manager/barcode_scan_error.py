"""
Retail Item Manager wrong barcode scan — wrong store modal and recovery flow.

Usage:
    .venv/bin/python3 -m unittest tests.item_manager.barcode_scan_error -v
"""

from __future__ import annotations

import unittest

from pages.item_manager.barcode_scan_error import BarcodeScanErrorPage
from tests.shared_session import SharedAppiumTestCase


class TestBarcodeScanError(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.retail_error = BarcodeScanErrorPage(cls.driver, cls.home)

    def test_retail_wrong_store_barcode_flow(self) -> None:
        """Scan wrong barcode, verify wrong-store modal, tap Scan a different item."""
        self.retail_error.ensure_on_home_before_menu()
        self.retail_error.navigate_to_retail_item_manager_via_menu()

        item_id = self.retail_error.complete_barcode_scan_to_wrong_store_modal()
        self.assertTrue(len(item_id) > 0)

        self.assertTrue(self.retail_error.wrong_store_badge.is_displayed())
        self.assertTrue(self.retail_error.wrong_store_title.is_displayed())
        self.assertTrue(self.retail_error.wrong_store_message.is_displayed())
        self.assertTrue(self.retail_error.scan_different_item_button.is_displayed())

        self.retail_error.click_scan_different_item()
        self.retail_error.wait_for_retail_scan_screen()
        self.assertTrue(self.retail_error.scan_heading.is_displayed())
        self.assertTrue(self.retail_error.confirm_button.is_displayed())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestBarcodeScanError.__module__}.{TestBarcodeScanError.__qualname__}.test_retail_wrong_store_barcode_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
