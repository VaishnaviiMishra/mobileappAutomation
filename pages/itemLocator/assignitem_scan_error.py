"""Assign Item Location wrong barcode flow — wrong-store modal and recovery."""

from __future__ import annotations

from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_for_present
from pages.itemLocator.assign_item_location import AssignItemLocationPage


class AssignItemScanErrorPage(AssignItemLocationPage):
    """Page object for wrong barcode scan during Assign Item Location."""

    WRONG_BARCODE_IMAGE = Path(__file__).resolve().parent.parent / "common" / "image.png"

    WRONG_STORE_MODAL_ID = "wrongStoreModal"
    WRONG_STORE_BADGE = "Wrong store"
    WRONG_STORE_TITLE = "Item belongs to a different store"
    WRONG_STORE_MESSAGE = (
        "This item belongs to a different store. You cannot update its location."
    )
    WRONG_STORE_EXIT_DESC = "Scan a different item"

    def _text_contains(self, fragment: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{fragment}")',
        )

    def wait_for_wrong_store_modal(self) -> None:
        wait_for_present(
            self.driver,
            self._resource(self.WRONG_STORE_MODAL_ID),
            timeout=self.wait.timeout,
            message="Wrong-store modal did not appear after confirming scanned barcode.",
        )

    @property
    def wrong_store_badge(self):
        return self.wait.until_present(self._text(self.WRONG_STORE_BADGE))

    @property
    def wrong_store_title(self):
        return self.wait.until_present(self._text(self.WRONG_STORE_TITLE))

    @property
    def wrong_store_message(self):
        return self.wait.until_present(
            self._text_contains("You cannot update its location")
        )

    @property
    def scan_different_item_button(self):
        return self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, self.WRONG_STORE_EXIT_DESC))

    def click_scan_different_item(self) -> None:
        self.scan_different_item_button.click()

    def wait_for_assign_scan_screen(self) -> None:
        wait_for_present(
            self.driver,
            self._text(self.SCAN_HEADING),
            timeout=self.wait.timeout,
            message="Assign Item Location scan screen did not reappear after wrong-store modal.",
        )
        wait_for_present(
            self.driver,
            self._resource(self.ITEM_NUMBER_INPUT_ID),
            timeout=self.wait.timeout,
            message="Item number field not visible on Assign Item Location scan screen.",
        )

    def complete_assign_scan_to_wrong_store_modal(self, barcode_image: Path | None = None) -> str:
        """Item Locator -> Assign -> wrong scan -> Confirm -> wrong-store modal."""
        self.open_item_locator_from_home()
        self.tap_assign_item_location()
        item_id = self.scan_and_enter_item_number(barcode_image or self.WRONG_BARCODE_IMAGE)
        self._dismiss_keyboard()
        self.wait.until_present(self._resource(self.CONFIRM_BUTTON_ID)).click()
        self.wait_for_wrong_store_modal()
        return item_id
