"""Retail Item Manager wrong-store barcode flow — barcodeerror.xml."""

from __future__ import annotations

from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_for_present
from pages.item_manager.barcode_decode import decode_barcode_from_image
from pages.item_manager.barcode_scan_page import BarcodeScanPage


class BarcodeScanErrorPage(BarcodeScanPage):
    """Page object for wrong barcode scan modal and recovery flow."""

    WRONG_BARCODE_IMAGE = Path(__file__).resolve().parent.parent / "common" / "image.png"

    WRONG_STORE_MODAL_ID = "wrongStoreModal"
    WRONG_STORE_BADGE = "Wrong store"
    WRONG_STORE_TITLE = "Item belongs to a different store"
    WRONG_STORE_MESSAGE = "This item belongs to a different store."
    WRONG_STORE_EXIT_DESC = "Scan a different item"

    def wait_for_wrong_store_modal(self) -> None:
        wait_for_present(
            self.driver,
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("{self.WRONG_STORE_MODAL_ID}")',
            ),
            timeout=self.wait.timeout,
            message="Wrong-store modal did not appear after scanning barcode.",
        )

    @property
    def wrong_store_badge(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.WRONG_STORE_BADGE}")')
        )

    @property
    def wrong_store_title(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.WRONG_STORE_TITLE}")')
        )

    @property
    def wrong_store_message(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.WRONG_STORE_MESSAGE}")')
        )

    @property
    def scan_different_item_button(self):
        return self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, self.WRONG_STORE_EXIT_DESC))

    def click_scan_different_item(self) -> None:
        self.scan_different_item_button.click()

    def complete_barcode_scan_to_wrong_store_modal(self, barcode_image: Path | None = None) -> str:
        """Submit wrong barcode and wait for wrong-store modal."""
        image = barcode_image or self.WRONG_BARCODE_IMAGE
        item_id = decode_barcode_from_image(self._barcode_image_path(image))
        self.submit_item_number(item_id)
        self.wait_for_wrong_store_modal()
        return item_id
