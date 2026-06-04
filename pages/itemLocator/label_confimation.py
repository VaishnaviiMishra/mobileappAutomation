"""Verify CURRENT LABEL after re-scanning the setup-location QR label.

Runs the same entry path as setup location (Item Locator → Setup Location → scan)
and stops on **Assign location reference** (``assignReference.xml``). Does not
open Change or type in ``locationNameInput``.

Compares the **CURRENT LABEL** badge to the location chosen in the prior
``execute_full_setup_flow`` (test_09).
"""

from __future__ import annotations

from pages.common.appium_wait import wait_for_present, wait_until
from pages.itemLocator.label_location_assign import (
    SCAN_WAIT_TIMEOUT,
    LabelLocationAssignPage,
)
from pages.login.home_page import HomePage


class LabelConfimationPage:
    """Confirmation step after setup location change."""

    # Set by test_09 / execute_full_setup_flow when run in the full suite.
    expected_location_from_setup: str | None = None

    def __init__(self, driver, home: HomePage, timeout: int | None = None) -> None:
        flow_timeout = timeout or LabelLocationAssignPage.DEFAULT_FLOW_TIMEOUT
        self.driver = driver
        self.home = home
        self.setup_page = LabelLocationAssignPage(driver, home, flow_timeout)

    def scan_until_assign_reference(self, scan_timeout: float = SCAN_WAIT_TIMEOUT) -> None:
        """
        Item Locator → Setup Location → scan QR → wait for Assign location reference.
        """
        self.setup_page.open_item_locator_from_home()
        self.setup_page.tap_setup_location()
        self.setup_page.wait_for_scan(timeout=scan_timeout)
        wait_for_present(
            self.driver,
            self.setup_page._text(self.setup_page.ASSIGN_REF_TITLE),
            timeout=self.setup_page.wait.timeout,
            message="Assign location reference did not appear after scanning the label.",
        )
        wait_for_present(
            self.driver,
            self.setup_page._text(self.setup_page.CURRENT_LABEL_TEXT),
            timeout=self.setup_page.wait.timeout,
            message="CURRENT LABEL badge did not appear on Assign location reference.",
        )

    def read_current_label_badge(self) -> str:
        """Read CURRENT LABEL from the post-scan screen (assignReference.xml)."""
        return self.setup_page.get_current_label_value()

    def verify_current_label_matches(self, expected: str) -> str:
        """
        Re-scan the label, read CURRENT LABEL, and assert it matches *expected*.

        Returns the label read from the badge.
        """
        self.scan_until_assign_reference()
        actual = self.read_current_label_badge()
        expected_key = LabelLocationAssignPage._normalize_label_key(expected)
        actual_key = LabelLocationAssignPage._normalize_label_key(actual)

        if not actual:
            raise AssertionError(
                "CURRENT LABEL badge is empty after re-scanning the setup label."
            )
        if actual_key != expected_key:
            raise AssertionError(
                f"CURRENT LABEL after re-scan is {actual!r}, expected {expected!r} "
                f"(normalized {actual_key!r} vs {expected_key!r})."
            )
        return actual

    def back_to_home(self) -> None:
        self.setup_page.back_to_home()
