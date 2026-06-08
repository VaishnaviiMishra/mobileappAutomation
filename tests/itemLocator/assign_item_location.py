"""
Assign Item Location — scan barcode, pick an available location, confirm, return home.

Supports Move item (shelf dropdown) or Change location reference (suggestion list).

Usage:
    .venv/bin/python3 -m unittest tests.itemLocator.assign_item_location -v
"""

from __future__ import annotations

import unittest

import allure

from pages.itemLocator.assign_item_location import AssignItemLocationPage
from tests.shared_session import SharedAppiumTestCase


class TestAssignItemLocation(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.assign_page = AssignItemLocationPage(cls.driver, cls.home)

    @allure.epic("3. Item Locator (Moving and finding inventory)")
    @allure.feature("Assign item location full flow (A 24 / A 54)")
    def test_assign_item_location_full_flow(self) -> None:
        """Scan item → toggle A 24 / A 54 → confirm → home."""
        item_id, chosen_location = self.assign_page.execute_full_assign_flow(timeout=90)

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
            "Home screen should be visible after completing assign item location flow.",
        )


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestAssignItemLocation.__module__}.{TestAssignItemLocation.__qualname__}"
        ".test_assign_item_location_full_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
