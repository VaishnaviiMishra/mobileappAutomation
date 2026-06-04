"""
Setup Location — full end-to-end: scan label, change reference, confirm, go home.

The test opens the QR label image full-screen on the host monitor so the device
camera can scan it, then walks through the entire Setup Location flow:
    scan → assign reference → change → pick location → confirm → home.

Usage:
    .venv/bin/python3 -m unittest tests.itemLocator.label_location_assign -v
"""

from __future__ import annotations

import unittest

from pages.itemLocator.label_location_assign import LabelLocationAssignPage
from tests.shared_session import SharedAppiumTestCase


class TestLabelLocationAssign(SharedAppiumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.label_page = LabelLocationAssignPage(cls.driver, cls.home)

    def test_setup_location_full_flow(self) -> None:
        """End-to-end: Item Locator → Setup Location → scan QR →
        Change → pick location → Confirm → Confirm popup → Go to Home."""
        chosen = self.label_page.execute_full_setup_flow()
        self.assertTrue(
            self.home.is_home_visible(),
            "Home screen should be visible after completing Setup Location flow.",
        )
        self.assertTrue(
            len(chosen) > 0,
            "A location should have been selected during the flow.",
        )


def load_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromName(
        f"{TestLabelLocationAssign.__module__}.{TestLabelLocationAssign.__qualname__}"
        ".test_setup_location_full_flow"
    ))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
