#!/usr/bin/env python3
"""
Run long refresh-data tests (Product MDM and Item Locations).

Not included in ``run_tests.py`` (each sync can take 5–15+ minutes).

From the project root, with Appium running and the device connected:

  python run_refresh_test.py              # menu UI + MDM + Item Locations refresh
  python run_refresh_test.py menu         # account menu UI only
  python run_refresh_test.py mdm          # Product MDM refresh only
  python run_refresh_test.py locations    # Item Locations refresh only

Override sync wait (seconds):

  EZPAWNPAL_MDM_REFRESH_TIMEOUT=1200 python run_refresh_test.py mdm
  EZPAWNPAL_LOCATIONS_REFRESH_TIMEOUT=1200 python run_refresh_test.py locations
"""

from __future__ import annotations

import argparse
import sys
import unittest

from tests.runner_utils import TimedTextTestRunner, print_results_table

_REFRESH_MODULE = "tests.refresh_data.refresh_data"
_REFRESH_CLASS = f"{_REFRESH_MODULE}.TestRefreshData"

_ALIASES: dict[str, str] = {
    "refresh": _REFRESH_MODULE,
    "refresh_data": _REFRESH_MODULE,
    "mdm": f"{_REFRESH_CLASS}.test_02_refresh_product_mdm_data_flow",
    "mdm_refresh": f"{_REFRESH_CLASS}.test_02_refresh_product_mdm_data_flow",
    "locations": f"{_REFRESH_CLASS}.test_03_refresh_item_locations_data_flow",
    "item_locations": f"{_REFRESH_CLASS}.test_03_refresh_item_locations_data_flow",
    "locations_refresh": f"{_REFRESH_CLASS}.test_03_refresh_item_locations_data_flow",
    "menu": f"{_REFRESH_CLASS}.test_01_account_menu_ui",
    "account": f"{_REFRESH_CLASS}.test_01_account_menu_ui",
    "account_menu": f"{_REFRESH_CLASS}.test_01_account_menu_ui",
}


def _resolve_names(args: list[str]) -> tuple[str, ...]:
    if not args:
        return (_REFRESH_MODULE,)
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
        if name == _REFRESH_MODULE:
            from tests.refresh_data.refresh_data import load_suite

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
        help="menu, mdm, locations, or omit for all three tests",
    )
    parser.add_argument("--list", action="store_true", help="Print known short names and exit.")
    args = parser.parse_args()

    if args.list:
        print("Refresh test commands:")
        for k in sorted(_ALIASES.keys()):
            print(f"  {k} -> {_ALIASES[k]}")
        print("Default: full refresh module (menu + MDM + Item Locations)")
        return 0

    try:
        dotted = _resolve_names(list(args.tests))
    except KeyError as e:
        print(f"Unknown test {e.args[0]!r}. Use --list.", file=sys.stderr)
        return 2

    print(
        "Running refresh tests (excluded from run_tests.py). "
        "Each sync may take 5–15+ minutes.\n"
    )
    runner = TimedTextTestRunner(verbosity=2)
    result = runner.run(_build_suite(dotted))
    print_results_table(result, rerun_hint="python run_refresh_test.py locations")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
