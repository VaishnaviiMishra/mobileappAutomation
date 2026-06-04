"""
Full ezPawnPal flow in one Appium session (login once, navigate with Back / menu).

Default entry point for ``python run_tests.py``.
"""

from __future__ import annotations

import unittest

from pages.item_manager.barcode_scan_page import BarcodeScanPage
from pages.itemCount.item_count_page import ItemCountPage
from pages.itemLocator.assign_item_location import AssignItemLocationPage
from pages.itemLocator.item_locator_page import ItemLocatorPage
from pages.itemLocator.label_confimation import LabelConfimationPage
from pages.itemLocator.label_location_assign import LabelLocationAssignPage
from tests.shared_session import SharedAppiumTestCase


class TestEzPawnPalSuite(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.retail = BarcodeScanPage(cls.driver, cls.home)
        cls.item_count = ItemCountPage(cls.driver, cls.home)
        cls.item_locator = ItemLocatorPage(cls.driver, cls.home)
        cls.assign_location = AssignItemLocationPage(cls.driver, cls.home)
        cls.setup_location = LabelLocationAssignPage(cls.driver, cls.home)
        cls.label_confirm = LabelConfimationPage(cls.driver, cls.home)

    def test_01_login_and_store_location_setup(self) -> None:
        self.assertTrue(
            self.home.is_home_visible(),
            "Home screen should be visible after login and store setup.",
        )

    def test_02_post_login_home_or_data_sync(self) -> None:
        self.assertIn(self.post_login_path, ("data_sync", "home"))
        self.assertTrue(self.home.is_home_visible(), "Home screen should be visible.")

    def test_03_item_count_layout_and_buttons(self) -> None:
        self.item_count.open_from_home()
        self.item_count.verify_hub_layout()

        self.assertTrue(self.item_count.get_hamburger_button().is_displayed())
        self.assertTrue(self.item_count.get_page_title().is_displayed())
        self.assertTrue(self.item_count.get_instruction().is_displayed())

        if not self.item_count.has_manage_jewelry_cases_link():
            self.skipTest("Manage jewelry cases link not shown on this store layout.")

        new_count = self.item_count.complete_manage_jewelry_cases_flow()
        self.assertTrue(self.item_count.is_on_hub_screen())
        self.assertGreater(new_count, 0)

    def test_04_item_locator_layout_and_buttons(self) -> None:
        self.item_locator.open_from_home()

        self.assertTrue(self.item_locator.get_hamburger_button().is_displayed())
        self.assertTrue(self.item_locator.get_module_title().is_displayed())
        self.assertTrue(self.item_locator.get_subtitle().is_displayed())
        self.assertTrue(self.item_locator.get_assign_button().is_displayed())
        self.assertTrue(self.item_locator.get_setup_button().is_displayed())

        self.item_locator.tap_setup_location()
        self.item_locator.return_to_hub()

        self.item_locator.back_to_home()
        self.assertTrue(self.home.is_home_visible())

    def test_05_retail_item_manager_live_barcode_scan(self) -> None:
        """Retail item details for store 14401 item (current test login)."""
        self.retail.ensure_on_home_before_menu()
        self.retail.navigate_to_retail_item_manager_via_menu()

        item_id = self.retail.lookup_item_number_to_details(BarcodeScanPage.STORE_14401_ITEM_ID)
        self.assertEqual(item_id.replace(" ", ""), BarcodeScanPage.STORE_14401_ITEM_ID)
        self.retail.verify_item_details_overview(item_id)
        self.retail.tap_edit_on_details()
        self.retail.complete_edit_color_and_update_flow(item_id)
        self.retail.tap_go_home_from_item_updated_modal()

        self.retail.return_to_dashboard_via_menu()
        self.assertTrue(
            self.home.is_home_visible(),
            "MODULES dashboard should be visible after leaving Retail Item Manager.",
        )

    def test_06_assign_item_location(self) -> None:
        """Assign item location — toggle A 24 / A 54 (same timeout as standalone test)."""
        self.home.navigate_to_dashboard_via_menu()
        item_id, chosen_location = self.assign_location.execute_full_assign_flow(
            timeout=AssignItemLocationPage.DEFAULT_FLOW_TIMEOUT,
        )
        self.assertEqual(
            item_id.replace(" ", ""),
            AssignItemLocationPage.STORE_14401_ITEM_ID,
        )
        chosen_key = AssignItemLocationPage._normalize_location_key(chosen_location)
        self.assertIn(
            chosen_key,
            AssignItemLocationPage.TOGGLE_LOCATION_KEYS,
            f"Expected A 24 or A 54, got {chosen_location!r}.",
        )
        self.assertTrue(
            self.home.is_home_visible(),
            "Home screen should be visible after assign item location flow.",
        )

    def test_07_setup_location_change(self) -> None:
        """Scan QR → Change → read CURRENT LABEL → pick a different label → home."""
        chosen = self.setup_location.execute_full_setup_flow(
            flow_timeout=LabelLocationAssignPage.DEFAULT_FLOW_TIMEOUT,
        )
        self.assertTrue(len(chosen) > 0, "A new location label should be selected.")
        LabelConfimationPage.expected_location_from_setup = chosen
        type(self).expected_setup_location = chosen
        self.assertTrue(
            self.home.is_home_visible(),
            "Home screen should be visible after Setup Location flow.",
        )

    def test_08_label_confimation(self) -> None:
        """Re-scan setup label → CURRENT LABEL must match test_07 choice."""
        expected = (
            getattr(type(self), "expected_setup_location", None)
            or LabelConfimationPage.expected_location_from_setup
        )
        self.assertIsNotNone(
            expected,
            "test_07 must run first and set the expected setup location.",
        )

        actual = self.label_confirm.verify_current_label_matches(expected)
        self.assertEqual(
            LabelLocationAssignPage._normalize_label_key(actual),
            LabelLocationAssignPage._normalize_label_key(expected),
        )
        
        # Ensure we return to dashboard so test_09 starts perfectly
        self.home.navigate_to_dashboard_via_menu()
        self.assertTrue(self.home.is_home_visible())

    def test_09_item_count_jewelry_recount(self) -> None:
        """Full jewelry recount flow (store 14401) — starts from MODULES dashboard."""
        from pages.itemCount.itemrecount_page import ItemRecountPage
        from tests.itemCount.itemrecount_test import run_full_jewelry_recount_flow

        self.home.navigate_to_dashboard_via_menu()
        self.assertTrue(
            self.home.is_home_visible(),
            "MODULES dashboard should be visible before Item Count recount.",
        )
        item_recount = ItemRecountPage(self.driver, self.home)
        run_full_jewelry_recount_flow(self, item_recount)


def load_suite() -> unittest.TestSuite:
    """Run tests in numbered order (login → home → item count → … → jewelry recount)."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_01_login_and_store_location_setup",
        "test_02_post_login_home_or_data_sync",
        "test_03_item_count_layout_and_buttons",
        "test_04_item_locator_layout_and_buttons",
        "test_05_retail_item_manager_live_barcode_scan",
        "test_06_assign_item_location",
        "test_07_setup_location_change",
        "test_08_label_confimation",
        "test_09_item_count_jewelry_recount",
    ):
        suite.addTest(loader.loadTestsFromName(f"{TestEzPawnPalSuite.__module__}.{TestEzPawnPalSuite.__qualname__}.{name}"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())