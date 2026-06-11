#!/usr/bin/env python3
"""
Run all ezPawnPal Appium test suites sequentially (unittest runners + results tables).

Executes in order:
  1. run_tests.py         — shared suite (10 tests, one session) + item-count standalone (6)
  2. run_error_tests.py   — login / barcode / assign error flows
  3. run_refresh_test.py  — long refresh-data flows (5–15+ min each)

For a combined Allure HTML report, use ``python run_all_allure.py`` instead.

Prerequisites:
  - Appium server: http://127.0.0.1:4723
  - Device connected
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

SCRIPTS = (
    ("Main + item-count standalone", "run_tests.py"),
    ("Error-path tests", "run_error_tests.py"),
    ("Refresh-data tests", "run_refresh_test.py"),
)


def main() -> int:
    overall_success = True

    print("=" * 50)
    print("STARTING MASTER TEST EXECUTION")
    print("=" * 50)
    print("Ensure Appium is running: appium  (default http://127.0.0.1:4723)")
    print()

    for label, script in SCRIPTS:
        print(f"\n---> {label}: {script} <---")
        print("-" * 50)

        result = subprocess.run([sys.executable, script], cwd=PROJECT_ROOT)

        if result.returncode != 0:
            print(f"\n{script} encountered failures or errors.")
            overall_success = False
        else:
            print(f"\n{script} completed successfully.")

        print("-" * 50)

    print()
    print("=" * 50)
    if overall_success:
        print("ALL TEST SUITES PASSED SUCCESSFULLY!")
        return 0
    print("SOME TEST SUITES FAILED. Check the logs above.")
    print("For Allure HTML report:  python run_all_allure.py")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
