#!/usr/bin/env python3
"""
Run ezPawnPal Appium tests.

From the project root, with Appium listening (default http://127.0.0.1:4723) and the device connected:

  python run_tests.py              # full run — shared suite (10) + item-count standalone (6)
  python run_tests.py suite        # shared session only (tests 01–10)
  python run_tests.py barcode      # retail barcode scan (test 05)
  python run_tests.py recount      # opening jewelry recount (test 09)
  python run_tests.py item4recount # closing jewelry attempt 4 (test 10)
  python run_tests.py firearms     # firearms recount (standalone session)
  python run_tests.py premium_watch
  python run_tests.py electronics  # see --list for all short names
  python run_tests.py login        # login check only

The shared suite (tests 01–10) keeps one app session and uses the hamburger menu between tests.
Item-count recount flows (firearms, premium watch, electronics) run in separate sessions with
their own credentials — not part of the shared session.

Long refresh flows (5–15+ min each) are **not** included; use ``python run_refresh_test.py``.

Error / negative-path tests are **not** included; use ``python run_error_tests.py``.
"""

from __future__ import annotations

import argparse
import sys
import unittest

from tests.runner_utils import TimedTextTestRunner, print_results_table
from tests.test_suite import ITEM_COUNT_STANDALONE_TESTS

_SUITE_MODULE = "tests.test_suite"
_SUITE_CLASS = f"{_SUITE_MODULE}.TestEzPawnPalSuite"
_STANDALONE_ITEM_COUNT = "item_count_standalone"

_SHARED_SUITE = (_SUITE_MODULE,)
_FULL_SUITE = _SHARED_SUITE + ITEM_COUNT_STANDALONE_TESTS
_EXPAND_ALL = frozenset({"all", "everything"})
_EXPAND_SHARED = frozenset({"suite", "shared"})

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

    # Test 10
    "item4recount": f"{_SUITE_CLASS}.test_10_item_count_closing_attempt4_recount",
    "item4_recount": f"{_SUITE_CLASS}.test_10_item_count_closing_attempt4_recount",
    "closing_recount": f"{_SUITE_CLASS}.test_10_item_count_closing_attempt4_recount",
    "attempt4": f"{_SUITE_CLASS}.test_10_item_count_closing_attempt4_recount",
    "item4recount_standalone": (
        "tests.itemCount.item4recount_test.TestItem4RecountFlow"
        ".test_01_closing_jewelry_attempt4_flow"
    ),

    # Item-count standalone (own session + credentials)
    "firearms": ITEM_COUNT_STANDALONE_TESTS[0],
    "firearms_recount": ITEM_COUNT_STANDALONE_TESTS[0],
    "firearms4recount": ITEM_COUNT_STANDALONE_TESTS[1],
    "firearms_4recount": ITEM_COUNT_STANDALONE_TESTS[1],
    "opening_firearms_attempt4": ITEM_COUNT_STANDALONE_TESTS[1],
    "premium_watch": ITEM_COUNT_STANDALONE_TESTS[2],
    "premium_watch_recount": ITEM_COUNT_STANDALONE_TESTS[2],
    "pw_recount": ITEM_COUNT_STANDALONE_TESTS[2],
    "premium_watch4recount": ITEM_COUNT_STANDALONE_TESTS[3],
    "premium_watch4": ITEM_COUNT_STANDALONE_TESTS[3],
    "pw4recount": ITEM_COUNT_STANDALONE_TESTS[3],
    "electronics": ITEM_COUNT_STANDALONE_TESTS[4],
    "electronics_recount": ITEM_COUNT_STANDALONE_TESTS[4],
    "elec_recount": ITEM_COUNT_STANDALONE_TESTS[4],
    "electronics4recount": ITEM_COUNT_STANDALONE_TESTS[5],
    "electronics4": ITEM_COUNT_STANDALONE_TESTS[5],
    "elec4recount": ITEM_COUNT_STANDALONE_TESTS[5],
    
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
    _STANDALONE_ITEM_COUNT: ITEM_COUNT_STANDALONE_TESTS,
    "item_count_recount": ITEM_COUNT_STANDALONE_TESTS,
}

_DEFAULT_ORDER = _FULL_SUITE


def _resolve_names(args: list[str]) -> tuple[str, ...]:
    names: list[str] = []
    for arg in args:
        key = arg.strip()
        if key in _EXPAND_ALL:
            names.extend(_FULL_SUITE)
            continue
        if key in _EXPAND_SHARED:
            names.extend(_SHARED_SUITE)
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
        print("Default: shared suite + item-count standalone flows")
        print(f"  {_SUITE_MODULE}")
        for name in ITEM_COUNT_STANDALONE_TESTS:
            print(f"  {name}")
        print("Shared session only: suite")
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