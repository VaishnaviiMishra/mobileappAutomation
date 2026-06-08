"""
Pytest hooks shared by ``run_all_allure.py`` and direct ``pytest`` invocations.

Ensures ``TestEzPawnPalSuite`` runs in the same order as ``tests.test_suite.load_suite()``.
"""

from __future__ import annotations


def pytest_collection_modifyitems(config, items) -> None:
    """Keep main-suite tests in load_suite() order (login → … → closing attempt 4)."""
    try:
        from tests.test_suite import TestEzPawnPalSuite, load_suite
    except ImportError:
        return

    ordered_names: list[str] = []

    def _walk(suite) -> None:
        for entry in suite:
            if hasattr(entry, "_tests"):
                _walk(entry)
            else:
                ordered_names.append(entry.id().split(".")[-1])

    _walk(load_suite())
    order_index = {name: idx for idx, name in enumerate(ordered_names)}

    def _is_main_suite(item) -> bool:
        cls = getattr(item, "cls", None)
        return (
            cls is not None
            and cls.__module__ == TestEzPawnPalSuite.__module__
            and cls.__qualname__ == TestEzPawnPalSuite.__qualname__
        )

    suite_items = [item for item in items if _is_main_suite(item)]
    other_items = [item for item in items if not _is_main_suite(item)]

    suite_items.sort(
        key=lambda item: order_index.get(item.name, len(order_index)),
    )
    items[:] = suite_items + other_items
