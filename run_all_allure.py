#!/usr/bin/env python3
"""
Run ALL ezPawnPal Appium suites with a combined Allure report.

Execution order (matches ``run_all.py``):
  1. tests/test_suite.py          — shared flow, one session, 10 tests (login → closing attempt 4)
  2. tests/itemCount/*_test.py    — item-count standalone flows (own session each)
  3. tests/login/loginerrors.py   — login error paths
  4. tests/item_manager/barcode_scan_error.py
  5. tests/itemLocator/assignitem_scan_error.py
  6. tests/refresh_data/refresh_data.py — long sync flows (5–15+ min each)

Prerequisites:
  - Appium server: http://127.0.0.1:4723
  - Device connected (``adb devices``)
  - ``pip install pytest allure-pytest``

Usage:
  python run_all_allure.py
  allure serve ./allure-results
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Same grouping as run_all.py — main suite first, then errors, then refresh.
TEST_MODULES = [
    "tests/test_suite.py",
    "tests/itemCount/firearms_test.py",
    "tests/itemCount/firearms4recount_test.py",
    "tests/itemCount/premium_watch_test.py",
    "tests/itemCount/premium_watch4recount_test.py",
    "tests/itemCount/electronics_test.py",
    "tests/itemCount/electronics4recount_test.py",
    "tests/login/loginerrors.py",
    "tests/item_manager/barcode_scan_error.py",
    "tests/itemLocator/assignitem_scan_error.py",
    "tests/refresh_data/refresh_data.py",
]


def _check_dependencies() -> int | None:
    try:
        import pytest  # noqa: F401
        import allure_pytest  # noqa: F401
    except ImportError:
        print(
            "Missing pytest or allure-pytest. Install with:\n"
            "  pip install pytest allure-pytest",
            file=sys.stderr,
        )
        return 1
    return None


def main() -> int:
    if (err := _check_dependencies()) is not None:
        return err

    command = [
        sys.executable,
        "-m",
        "pytest",
        *TEST_MODULES,
        "--alluredir=./allure-results",
        "--clean-alluredir",
        "-v",
    ]

    print("=" * 50)
    print("Running ALL suites (Allure report)")
    print("=" * 50)
    print("Modules (in order):")
    for path in TEST_MODULES:
        print(f"  - {path}")
    print()
    print("Ensure Appium is running: appium  (default http://127.0.0.1:4723)")
    print("=" * 50)
    print()

    result = subprocess.run(command, cwd=PROJECT_ROOT)

    print()
    print("=" * 50)
    if result.returncode == 0:
        print("All pytest modules finished successfully.")
    else:
        print("Some tests failed or errored — see output above.")
    print("View report:  allure serve ./allure-results")
    print("=" * 50)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
