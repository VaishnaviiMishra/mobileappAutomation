"""Shared unittest runner with a results summary table."""

from __future__ import annotations

import time
import unittest
from typing import TextIO


class TimedTextTestResult(unittest.TextTestResult):
    """Collect per-test duration for the summary table."""

    def __init__(self, stream: TextIO, descriptions: bool, verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        self._starts: dict[str, float] = {}
        self.durations: dict[str, float] = {}

    def startTest(self, test: unittest.TestCase) -> None:
        self._starts[test.id()] = time.monotonic()
        super().startTest(test)

    def stopTest(self, test: unittest.TestCase) -> None:
        started = self._starts.pop(test.id(), time.monotonic())
        self.durations[test.id()] = time.monotonic() - started
        super().stopTest(test)


class TimedTextTestRunner(unittest.TextTestRunner):
    resultclass = TimedTextTestResult


def _status_for_test(result: unittest.TestResult, test_id: str) -> str:
    failed_ids = {t.id() for t, _ in result.failures + result.errors}
    if test_id in failed_ids:
        for t, _ in result.failures:
            if t.id() == test_id:
                return "FAIL"
        return "ERROR"
    if test_id in {t.id() for t, _ in result.skipped}:
        return "SKIP"
    return "PASS"


def print_results_table(
    result: TimedTextTestResult,
    *,
    rerun_hint: str = "python run_tests.py barcode",
) -> None:
    all_ids: list[str] = list(result.durations.keys())
    for test_case, _ in result.failures + result.errors + result.skipped:
        tid = test_case.id()
        if tid not in all_ids:
            all_ids.append(tid)

    rows: list[tuple[str, str, str, str]] = []
    for index, test_id in enumerate(all_ids, start=1):
        status = _status_for_test(result, test_id)
        seconds = result.durations.get(test_id)
        time_col = f"{seconds:.1f}s" if seconds is not None else "—"
        name = test_id.rsplit(".", 1)[-1]
        rows.append((str(index), name, status, time_col))

    if not rows:
        return

    headers = ("#", "Test", "Result", "Time")
    col_widths = [
        max(len(headers[i]), max((len(r[i]) for r in rows), default=0))
        for i in range(4)
    ]

    def _row(cells: tuple[str, ...]) -> str:
        return " | ".join(cells[i].ljust(col_widths[i]) for i in range(4))

    divider = "-+-".join("-" * w for w in col_widths)

    print()
    print("Test results")
    print(_row(headers))
    print(divider)
    for row in rows:
        print(_row(row))
    print(divider)

    passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    print(
        f"Summary: {result.testsRun} run — "
        f"{passed} passed, {len(result.failures)} failed, "
        f"{len(result.errors)} errors, {len(result.skipped)} skipped"
    )
    if result.failures or result.errors:
        print("Review failed/error rows above, then re-run a single test, e.g.:")
        print(f"  {rerun_hint}")
