"""Poll-based waits using the Appium driver only — no selenium imports."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class AppiumWaitTimeout(Exception):
    """Raised when a condition is not met within the allotted time."""


def _first_displayed(driver, by: str, value: str) -> Any | None:
    for el in driver.find_elements(by, value):
        try:
            if el.is_displayed():
                return el
        except Exception:
            continue
    return None


def wait_for_present(
    driver,
    locator: tuple[str, str],
    *,
    timeout: float,
    poll: float = 0.25,
    message: str | None = None,
) -> Any:
    by, value = locator
    end = time.time() + timeout
    last: BaseException | None = None
    while time.time() < end:
        try:
            el = _first_displayed(driver, by, value)
            if el is not None:
                return el
        except Exception as e:
            last = e
        time.sleep(poll)
    msg = message or f"Element not found within {timeout}s: {locator!r}"
    if last:
        raise AppiumWaitTimeout(f"{msg} (last error: {last!r})") from last
    raise AppiumWaitTimeout(msg)


def wait_for_clickable(
    driver,
    locator: tuple[str, str],
    *,
    timeout: float,
    poll: float = 0.25,
    message: str | None = None,
) -> Any:
    by, value = locator
    end = time.time() + timeout
    last: BaseException | None = None
    while time.time() < end:
        try:
            for el in driver.find_elements(by, value):
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except Exception as e:
                    last = e
                    continue
        except Exception as e:
            last = e
        time.sleep(poll)
    msg = message or f"Element not clickable within {timeout}s: {locator!r}"
    if last:
        raise AppiumWaitTimeout(f"{msg} (last error: {last!r})") from last
    raise AppiumWaitTimeout(msg)


def wait_until(
    driver,
    condition: Callable[[], T | None],
    *,
    timeout: float,
    poll: float = 0.25,
    message: str = "Timed out waiting for condition",
) -> T:
    end = time.time() + timeout
    last: BaseException | None = None
    while time.time() < end:
        try:
            out = condition()
            if out is not None:
                return out
        except Exception as e:
            last = e
        time.sleep(poll)
    if last:
        raise AppiumWaitTimeout(f"{message}: {last!r}") from last
    raise AppiumWaitTimeout(message)


class AppiumWait:
    """Fluent-style waiter bound to default timeout and poll interval."""

    def __init__(self, driver, timeout: float = 20.0, poll: float = 0.25) -> None:
        self.driver = driver
        self.timeout = timeout
        self.poll = poll

    def until_present(self, locator: tuple[str, str], *, message: str | None = None) -> Any:
        return wait_for_present(
            self.driver,
            locator,
            timeout=self.timeout,
            poll=self.poll,
            message=message,
        )

    def until_clickable(self, locator: tuple[str, str], *, message: str | None = None) -> Any:
        return wait_for_clickable(
            self.driver,
            locator,
            timeout=self.timeout,
            poll=self.poll,
            message=message,
        )
