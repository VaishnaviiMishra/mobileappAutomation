"""Retail Item Manager barcode scan — menu.xml & retailitem.xml."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / ".cursor" / "debug-c68c63.log"

from appium.webdriver.common.appiumby import AppiumBy

from pages.common import adb_helper
from pages.common.appium_wait import AppiumWait, AppiumWaitTimeout, wait_for_present, wait_until
from pages.item_manager.barcode_decode import decode_barcode_from_image
from pages.login.home_page import HomePage


class BarcodeScanPage:
    APP_PACKAGE = "com.ezpawnpal"
    # Other store; needs a different employee login — not used in active retail tests yet.
    STORE_14401_ITEM_ID = "144010051344"
    EXPECTED_BARCODE = STORE_14401_ITEM_ID
    ACTIVE_RETAIL_ITEM_ID = STORE_14401_ITEM_ID

    MODULE_TITLE = "Retail Item Manager"
    MENU_RETAIL_ITEM = MODULE_TITLE
    SCAN_HEADING = "Scan item barcode"
    SCAN_PREVIEW_ID = "scanButton"
    SCREEN_SUBTITLE = "Edit item details or view discounts"
    MANUAL_ENTRY_HINT = "Enter item number instead"
    ITEM_NUMBER_LABEL = "Item number"
    CONFIRM_BUTTON_DESC = "Confirm"
    ITEM_EZ_ID_RESOURCE_ID = "ezIdInput"

    # item_details.xml — screen after Confirm on scan
    ITEM_MANAGEMENT_HEADING = "Item management"
    ITEM_DETAILS_HEADING = "Item details"
    FIELD_EZ_ID = "fieldEzId"
    STONES_SECTION_ID = "stonesSection"
    STONE_CARD_ID = "stoneCard-0"
    DISCOUNT_SECTION_ID = "discountSection"
    DISCOUNT_TITLE = "Adjusted price based on discount"
    AGE_LABEL_PREFIX = "Age:"
    STONES_HEADING = "Stones"
    DISCOUNT_TABLE_HEADERS = ("RANGE", "DISC.", "PRICE")
    DISCOUNT_ROW_LABELS = (
        "ALLOWABLE DISCOUNT",
        "STARTING RANGE",
        "UPPER RANGE",
    )
    CORE_ITEM_DETAIL_LABELS = (
        "Item number",
        "Price",
        "Category",
        "Weight (in grams)",
        "Material Type",
        "Pendant Description",
    )
    SILVER_ITEM_DETAIL_LABELS = ("Quality",)
    GOLD_ITEM_DETAIL_LABELS = ("Color", "Karat")
    ALL_ITEM_DETAIL_LABELS = (
        *CORE_ITEM_DETAIL_LABELS,
        *SILVER_ITEM_DETAIL_LABELS,
        *GOLD_ITEM_DETAIL_LABELS,
    )
    STONE_FIELD_LABELS = ("Color / Type", "Quality", "Shape", "Size (in points)")
    EDIT_BUTTON_DESC = "Edit"
    EDIT_BUTTON_ID = "editButton"
    EDIT_ITEM_HEADING = "Edit item details"
    EDIT_ITEM_NUMBER_DESC = "Item #"
    UPDATE_AND_PRINT_DESC = "Update and print tag"
    UPDATE_AND_PRINT_ID = "updateAndPrintButton"
    STONE_COLOR_FIELD_ID = "stoneColor-0"
    STONE_COLOR_MODAL_ID = "stoneColor-0-modal"
    STONE_COLOR_DROPDOWN_CARET = "▾"
    ITEM_UPDATED_TITLE = "Item Updated!"
    SAVED_SUCCESS_MESSAGE = "Your changes have been saved successfully."
    TAG_SENT_SUCCESS_MESSAGE = "Your tag has been sent to the printer successfully."
    SUCCESS_VIEW_ID = "successView"
    SCAN_ANOTHER_ITEM_DESC = "Scan another item"
    GO_HOME_DESC = "Go to Home"
    GO_HOME_BUTTON_ID = "closeButton"
    SCAN_ANOTHER_BUTTON_ID = "scanAnotherButton"
    ITEM_UPDATE_SUCCESS_TIMEOUT = 60.0
    PRINTER_MEDIA_HINT = "Ensure the correct media is prepared in the printer."
    PRINT_TAG_DESC = "Print tag"
    REPRINT_BUTTON_ID = "reprintButton"

    DEFAULT_BARCODE_IMAGE = (
        Path(__file__).resolve().parent.parent / "common" / "barcode_14401.png"
    )
    STORE_14401_BARCODE_IMAGE = DEFAULT_BARCODE_IMAGE

    ITEM_DETAILS_LOAD_TIMEOUT = 45.0
    ITEM_DETAILS_SETTLE_SECONDS = 3.0
    ITEM_DETAILS_MAX_SCROLL_SWIPES = 12
    ITEM_DETAILS_SCROLL_PAUSE_SECONDS = 0.35

    _FIELD_HINTS = frozenset({"Item number"})
    _FIELD_LABELS = frozenset({"Item number", "Item EZ ID"})

    def __init__(self, driver, home: HomePage, timeout: int = 25) -> None:
        self.driver = driver
        self.home = home
        self.wait = AppiumWait(driver, float(timeout))

    # region agent log
    def _debug_log(self, hypothesis_id: str, message: str, data: dict | None = None) -> None:
        try:
            entry = {
                "sessionId": "c68c63",
                "hypothesisId": hypothesis_id,
                "location": "barcode_scan_page",
                "message": message,
                "data": data or {},
                "timestamp": int(time.time() * 1000),
            }
            with _DEBUG_LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    # endregion

    # ---------- Navigation (menu.xml) ----------
    def open_navigation_menu(self) -> None:
        self.home.hamburger_button.click()
        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, self.MENU_RETAIL_ITEM),
            timeout=self.wait.timeout,
            message="Navigation drawer did not open (Retail Item Manager not found).",
        )

    def select_retail_item_manager(self) -> None:
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, self.MENU_RETAIL_ITEM).click()
        self.wait_for_retail_scan_screen()

    def navigate_to_retail_item_manager_via_menu(self) -> None:
        """Hamburger → Retail Item Manager (retailitem.xml)."""
        self.open_navigation_menu()
        self.select_retail_item_manager()

    def open_from_home(self) -> None:
        """Home MODULES tile → Retail Item Manager (retailitem.xml)."""
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.wait_for_post_login_screen()
        self.home.retail_item_manager_module.click()
        self.wait_for_retail_scan_screen()

    # ---------- Retail scan screen (retailitem.xml) ----------
    def wait_for_retail_scan_screen(self) -> None:
        wait_for_present(
            self.driver,
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.SCAN_HEADING}")'),
            timeout=self.wait.timeout,
            message="Retail Item Manager scan screen did not appear.",
        )

    @property
    def page_title(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.MODULE_TITLE}")')
        )

    @property
    def scan_heading(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.SCAN_HEADING}")')
        )

    @property
    def scan_preview(self):
        return self.wait.until_present(
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("{self.SCAN_PREVIEW_ID}")',
            )
        )

    @property
    def screen_subtitle(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.SCREEN_SUBTITLE}")')
        )

    @property
    def manual_entry_hint(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.MANUAL_ENTRY_HINT}")')
        )

    @property
    def item_number_label(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.ITEM_NUMBER_LABEL}")')
        )

    def _item_ez_id_locators(self) -> list[tuple]:
        return [
            (AppiumBy.ACCESSIBILITY_ID, "Item EZ ID"),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("{self.ITEM_EZ_ID_RESOURCE_ID}")',
            ),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Item EZ ID")'),
        ]

    def item_ez_id_input(self):
        last_error: Exception | None = None
        for locator in self._item_ez_id_locators():
            try:
                return self.wait.until_present(locator)
            except Exception as exc:
                last_error = exc
        raise AppiumWaitTimeout(f"Item EZ ID field not found. Last error: {last_error}")

    @property
    def confirm_button(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.CONFIRM_BUTTON_DESC))

    # --- Actions ---

    def open_hamburger_from_scan(self) -> None:
        self.home.hamburger_button.click()
        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, self.MENU_RETAIL_ITEM),
            timeout=self.wait.timeout,
            message="Navigation drawer did not open from Retail Item Manager.",
        )

    def close_hamburger(self) -> None:
        self.driver.press_keycode(4)

    def tap_profile(self) -> None:
        self.home.profile_button.click()
        time.sleep(0.5)
        self.driver.press_keycode(4)

    def tap_scan_preview(self) -> None:
        self.scan_preview.click()

    def tap_item_field(self) -> None:
        self.item_ez_id_input().click()

    def tap_confirm(self) -> None:
        self.confirm_button.click()

    def wait_still_on_scan_screen(self) -> None:
        wait_for_present(
            self.driver,
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.SCAN_HEADING}")'),
            timeout=self.wait.timeout,
            message="Retail scan screen closed unexpectedly.",
        )

    @classmethod
    def _read_field_text(cls, element: Any) -> str:
        text = (element.text or "").strip()
        if text and text not in cls._FIELD_HINTS and text not in cls._FIELD_LABELS:
            return text
        for attr in ("text", "value", "content-desc"):
            try:
                value = (element.get_attribute(attr) or "").strip()
            except Exception:
                value = ""
            if value and value not in cls._FIELD_HINTS and value not in cls._FIELD_LABELS:
                return value
        return ""

    def _read_item_ez_id_value(self) -> str:
        return self._read_field_text(self.item_ez_id_input())

    def _dismiss_keyboard_if_visible(self) -> None:
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            try:
                self.driver.press_keycode(4)
            except Exception:
                pass

    def _set_item_ez_id_value(self, field: Any, value: str) -> str:
        field.click()
        time.sleep(0.3)
        strategies: list[Callable[[], None]] = [
            lambda: self._fill_via_send_keys(field, value),
            lambda: self._fill_via_clipboard(field, value),
            lambda: self._fill_via_adb_input(value),
            lambda: self._fill_via_mobile_set_value(field, value),
        ]
        for action in strategies:
            try:
                action()
                time.sleep(0.4)
                current = self._read_field_text(field)
                if value in current.replace(" ", "") or current == value:
                    return current
            except Exception:
                continue
        return self._read_field_text(field)

    def _fill_via_send_keys(self, field: Any, value: str) -> None:
        try:
            field.clear()
        except Exception:
            pass
        field.send_keys(value)

    def _fill_via_clipboard(self, field: Any, value: str) -> None:
        self.driver.set_clipboard_text(value)
        field.click()
        try:
            self.driver.press_keycode(279)
        except Exception:
            field.send_keys(value)

    def _fill_via_adb_input(self, value: str) -> None:
        udid = self.driver.capabilities.get("appium:udid") or self.driver.capabilities.get("udid")
        adb_helper.input_text(value, udid=udid)

    def _fill_via_mobile_set_value(self, field: Any, value: str) -> None:
        self.driver.execute_script(
            "mobile: setValue",
            {"elementId": field.id, "text": value},
        )

    def submit_item_number(self, item_number: str) -> str:
        """Type item number into Item EZ ID and tap Confirm."""
        value = item_number.strip()
        field = self.item_ez_id_input()
        entered = self._set_item_ez_id_value(field, value)
        if value not in entered.replace(" ", "") and entered != value:
            raise AssertionError(
                f"Item EZ ID field expected {value!r} after entry, got {entered!r}."
            )
        self._dismiss_keyboard_if_visible()
        self.confirm_button.click()
        return entered

    def _text_locator(self, label: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{label}")',
        )

    def _resource_locator(self, resource_id: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceId("{resource_id}")',
        )

    def _text_contains_locator(self, fragment: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{fragment}")',
        )

    def _item_details_scroll_gesture(self, direction: str) -> None:
        """Scroll through the horizontal center of the form (avoids edge scrollbar)."""
        window = self.driver.get_window_size()
        width = int(window["width"])
        height = int(window["height"])
        center_x = width // 2
        top_y = int(height * 0.28)
        bottom_y = int(height * 0.72)
        duration_ms = 500
        if direction == "up":
            self.driver.swipe(center_x, bottom_y, center_x, top_y, duration_ms)
        else:
            self.driver.swipe(center_x, top_y, center_x, bottom_y, duration_ms)
        time.sleep(self.ITEM_DETAILS_SCROLL_PAUSE_SECONDS)

    def scroll_item_details_down(self) -> None:
        """Reveal content lower on the item-details page."""
        self._item_details_scroll_gesture("up")

    def scroll_item_details_to_top(self) -> None:
        """Return the item-details scroll position near the top."""
        for _ in range(6):
            self._item_details_scroll_gesture("down")

    def _scroll_label_into_view(self, label: str) -> None:
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                (
                    "new UiScrollable(new UiSelector().scrollable(true))"
                    f'.scrollIntoView(new UiSelector().text("{label}"))'
                ),
            )
            time.sleep(self.ITEM_DETAILS_SCROLL_PAUSE_SECONDS)
        except Exception:
            pass

    def _scroll_resource_into_view(self, resource_id: str) -> None:
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                (
                    "new UiScrollable(new UiSelector().scrollable(true))"
                    f'.scrollIntoView(new UiSelector().resourceId("{resource_id}"))'
                ),
            )
            time.sleep(self.ITEM_DETAILS_SCROLL_PAUSE_SECONDS)
        except Exception:
            pass

    def _find_displayed_by_text(self, label: str) -> Any | None:
        for element in self.driver.find_elements(*self._text_locator(label)):
            try:
                if element.is_displayed():
                    return element
            except Exception:
                continue
        return None

    def _find_displayed_by_text_contains(self, fragment: str) -> Any | None:
        for element in self.driver.find_elements(*self._text_contains_locator(fragment)):
            try:
                if element.is_displayed():
                    return element
            except Exception:
                continue
        return None

    def ensure_label_visible(self, label: str, *, max_swipes: int | None = None) -> Any:
        """Scroll the details page until a text label is on screen."""
        limit = (
            self.ITEM_DETAILS_MAX_SCROLL_SWIPES
            if max_swipes is None
            else max_swipes
        )
        self.scroll_item_details_to_top()
        for swipe in range(limit + 1):
            self._scroll_label_into_view(label)
            found = self._find_displayed_by_text(label)
            if found is not None:
                return found
            if swipe < limit:
                self.scroll_item_details_down()
        raise AssertionError(f"Label {label!r} not visible after scrolling item details.")

    def scroll_to_discount_section(self) -> None:
        """Bring the discount block into view (often below stones on long items)."""
        self._scroll_resource_into_view(self.DISCOUNT_SECTION_ID)
        self._scroll_label_into_view(self.DISCOUNT_TITLE)

    def scroll_through_item_details(self) -> None:
        """Walk the page top-to-bottom so off-screen sections enter the viewport."""
        self.scroll_item_details_to_top()
        for _ in range(self.ITEM_DETAILS_MAX_SCROLL_SWIPES):
            self.scroll_item_details_down()

    def is_label_displayed(self, label: str, *, scroll: bool = False) -> bool:
        if scroll:
            try:
                self.ensure_label_visible(label)
                return True
            except AssertionError:
                return False
        return self._find_displayed_by_text(label) is not None

    def get_present_item_detail_labels(self) -> list[str]:
        """Return item-detail field labels found while scrolling the details page."""
        present: list[str] = []
        self.scroll_item_details_to_top()
        for label in self.ALL_ITEM_DETAIL_LABELS:
            if label in present:
                continue
            try:
                self.ensure_label_visible(label, max_swipes=4)
                present.append(label)
            except AssertionError:
                continue
        return present

    def get_visible_discount_row_labels(self) -> list[str]:
        """Return discount tier row labels visible (varies by item age / store)."""
        self.scroll_to_discount_section()
        visible: list[str] = []
        for label in self.DISCOUNT_ROW_LABELS:
            if self._find_displayed_by_text(label) is not None:
                visible.append(label)
                continue
            try:
                self.ensure_label_visible(label, max_swipes=6)
                visible.append(label)
            except AssertionError:
                continue
        return visible

    def has_discount_tier_rows(self) -> bool:
        self.scroll_to_discount_section()
        tier_ids = ("startingTier-0", "upperTier-0")
        for tier_id in tier_ids:
            for element in self.driver.find_elements(*self._resource_locator(tier_id)):
                try:
                    if element.is_displayed():
                        return True
                except Exception:
                    continue
        if self.get_visible_discount_row_labels():
            return True
        self.scroll_through_item_details()
        return bool(self.get_visible_discount_row_labels())

    def _element_in_tree(self, locator: tuple[str, str]) -> bool:
        return bool(self.driver.find_elements(*locator))

    def _find_item_number_element(self, item_id: str) -> Any | None:
        expected = item_id.strip()
        number_el = self._find_displayed_by_text(expected)
        if number_el is not None:
            return number_el
        contains_locator = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{expected}")',
        )
        for element in self.driver.find_elements(*contains_locator):
            try:
                if element.is_displayed():
                    return element
            except Exception:
                continue
        return None

    def verify_item_details_overview(self, item_id: str) -> None:
        """Verify top-of-page details, then one scroll for discount overview."""
        expected = item_id.strip()
        normalized = expected.replace(" ", "")

        self._debug_log("H1", "verify_item_details_overview start", {"item_id": expected})

        number_el = self._find_item_number_element(expected)
        if number_el is None:
            raise AssertionError(f"Item number {expected!r} not found on details screen.")
        item_text = (number_el.text or "").replace(" ", "")
        if normalized not in item_text:
            raise AssertionError(f"Expected item number {expected!r} in {item_text!r}.")

        top_markers = (
            self._find_displayed_by_text("Item number"),
            self._find_displayed_by_text(self.ITEM_DETAILS_HEADING),
            self._element_in_tree(self._resource_locator(self.FIELD_EZ_ID)),
        )
        if not any(top_markers):
            raise AssertionError("Expected item details content near top of screen.")

        self.scroll_item_details_down()
        self._debug_log("H2", "scrolled once for discount", {})

        discount_visible = (
            self._find_displayed_by_text(self.DISCOUNT_TITLE) is not None
            or self._find_displayed_by_text_contains(self.AGE_LABEL_PREFIX) is not None
            or self._element_in_tree(self._resource_locator(self.DISCOUNT_SECTION_ID))
        )
        if not discount_visible:
            self.scroll_item_details_down()
            discount_visible = (
                self._find_displayed_by_text(self.DISCOUNT_TITLE) is not None
                or self._find_displayed_by_text_contains(self.AGE_LABEL_PREFIX) is not None
                or self._element_in_tree(self._resource_locator(self.DISCOUNT_SECTION_ID))
            )
        if not discount_visible:
            raise AssertionError("Discount section overview not visible after scrolling.")

        self._debug_log("H2", "discount overview ok", {"has_section": True})

    def verify_discount_section(self) -> None:
        """Light discount check (title/age/section); used when full tier validation is needed."""
        if not self._element_in_tree(self._resource_locator(self.DISCOUNT_SECTION_ID)):
            raise AssertionError("Discount section is not present on screen.")
        if not (
            self._find_displayed_by_text(self.DISCOUNT_TITLE)
            or self._find_displayed_by_text_contains(self.AGE_LABEL_PREFIX)
        ):
            self.scroll_item_details_down()
        if not (
            self._find_displayed_by_text(self.DISCOUNT_TITLE)
            or self._find_displayed_by_text_contains(self.AGE_LABEL_PREFIX)
        ):
            raise AssertionError("Discount title or age line not visible.")

    def is_on_item_details_screen(self) -> bool:
        if not self.driver.find_elements(*self._text_locator(self.ITEM_MANAGEMENT_HEADING)):
            return False
        if not self.driver.find_elements(*self._text_contains_locator(self.AGE_LABEL_PREFIX)):
            return False
        return bool(self.driver.find_elements(*self._resource_locator(self.DISCOUNT_SECTION_ID)))

    def wait_for_item_details_screen(
        self, item_id: str, *, timeout: float | None = None
    ) -> None:
        """Wait until item details loaded (headings, item number, discount section in tree)."""
        expected = item_id.strip()
        normalized = expected.replace(" ", "")

        def _loaded() -> bool | None:
            if not self.driver.find_elements(*self._resource_locator(self.DISCOUNT_SECTION_ID)):
                return None
            if self._find_item_number_element(expected) is not None:
                return True
            for el in self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{expected}")',
            ):
                try:
                    text = (el.text or "").strip().replace(" ", "")
                    if normalized in text.replace(" ", ""):
                        return True
                except Exception:
                    continue
            return None

        wait_until(
            self.driver,
            _loaded,
            timeout=timeout if timeout is not None else self.ITEM_DETAILS_LOAD_TIMEOUT,
            poll=0.5,
            message=(
                f"Item details screen did not finish loading for item {expected!r} "
                "(expected headings, item number, and discount section)."
            ),
        )
        time.sleep(self.ITEM_DETAILS_SETTLE_SECONDS)

    # --- Item details screen (item_details.xml) ---

    @property
    def item_management_heading(self):
        return self.wait.until_present(self._text_locator(self.ITEM_MANAGEMENT_HEADING))

    @property
    def item_details_heading(self):
        return self.wait.until_present(self._text_locator(self.ITEM_DETAILS_HEADING))

    @property
    def item_details_ez_id_field(self):
        return self.wait.until_present(self._resource_locator(self.FIELD_EZ_ID))

    @property
    def stones_section(self):
        return self.wait.until_present(self._resource_locator(self.STONES_SECTION_ID))

    @property
    def stones_heading(self):
        return self.wait.until_present(self._text_locator(self.STONES_HEADING))

    @property
    def discount_section(self):
        return self.wait.until_present(self._resource_locator(self.DISCOUNT_SECTION_ID))

    @property
    def discount_title(self):
        return self.wait.until_present(self._text_locator(self.DISCOUNT_TITLE))

    @property
    def discount_age_line(self):
        return self.wait.until_present(self._text_contains_locator(self.AGE_LABEL_PREFIX))

    @property
    def printer_media_hint(self):
        return self.wait.until_present(self._text_locator(self.PRINTER_MEDIA_HINT))

    @property
    def print_tag_button(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.PRINT_TAG_DESC))

    def get_item_detail_label(self, label: str):
        return self.wait.until_present(self._text_locator(label))

    def get_stone_field_label(self, label: str):
        return self.wait.until_present(self._text_locator(label))

    def get_discount_table_header(self, header: str):
        return self.wait.until_present(self._text_locator(header))

    def get_item_number_on_details(self, item_id: str | None = None) -> str:
        expected = (item_id or self.EXPECTED_BARCODE).strip()
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{expected}")')
        )

    def _barcode_image_path(self, barcode_image: Path | None) -> Path:
        image = (barcode_image or self.DEFAULT_BARCODE_IMAGE).resolve()
        if not image.is_file():
            raise FileNotFoundError(
                f"Barcode image required: {image}. Add pages/common/barcode_14401.png (CODE128 of the item number)."
            )
        return image

    def scan_barcode_live(
        self, barcode_image: Path | None = None, *, fallback_item_id: str | None = None
    ) -> str:
        """Decode barcode, submit on scan screen, and wait for item details to load."""
        try:
            item_id = decode_barcode_from_image(self._barcode_image_path(barcode_image))
        except ValueError:
            item_id = (fallback_item_id or self.EXPECTED_BARCODE).strip()
        self.submit_item_number(item_id)
        self.wait_for_item_details_screen(item_id)
        return item_id

    def complete_barcode_scan_to_item_details(
        self, barcode_image: Path | None = None
    ) -> str:
        """Full scan flow ending on the loaded item details screen."""
        return self.scan_barcode_live(barcode_image)

    def lookup_item_number_to_details(self, item_number: str) -> str:
        """Manual item entry on scan screen, then wait for item details."""
        item_id = item_number.strip()
        self.submit_item_number(item_id)
        if self._element_in_tree(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("wrongStoreModal")')
        ):
            raise AssertionError(
                f"Item {item_id!r} belongs to a different store (wrong-store modal shown)."
            )
        self.wait_for_item_details_screen(item_id)
        wait_for_present(
            self.driver,
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{item_id}")',
            ),
            timeout=self.wait.timeout,
            message=f"Item number {item_id!r} not visible on details screen after load.",
        )
        return item_id

    def tap_edit_on_details(self) -> None:
        """Scroll to and tap Edit on the item details screen."""
        self._scroll_resource_into_view(self.EDIT_BUTTON_ID)
        edit = self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, self.EDIT_BUTTON_DESC))
        edit.click()
        self.wait_for_edit_item_screen()
        self._debug_log("H3", "opened edit screen", {})

    def wait_for_edit_item_screen(self, *, timeout: float | None = None) -> None:
        wait_for_present(
            self.driver,
            self._text_locator(self.EDIT_ITEM_HEADING),
            timeout=timeout if timeout is not None else self.wait.timeout,
            message="Edit item details screen did not appear.",
        )
        time.sleep(self.ITEM_DETAILS_SETTLE_SECONDS)

    def verify_edit_item_top(self, item_id: str) -> None:
        """Verify edit form header before scrolling to stones (edititem1.xml)."""
        expected = item_id.strip()
        wait_for_present(
            self.driver,
            self._text_locator(self.EDIT_ITEM_HEADING),
            timeout=self.wait.timeout,
            message="Edit item details heading missing.",
        )
        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, self.EDIT_ITEM_NUMBER_DESC),
            timeout=self.wait.timeout,
            message="Item # field missing on edit screen.",
        )
        if not self._element_in_tree(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{expected}")')
        ):
            raise AssertionError(f"Item id {expected!r} not on edit screen.")

    def _is_stone_color_field_visible(self) -> bool:
        for element in self.driver.find_elements(*self._resource_locator(self.STONE_COLOR_FIELD_ID)):
            try:
                if element.is_displayed():
                    return True
            except Exception:
                continue
        return False

    def scroll_edit_item_down_once(self) -> None:
        self.scroll_item_details_down()

    def scroll_edit_item_to_stone_color(self, *, max_swipes: int = 5) -> None:
        """Scroll the edit form down until stone Color / Type is on screen."""
        self._debug_log("H6", "scroll_edit_to_stone_color start", {"max_swipes": max_swipes})
        for swipe in range(max_swipes + 1):
            if self._is_stone_color_field_visible():
                self._debug_log("H6", "stone color field visible", {"swipes": swipe})
                return
            self.scroll_item_details_down()
        self._scroll_resource_into_view(self.STONE_COLOR_FIELD_ID)
        self._scroll_label_into_view("Color / Type")
        if not self._is_stone_color_field_visible():
            raise AssertionError(
                "Stone Color / Type field not visible after scrolling edit screen."
            )

    def verify_edit_item_stones_section(self) -> None:
        """Verify stones block is reachable after scrolling (edititem2.xml)."""
        self.scroll_edit_item_to_stone_color()
        if not self._is_stone_color_field_visible():
            raise AssertionError("Stone Color / Type field not found on edit screen.")

    def _stone_color_option_label(self, element: Any) -> str:
        desc = (element.get_attribute("content-desc") or "").strip().upper()
        if desc:
            return desc
        for text_view in element.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"):
            text = (text_view.text or "").strip().upper()
            if text:
                return text
        return ""

    def _get_stone_color_displayed_value(self) -> str:
        """Read current Color/Type from inner TextView on stoneColor-0 (edititem2.xml)."""
        color_field = self.wait.until_present(
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("{self.STONE_COLOR_FIELD_ID}")',
            )
        )
        content_desc = (color_field.get_attribute("content-desc") or "").strip()
        field_text = (color_field.text or "").strip()
        child_values: list[str] = []
        for text_view in color_field.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"):
            text = (text_view.text or "").strip()
            if text and text != self.STONE_COLOR_DROPDOWN_CARET:
                child_values.append(text.upper())
        current = child_values[0] if child_values else (field_text or content_desc).upper()
        # region agent log
        self._debug_log(
            "H1",
            "stone color current read",
            {
                "contentDesc": content_desc,
                "fieldText": field_text,
                "childTextViews": child_values,
                "resolvedCurrent": current,
            },
        )
        # endregion
        return current

    def _collect_stone_color_modal_options(self) -> list[tuple[str, Any]]:
        """Return (label, element) pairs from stoneColor-0-modal (coloroptions.xml)."""
        wait_for_present(
            self.driver,
            self._resource_locator(self.STONE_COLOR_MODAL_ID),
            timeout=self.wait.timeout,
            message="Stone color options modal did not open.",
        )
        option_prefix = f"{self.STONE_COLOR_FIELD_ID}-option"
        option_elements = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceIdMatches("{option_prefix}.*")',
        )
        options: list[tuple[str, Any]] = []
        seen: set[str] = set()
        for element in option_elements:
            label = self._stone_color_option_label(element)
            if label and label not in seen:
                seen.add(label)
                options.append((label, element))
        # region agent log
        self._debug_log(
            "H2",
            "stone color modal options",
            {"labels": [label for label, _ in options]},
        )
        # endregion
        return options

    def change_stone_color_to_alternate(self) -> str:
        """Open Color / Type picker and choose any option different from the current value."""
        self.scroll_edit_item_to_stone_color()
        current = self._get_stone_color_displayed_value()
        if not current or current == self.STONE_FIELD_LABELS[0].upper():
            raise AssertionError(
                "Could not read current stone Color / Type from edit screen."
            )
        color_field = self.wait.until_clickable(
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("{self.STONE_COLOR_FIELD_ID}")',
            )
        )
        color_field.click()
        modal_options = self._collect_stone_color_modal_options()
        if not modal_options:
            raise AssertionError("Stone color picker opened but no options were found.")
        chosen = ""
        for label, element in modal_options:
            if label == current:
                continue
            element.click()
            chosen = label
            break
        if not chosen:
            raise AssertionError(
                f"No alternate stone color found (current={current!r}, "
                f"options={[label for label, _ in modal_options]!r})."
            )
        time.sleep(self.ITEM_DETAILS_SETTLE_SECONDS)
        # region agent log
        self._debug_log("H4", "stone color selected", {"color": chosen, "previous": current})
        # endregion
        return chosen

    def tap_update_and_print_tag(self) -> None:
        self._scroll_resource_into_view(self.UPDATE_AND_PRINT_ID)
        button = self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, self.UPDATE_AND_PRINT_DESC))
        button.click()
        time.sleep(self.ITEM_DETAILS_SETTLE_SECONDS)
        self._debug_log("H5", "tapped update and print tag", {})

    def wait_for_item_updated_success_modal(self, *, timeout: float | None = None) -> None:
        """Wait for post-update success dialog (save + tag sent to printer)."""
        wait_timeout = timeout if timeout is not None else self.ITEM_UPDATE_SUCCESS_TIMEOUT
        wait_for_present(
            self.driver,
            self._text_locator(self.ITEM_UPDATED_TITLE),
            timeout=wait_timeout,
            message="Item Updated success modal did not appear.",
        )
        wait_for_present(
            self.driver,
            self._text_contains_locator("saved successfully"),
            timeout=wait_timeout,
            message="Save-success message not shown on Item Updated modal.",
        )
        wait_for_present(
            self.driver,
            self._text_contains_locator("sent to the printer"),
            timeout=wait_timeout,
            message="Printer-success message not shown on Item Updated modal.",
        )
        self._debug_log("H7", "item updated success modal visible", {})

    def verify_item_updated_success_modal(self) -> None:
        """Assert success modal content and action buttons are present."""
        checks = (
            (self.ITEM_UPDATED_TITLE, self._text_locator(self.ITEM_UPDATED_TITLE)),
            ("saved successfully", self._text_contains_locator("saved successfully")),
            ("sent to the printer", self._text_contains_locator("sent to the printer")),
        )
        for name, locator in checks:
            if self._find_displayed_by_text(name) is not None:
                continue
            if self._element_in_tree(locator):
                continue
            raise AssertionError(f"Success modal missing {name!r}.")

        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, self.SCAN_ANOTHER_ITEM_DESC),
            timeout=self.wait.timeout,
            message="Scan another item button missing on success modal.",
        )
        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, self.GO_HOME_DESC),
            timeout=self.wait.timeout,
            message="Go to Home button missing on success modal.",
        )

    def tap_go_home_from_item_updated_modal(self) -> None:
        """Dismiss Item Updated modal and return to MODULES home."""
        self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, self.GO_HOME_DESC)).click()
        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            poll=0.5,
            message="Home screen did not appear after tapping Go to Home.",
        )
        self._debug_log("H7", "returned home from item updated modal", {})

    def complete_edit_color_and_update_flow(self, item_id: str) -> str:
        """Edit flow: scroll to color, update, print, and wait for success modal."""
        self.verify_edit_item_top(item_id)
        self.verify_edit_item_stones_section()
        chosen = self.change_stone_color_to_alternate()
        self.scroll_edit_item_down_once()
        self.tap_update_and_print_tag()
        self.wait_for_item_updated_success_modal()
        self.verify_item_updated_success_modal()
        return chosen

    @property
    def edit_button(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.EDIT_BUTTON_DESC))

    def is_edit_button_displayed(self) -> bool:
        elements = self.driver.find_elements(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceId("{self.EDIT_BUTTON_ID}")')
        )
        return any(el.is_displayed() for el in elements)

    def ensure_on_home_before_menu(self) -> None:
        """Dismiss Data Sync if it blocks the hamburger menu."""
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.navigate_to_dashboard_via_menu()

    def return_to_dashboard_via_menu(self) -> None:
        """Leave Retail Item Manager and return to MODULES via hamburger → Dashboard."""
        self.home.navigate_to_dashboard_via_menu()
