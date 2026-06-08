"""
Item Locator hub — layout verification and Setup Location button test.

Usage:
    .venv/bin/python3 -m unittest tests.itemLocator.item_locator_test -v
"""

from __future__ import annotations

import unittest

import allure

from pages.itemLocator.item_locator_page import ItemLocatorPage
from tests.shared_session import SharedAppiumTestCase


class TestItemLocatorHub(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.item_locator = ItemLocatorPage(cls.driver, cls.home)

    @allure.epic("3. Item Locator (Moving and finding inventory)")
    @allure.feature("Item Locator hub layout verification")
    def test_item_locator_layout(self) -> None:
        """Verify all static UI elements on the Item Locator hub are visible."""
        self.item_locator.open_from_home()

        self.assertTrue(self.item_locator.get_hamburger_button().is_displayed())
        self.assertTrue(self.item_locator.get_module_title().is_displayed())
        self.assertTrue(self.item_locator.get_subtitle().is_displayed())

        assign_btn = self.item_locator.get_assign_button()
        self.assertTrue(assign_btn.is_displayed())
        self.assertTrue(assign_btn.is_enabled())

        setup_btn = self.item_locator.get_setup_button()
        self.assertTrue(setup_btn.is_displayed())
        self.assertTrue(setup_btn.is_enabled())

        self.assertTrue(self.item_locator.get_assign_title().is_displayed())
        self.assertTrue(self.item_locator.get_assign_blurb().is_displayed())
        self.assertTrue(self.item_locator.get_setup_title().is_displayed())
        self.assertTrue(self.item_locator.get_setup_blurb().is_displayed())

    @allure.epic("3. Item Locator (Moving and finding inventory)")
    @allure.feature("Setup Location navigation from hub")
    def test_setup_location_navigates(self) -> None:
        """Tap Setup Location card and verify it navigates away from hub."""
        self.item_locator.open_from_home()
        self.item_locator.tap_setup_location()
        self.assertFalse(self.item_locator.is_on_hub())
        self.item_locator.return_to_hub()
        self.assertTrue(self.item_locator.is_on_hub())

        self.item_locator.back_to_home()
        self.assertTrue(self.home.is_home_visible())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_item_locator_layout",
        "test_setup_location_navigates",
    ):
        suite.addTest(loader.loadTestsFromName(
            f"{TestItemLocatorHub.__module__}.{TestItemLocatorHub.__qualname__}.{name}"
        ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
