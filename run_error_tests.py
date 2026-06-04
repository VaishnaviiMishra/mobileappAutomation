#!/usr/bin/env python3
"""
Run all validation / error-path Appium tests.

Not included in ``run_tests.py`` (negative flows use invalid credentials or barcodes).

From the project root, with Appium running and the device connected:

  python run_error_tests.py              # all error tests
  python run_error_tests.py login        # login errors only
  python run_error_tests.py barcode      # Retail wrong barcode only
  python run_error_tests.py assign       # Assign Item Location wrong barcode only
  python run_error_tests.py --list
"""

from __future__ import annotations

import argparse
import sys
import unittest

from tests.runner_utils import TimedTextTestRunner, print_results_table

_ERROR_SUITE_MODULE = "tests.error_suite"

_ALIASES: dict[str, str] = {
    "errors": _ERROR_SUITE_MODULE,
    "error": _ERROR_SUITE_MODULE,
    "all": _ERROR_SUITE_MODULE,
    "login": "tests.login.loginerrors",
    "login_errors": "tests.login.loginerrors",
    "loginerrors": "tests.login.loginerrors",
    "barcode": "tests.item_manager.barcode_scan_error",
    "barcode_error": "tests.item_manager.barcode_scan_error",
    "wrong_barcode": "tests.item_manager.barcode_scan_error",
    "retail_error": "tests.item_manager.barcode_scan_error",
    "assign": "tests.itemLocator.assignitem_scan_error",
    "assign_error": "tests.itemLocator.assignitem_scan_error",
    "assignitem": "tests.itemLocator.assignitem_scan_error",
    "assignitem_error": "tests.itemLocator.assignitem_scan_error",
}


def _resolve_names(args: list[str]) -> tuple[str, ...]:
    if not args:
        return (_ERROR_SUITE_MODULE,)
    names: list[str] = []
    for arg in args:
        key = arg.strip()
        if key in _ALIASES:
            names.append(_ALIASES[key])
            continue
        if key.startswith("tests."):
            names.append(key)
            continue
        raise KeyError(key)
    return tuple(names)


def _build_suite(dotted_names: tuple[str, ...]) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in dotted_names:
        if name == _ERROR_SUITE_MODULE:
            from tests.error_suite import load_suite

            suite.addTests(load_suite())
        elif name == "tests.login.loginerrors":
            from tests.login.loginerrors import load_suite

            suite.addTests(load_suite())
        elif name == "tests.item_manager.barcode_scan_error":
            from tests.item_manager.barcode_scan_error import load_suite

            suite.addTests(load_suite())
        elif name == "tests.itemLocator.assignitem_scan_error":
            from tests.itemLocator.assignitem_scan_error import load_suite

            suite.addTests(load_suite())
        else:
            suite.addTests(loader.loadTestsFromName(name))
    return suite


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tests",
        nargs="*",
        metavar="NAME",
        help="login, barcode, assign, or omit for all error tests",
    )
    parser.add_argument("--list", action="store_true", help="Print known short names and exit.")
    args = parser.parse_args()

    if args.list:
        print("Error test commands:")
        for k in sorted(_ALIASES.keys()):
            print(f"  {k} -> {_ALIASES[k]}")
        print("Default: all error tests (login + retail barcode + assign barcode)")
        return 0

    try:
        dotted = _resolve_names(list(args.tests))
    except KeyError as e:
        print(f"Unknown test {e.args[0]!r}. Use --list.", file=sys.stderr)
        return 2

    print(
        "Running error-path tests (excluded from run_tests.py). "
        "Each module may start its own Appium session.\n"
    )
    runner = TimedTextTestRunner(verbosity=2)
    result = runner.run(_build_suite(dotted))
    print_results_table(result, rerun_hint="python run_error_tests.py login")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
