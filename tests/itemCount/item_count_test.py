"""
Item Count — hub layout and Manage jewelry cases flow.

Primary flow: Manage jewelry cases → + → Save and finish → back on Today's Counts.

Usage:
    .venv/bin/python3 -m unittest tests.itemCount.item_count_test -v
"""

from __future__ import annotations

import unittest

from pages.itemCount.item_count_page import ItemCountPage
from tests.shared_session import SharedAppiumTestCase


class TestItemCount(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.item_count = ItemCountPage(cls.driver, cls.home)

    def test_item_count_layout(self) -> None:
        """Verify Today's Counts hub chrome and footer actions."""
        self.item_count.open_from_home()
        snapshot = self.item_count.verify_hub_layout()

        self.assertTrue(self.item_count.get_hamburger_button().is_displayed())
        self.assertTrue(self.item_count.get_module_title().is_displayed())
        self.assertTrue(self.item_count.get_page_title().is_displayed())
        self.assertTrue(self.item_count.get_instruction().is_displayed())

        sections: list[str] = snapshot["sections"]  # type: ignore[assignment]
        self.assertGreaterEqual(len(sections), 1)

        start_btn = self.item_count.get_footer_button(ItemCountPage.START_COUNT_DESC)
        self.assertTrue(start_btn.is_displayed())
        self.assertTrue(start_btn.is_enabled())

        if snapshot.get("has_footer_exit"):  # type: ignore[union-attr]
            exit_btn = self.item_count.get_footer_button(ItemCountPage.EXIT_DESC)
            self.assertTrue(exit_btn.is_displayed())
            self.assertTrue(exit_btn.is_enabled())

    def test_item_count_manage_jewelry_cases(self) -> None:
        """
        Manage jewelry cases → tap + → Save and finish → return to Item Count hub.
        """
        self.item_count.open_from_home()
        if not self.item_count.has_manage_jewelry_cases_link():
            self.skipTest("Manage jewelry cases link not shown on this store layout.")

        self.item_count.ensure_hub_footer_visible()
        new_count = self.item_count.complete_manage_jewelry_cases_flow()

        self.assertTrue(self.item_count.is_on_hub_screen())
        self.assertGreater(new_count, 0)
        self.assertTrue(self.item_count.get_page_title().is_displayed())


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in (
        "test_item_count_layout",
        "test_item_count_manage_jewelry_cases",
    ):
        suite.addTest(loader.loadTestsFromName(
            f"{TestItemCount.__module__}.{TestItemCount.__qualname__}.{name}"
        ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
