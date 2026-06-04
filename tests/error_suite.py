"""
Combined error-path tests — login, Retail wrong barcode, Assign wrong barcode.

Usage:
    python run_error_tests.py
    python -m unittest tests.error_suite -v
"""

from __future__ import annotations

import unittest

from tests.itemLocator.assignitem_scan_error import load_suite as load_assign_errors
from tests.item_manager.barcode_scan_error import load_suite as load_barcode_errors
from tests.login.loginerrors import load_suite as load_login_errors


def load_suite() -> unittest.TestSuite:
    """Login errors, then Retail wrong barcode, then Assign wrong barcode."""
    suite = unittest.TestSuite()
    suite.addTests(load_login_errors())
    suite.addTests(load_barcode_errors())
    suite.addTests(load_assign_errors())
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(load_suite()).wasSuccessful())
