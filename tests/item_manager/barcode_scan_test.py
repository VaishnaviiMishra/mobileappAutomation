"""
Retail Item Manager barcode scan — layout, item details overview, and edit flow.

Usage:
    .venv/bin/python3 -m unittest tests.item_manager.barcode_scan_test -v
"""

from __future__ import annotations

import unittest

from pages.item_manager.barcode_scan_page import BarcodeScanPage
from tests.shared_session import SharedAppiumTestCase


class TestBarcodeScan(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.retail = BarcodeScanPage(cls.driver, cls.home)

    def test_retail_scan_layout(self) -> None:
        """Verify all static UI elements on the Retail Item Manager scan screen."""
        self.retail.open_from_home()

        self.assertTrue(self.home.hamburger_button.is_displayed())
        self.assertTrue(self.retail.page_title.is_displayed())
        self.assertTrue(self.retail.scan_heading.is_displayed())
        self.assertTrue(self.retail.screen_subtitle.is_displayed())
        self.assertTrue(self.retail.scan_preview.is_displayed())
        self.assertTrue(self.retail.manual_entry_hint.is_displayed())
        self.assertTrue(self.retail.item_number_label.is_displayed())

        field = self.retail.item_ez_id_input()
        self.assertTrue(field.is_displayed())
        self.assertTrue(field.is_enabled())

        self.assertTrue(self.retail.confirm_button.is_displayed())
        self.assertTrue(self.retail.confirm_button.is_enabled())

    @unittest.skip(
        "Item 230053938582 requires a different employee/store login; re-enable when credentials are available."
    )
    def test_retail_live_barcode_scan(self) -> None:
        """Default store: scan barcode, verify item details (silver / allowable discount)."""
        self.retail.ensure_on_home_before_menu()
        self.retail.navigate_to_retail_item_manager_via_menu()

        item_id = self.retail.complete_barcode_scan_to_item_details()
        self.assertEqual(item_id.replace(" ", ""), BarcodeScanPage.EXPECTED_BARCODE)
        self.retail.verify_item_details_overview(item_id)

        self.retail.return_to_dashboard_via_menu()
        self.assertTrue(self.home.is_home_visible())

    def test_retail_item_details_store_14401(self) -> None:
        """Store 14401: details, edit color, update/print, Item Updated modal, go home."""
        self.retail.ensure_on_home_before_menu()
        self.retail.navigate_to_retail_item_manager_via_menu()

        item_id = self.retail.lookup_item_number_to_details(BarcodeScanPage.STORE_14401_ITEM_ID)
        self.assertEqual(item_id.replace(" ", ""), BarcodeScanPage.STORE_14401_ITEM_ID)

        self.retail.verify_item_details_overview(item_id)
        self.retail.tap_edit_on_details()
        chosen_color = self.retail.complete_edit_color_and_update_flow(item_id)
        self.assertTrue(chosen_color)

        self.retail.tap_go_home_from_item_updated_modal()
        self.assertTrue(self.home.is_home_visible())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_retail_scan_layout",
        "test_retail_item_details_store_14401",
    ):
        suite.addTest(loader.loadTestsFromName(
            f"{TestBarcodeScan.__module__}.{TestBarcodeScan.__qualname__}.{name}"
        ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
