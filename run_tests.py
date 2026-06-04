#!/usr/bin/env python3
"""
Run ezPawnPal Appium tests.

From the project root, with Appium listening (default http://127.0.0.1:4723) and the device connected:

  python run_tests.py              # full suite — 9 tests, one session, results table
  python run_tests.py barcode      # retail barcode scan (test 05)
  python run_tests.py recount      # jewelry recount only (test 09)
  python run_tests.py login        # login check only

The default suite keeps the app open and uses the hamburger menu between tests.
Tests 01–09: login → home → item count → locator → barcode → assign → setup → label → recount.

Long refresh flows (5–15+ min each) are **not** included; use ``python run_refresh_test.py``.

Error / negative-path tests are **not** included; use ``python run_error_tests.py``.
"""

from __future__ import annotations

import argparse
import sys
import unittest

from tests.runner_utils import TimedTextTestRunner, print_results_table

_SUITE_MODULE = "tests.test_suite"
_SUITE_CLASS = f"{_SUITE_MODULE}.TestEzPawnPalSuite"

_FULL_SUITE = (_SUITE_MODULE,)
_EXPAND_ALL = frozenset({"all", "suite", "everything"})

_ALIASES: dict[str, str] = {
    # Test 05
    "flow": f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    "barcode": f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    "barcode_scan": f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    "test_barcode_scan": f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    "retail_item_manager": f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    "RETAIL_ITEM_MANAGER": f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    
    # Error Barcodes (External)
    "barcode_error": "tests.item_manager.barcode_scan_error.TestBarcodeScanError.test_retail_wrong_store_barcode_flow",
    "wrong_barcode": "tests.item_manager.barcode_scan_error.TestBarcodeScanError.test_retail_wrong_store_barcode_flow",
    
    # Test 03
    "item_count": f"{_SUITE_CLASS}.test_03_item_count_layout_and_buttons",
    
    # Test 04
    "item_locater": f"{_SUITE_CLASS}.test_04_item_locator_layout_and_buttons",
    "item_locator": f"{_SUITE_CLASS}.test_04_item_locator_layout_and_buttons",
    
    # Test 06
    "assign_location": f"{_SUITE_CLASS}.test_06_assign_item_location",
    "assign_item_location": f"{_SUITE_CLASS}.test_06_assign_item_location",
    
    # Test 07
    "setup_location": f"{_SUITE_CLASS}.test_07_setup_location_change",
    "label_location_assign": f"{_SUITE_CLASS}.test_07_setup_location_change",
    
    # Test 08
    "label_confimation": f"{_SUITE_CLASS}.test_08_label_confimation",
    "label_confirmation": f"{_SUITE_CLASS}.test_08_label_confimation",
    
    # Test 09
    "recount": f"{_SUITE_CLASS}.test_09_item_count_jewelry_recount",
    "jewelry": f"{_SUITE_CLASS}.test_09_item_count_jewelry_recount",
    "item_recount": f"{_SUITE_CLASS}.test_09_item_count_jewelry_recount",
    "itemrecount": f"{_SUITE_CLASS}.test_09_item_count_jewelry_recount",
    "jewelry_recount": f"{_SUITE_CLASS}.test_09_item_count_jewelry_recount",
    
    # Test 01
    "login": f"{_SUITE_CLASS}.test_01_login_and_store_location_setup",
    "test_login": f"{_SUITE_CLASS}.test_01_login_and_store_location_setup",
    
    # Test 02
    "home": f"{_SUITE_CLASS}.test_02_post_login_home_or_data_sync",
    "test_home": f"{_SUITE_CLASS}.test_02_post_login_home_or_data_sync",
}

_MULTI_ALIASES: dict[str, tuple[str, ...]] = {
    "item_manager": (
        f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    ),
    "test_item_manager": (
        f"{_SUITE_CLASS}.test_05_retail_item_manager_live_barcode_scan",
    ),
}

_DEFAULT_ORDER = _FULL_SUITE


def _resolve_names(args: list[str]) -> tuple[str, ...]:
    names: list[str] = []
    for arg in args:
        key = arg.strip()
        if key in _EXPAND_ALL:
            names.extend(_FULL_SUITE)
            continue
        if key in _MULTI_ALIASES:
            names.extend(_MULTI_ALIASES[key])
            continue
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
        if name == _SUITE_MODULE:
            from tests.test_suite import load_suite

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
        help="Short names: barcode, login, item_count, all (default: full suite), …",
    )
    parser.add_argument("--list", action="store_true", help="Print known short names and exit.")
    args = parser.parse_args()

    if args.list:
        print("Short names -> test(s)")
        for k in sorted(set(_ALIASES) | set(_MULTI_ALIASES)):
            target = _MULTI_ALIASES.get(k) or (_ALIASES[k],)
            for t in target:
                print(f"  {k} -> {t}")
        print("Default: full suite (one session)")
        print(f"  {_SUITE_MODULE}")
        return 0

    if not args.tests:
        dotted = _DEFAULT_ORDER
    else:
        try:
            dotted = _resolve_names(list(args.tests))
        except KeyError as e:
            print(
                f"Unknown test {e.args[0]!r}. Use --list or a dotted name like "
                f"{_SUITE_CLASS}.test_03_item_count_layout_and_buttons.",
                file=sys.stderr,
            )
            return 2

    runner = TimedTextTestRunner(verbosity=2)
    result = runner.run(_build_suite(dotted))
    print_results_table(result)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())