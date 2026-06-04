"""Assign Item Location flow — scan barcode, pick location, confirm, return home.

Supports two post-scan layouts:
- **Move item** — tap **Item Location**, toggle between **A 24** and **A 54** (always pick
  the one that is not the item's current location), confirm on the modal.
- **Change location reference** — ``locationNameInput`` with ``suggestion-*`` radios
  (e.g. J-04, END-J, JC, JAGI LAB); skips Assigned / Current rows.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from appium.webdriver.common.appiumby import AppiumBy

from pages.common import adb_helper
from pages.common.appium_wait import AppiumWait, wait_for_present, wait_until
from pages.item_manager.barcode_decode import decode_barcode_from_image
from pages.login.home_page import HomePage

DEFAULT_BARCODE_IMAGE = (
    Path(__file__).resolve().parent.parent / "common" / "barcode_14401.png"
)


class AssignItemLocationPage:
    STORE_14401_ITEM_ID = "144010051344"

    ASSIGN_BUTTON_ID = "assignItemLocationButton"
    ASSIGN_BUTTON_DESC = "Assign Item Location"

    SCAN_HEADING = "Scan item barcode"
    ITEM_NUMBER_INPUT_ID = "itemEzIdInput"
    CONFIRM_BUTTON_ID = "confirmButton"

    MOVE_ITEM_TITLE = "Move item"
    MOVE_ITEM_CURRENT_LOCATION_LABEL = "Current location"
    CHANGE_REF_TITLE = "Change location reference"
    ASSIGN_REF_TITLE = "Assign location reference"

    SHELF_INPUT_ID = "shelfIdInput"
    ITEM_LOCATION_LABEL = "Item Location"
    LOCATION_NAME_INPUT_ID = "locationNameInput"
    CURRENT_LABEL_BADGE_ID = "currentLabelBadge"
    CHANGE_BUTTON_ID = "changeButton"
    LOCATION_SUGGESTIONS_ID = "locationSuggestions"

    CONTINUE_BUTTON_DESC = "Continue"
    JUST_CHECKING_TITLE_ID = "justCheckingTitle"
    JUST_CHECKING_CONFIRM_ID = "justCheckingConfirmButton"

    CONFIRMATION_MODAL_ID = "confirmationModal"
    CONFIRM_FINAL_BUTTON_ID = "confirmFinalButton"

    SUCCESS_VIEW_ID = "successView"
    SUCCESS_MODAL_ID = "successModal"
    GO_HOME_BUTTON_ID = "closeButton"
    GO_TO_LOCATOR_HOME_ID = "goToLocatorHomeButton"
    GO_HOME_DESC = "Go to Home"

    WRONG_STORE_MODAL_ID = "wrongStoreModal"

    SUGGESTION_RESOURCE_PATTERN = "suggestion-.*"
    SHELF_SUGGESTION_RESOURCE_PATTERN = "shelfIdInput-suggestion-.*"

    # Store 14401 item — alternate between these two shelf locations each run.
    LOCATION_A24 = "A 24"
    LOCATION_A54 = "A 54"
    TOGGLE_LOCATION_KEYS = frozenset({"A24", "A54"})

    # Fallback prefixes when not on Move item (Change location reference).
    SEARCH_PREFIXES = ("A", "B", "C", "J", "JC", "JA", "E", "G")

    SCROLL_PAUSE_SECONDS = 0.35

    # Full flow (scan + A24/A54 toggle + modals) needs ~60–90s; 25s is too short in suite runs.
    DEFAULT_FLOW_TIMEOUT = 90

    def __init__(self, driver, home: HomePage, timeout: int = DEFAULT_FLOW_TIMEOUT) -> None:
        self.driver = driver
        self.home = home
        self.wait = AppiumWait(driver, float(timeout))

    def _text(self, label: str) -> tuple[str, str]:
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{label}")')

    def _text_contains(self, fragment: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{fragment}")',
        )

    def _resource(self, resource_id: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceId("{resource_id}")',
        )

    def _resource_matches(self, pattern: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceIdMatches("{pattern}")',
        )

    def _accessibility(self, desc: str) -> tuple[str, str]:
        return (AppiumBy.ACCESSIBILITY_ID, desc)

    def _dismiss_keyboard(self) -> None:
        self._dismiss_keyboard_for_suggestions()

    def _tap_outside_location_field(self) -> None:
        """Blur the Item Location field so the suggestion list is not under the keyboard."""
        for locator in (
            self._text(self.MOVE_ITEM_TITLE),
            self._text_contains("THIS ITEM ALREADY HAS A LOCATION"),
            self._text_contains("Current location"),
        ):
            elements = self.driver.find_elements(*locator)
            if elements:
                try:
                    elements[0].click()
                    time.sleep(0.25)
                    return
                except Exception:
                    continue

    def _dismiss_keyboard_for_suggestions(self) -> None:
        """
        Hide the soft keyboard so shelf/location suggestions below the field stay visible.
        """
        for strategy in ("tapOutside", "swipeDown", None):
            try:
                if strategy:
                    self.driver.hide_keyboard(strategy=strategy)
                else:
                    self.driver.hide_keyboard()
                time.sleep(0.35)
            except Exception:
                continue

        self._tap_outside_location_field()

        try:
            if self.driver.is_keyboard_shown():
                self.driver.press_keycode(66)  # ENTER — often closes IME without leaving screen
                time.sleep(0.25)
        except Exception:
            pass

        try:
            if self.driver.is_keyboard_shown() and (
                self.is_on_move_item_screen() or self.is_on_change_reference_screen()
            ):
                self.driver.press_keycode(4)  # BACK — only while still on location screen
                time.sleep(0.25)
        except Exception:
            pass

    def _shelf_suggestions_scroll_view(self) -> Any | None:
        scrolls = self.driver.find_elements(
            AppiumBy.XPATH,
            '//android.widget.EditText[@resource-id="shelfIdInput"]'
            "/following-sibling::android.widget.ScrollView",
        )
        for scroll in scrolls:
            try:
                if scroll.is_displayed():
                    return scroll
            except Exception:
                continue
        return None

    def _scroll_shelf_suggestion_into_view(self, element: Any) -> None:
        try:
            self.driver.execute_script(
                "mobile: scrollGesture",
                {
                    "elementId": element.id,
                    "direction": "down",
                    "percent": 0.85,
                },
            )
            time.sleep(self.SCROLL_PAUSE_SECONDS)
            return
        except Exception:
            pass

        scroll_view = self._shelf_suggestions_scroll_view()
        if scroll_view is not None:
            try:
                rect = scroll_view.rect
                cx = rect["x"] + rect["width"] // 2
                top = rect["y"] + int(rect["height"] * 0.75)
                bottom = rect["y"] + int(rect["height"] * 0.25)
                self.driver.swipe(cx, top, cx, bottom, 350)
                time.sleep(self.SCROLL_PAUSE_SECONDS)
                return
            except Exception:
                pass

        self.scroll_from_center(direction="up", times=1)

    def _click_suggestion_element(self, element: Any, *, shelf: bool = False) -> None:
        self._dismiss_keyboard_for_suggestions()
        if shelf:
            self._scroll_shelf_suggestion_into_view(element)
        else:
            self._scroll_suggestion_list()
        self._dismiss_keyboard_for_suggestions()

        try:
            element.click()
            return
        except Exception:
            pass

        try:
            rect = element.rect
            x = rect["x"] + rect["width"] // 2
            y = rect["y"] + rect["height"] // 2
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        except Exception:
            raise

    def _wait_for_suggestions(self, pattern: str, *, timeout: float = 5.0) -> bool:
        def _has_suggestions() -> bool | None:
            if self._collect_suggestion_elements(pattern):
                return True
            return None

        try:
            wait_until(
                self.driver,
                _has_suggestions,
                timeout=timeout,
                message=f"Location suggestions ({pattern}) did not appear.",
            )
            return True
        except Exception:
            return bool(self._collect_suggestion_elements(pattern))

    def _device_udid(self) -> str | None:
        return (
            self.driver.capabilities.get("appium:udid")
            or self.driver.capabilities.get("udid")
        )

    def scroll_from_center(self, *, direction: str = "down", times: int = 1) -> None:
        """Swipe from the middle of the screen to reveal fields below the fold."""
        window = self.driver.get_window_size()
        width = int(window["width"])
        height = int(window["height"])
        center_x = width // 2
        top_y = int(height * 0.30)
        bottom_y = int(height * 0.70)
        for _ in range(times):
            if direction == "down":
                self.driver.swipe(center_x, bottom_y, center_x, top_y, 500)
            else:
                self.driver.swipe(center_x, top_y, center_x, bottom_y, 400)
            time.sleep(self.SCROLL_PAUSE_SECONDS)

    # --- Screen detection ---

    def is_on_move_item_screen(self) -> bool:
        return bool(self.driver.find_elements(*self._text(self.MOVE_ITEM_TITLE)))

    def is_on_change_reference_screen(self) -> bool:
        return bool(self.driver.find_elements(*self._text(self.CHANGE_REF_TITLE)))

    def is_on_assign_reference_screen(self) -> bool:
        return bool(self.driver.find_elements(*self._text(self.ASSIGN_REF_TITLE)))

    def is_just_checking_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.JUST_CHECKING_TITLE_ID)))

    def is_confirmation_modal_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.CONFIRMATION_MODAL_ID)))

    def is_success_view_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.SUCCESS_VIEW_ID)))

    def is_success_modal_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.SUCCESS_MODAL_ID)))

    def is_wrong_store_modal_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.WRONG_STORE_MODAL_ID)))

    def is_assign_success_visible(self) -> bool:
        return self.is_success_view_visible() or self.is_success_modal_visible()

    # --- Navigation ---

    def open_item_locator_from_home(self) -> None:
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.navigate_to_dashboard_via_menu()
        self.home.item_locator_module.click()
        wait_for_present(
            self.driver,
            self._text("What would you like to do?"),
            timeout=self.wait.timeout,
            message="Item Locator hub did not load.",
        )

    def tap_assign_item_location(self) -> None:
        self.wait.until_present(self._resource(self.ASSIGN_BUTTON_ID)).click()
        wait_for_present(
            self.driver,
            self._text(self.SCAN_HEADING),
            timeout=self.wait.timeout,
            message="Assign Item Location scan screen did not appear.",
        )

    def scan_and_enter_item_number(self, barcode_image: Path | None = None) -> str:
        image = (barcode_image or DEFAULT_BARCODE_IMAGE).resolve()
        item_id = decode_barcode_from_image(image)

        field = self.wait.until_present(self._resource(self.ITEM_NUMBER_INPUT_ID))
        field.click()
        time.sleep(0.3)

        for action in (
            lambda: self._fill_via_send_keys(field, item_id),
            lambda: self._fill_via_adb(item_id),
        ):
            try:
                action()
                time.sleep(0.4)
                current = (field.text or "").strip()
                if item_id in current.replace(" ", ""):
                    break
            except Exception:
                continue

        return item_id

    def _fill_via_send_keys(self, field: Any, value: str) -> None:
        try:
            field.clear()
        except Exception:
            pass
        field.send_keys(value)

    def _fill_via_adb(self, value: str) -> None:
        adb_helper.input_text(value, udid=self._device_udid())

    def confirm_item_number(self) -> str:
        """Confirm scanned item and wait for the next assign-location screen."""
        self._dismiss_keyboard()
        self.wait.until_present(self._resource(self.CONFIRM_BUTTON_ID)).click()
        if self.is_wrong_store_modal_visible():
            raise AssertionError(
                "Wrong-store modal appeared; use a barcode for the logged-in store "
                f"(expected item like {self.STORE_14401_ITEM_ID})."
            )
        return self.wait_for_post_scan_screen()

    def wait_for_post_scan_screen(self) -> str:
        """Return ``move_item``, ``change_reference``, or ``assign_reference``."""

        def _detected() -> str | None:
            if self.is_wrong_store_modal_visible():
                return None
            if self.is_on_move_item_screen():
                return "move_item"
            if self.is_on_change_reference_screen():
                return "change_reference"
            if self.is_on_assign_reference_screen():
                return "assign_reference"
            return None

        mode = wait_until(
            self.driver,
            _detected,
            timeout=self.wait.timeout,
            message=(
                "Neither Move item, Change location reference, nor "
                "Assign location reference appeared after confirming item number."
            ),
        )
        return mode or "move_item"

    def tap_change_from_assign_reference(self) -> None:
        self.wait.until_present(self._resource(self.CHANGE_BUTTON_ID)).click()
        wait_for_present(
            self.driver,
            self._text(self.CHANGE_REF_TITLE),
            timeout=self.wait.timeout,
            message="Change location reference screen did not appear after tapping Change.",
        )

    def get_current_label_from_badge(self) -> str:
        if not self.driver.find_elements(*self._resource(self.CURRENT_LABEL_BADGE_ID)):
            return ""
        badge = self.wait.until_present(self._resource(self.CURRENT_LABEL_BADGE_ID))
        for child in badge.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"):
            text = (child.text or "").strip()
            if text and text != "CURRENT LABEL":
                return text
        return ""

    @staticmethod
    def _is_inventory_status_text(text: str) -> bool:
        return text.startswith("IN -") or text.startswith("IN –")

    @classmethod
    def _is_toggle_shelf_key(cls, location_key: str) -> bool:
        return location_key in cls.TOGGLE_LOCATION_KEYS

    @classmethod
    def _is_valid_move_item_location_value(cls, text: str) -> bool:
        if not text or text == cls.MOVE_ITEM_CURRENT_LOCATION_LABEL:
            return False
        if cls._is_inventory_status_text(text):
            return False
        return True

    def _ensure_current_location_row_visible(self) -> None:
        """Scroll Move item until the ``Current location`` row is on screen."""
        for _ in range(5):
            if self.driver.find_elements(*self._text(self.MOVE_ITEM_CURRENT_LOCATION_LABEL)):
                return
            self.scroll_from_center(direction="up", times=1)

    def _scan_move_item_for_toggle_shelf(self) -> str:
        """Find A 24 / A 54 anywhere on the Move item card (fallback)."""
        for element in self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"):
            try:
                text = (element.text or "").strip()
            except Exception:
                continue
            if self._is_toggle_shelf_key(self._normalize_location_key(text)):
                return text
        return ""

    def get_current_location_on_move_item(self) -> str:
        """
        Read shelf id from the **Current location** row on Move item.

        Layout (``moveitemlocator.xml``): label TextView then value TextView on the
        same row (e.g. ``A 54``). Assigning the same shelf again causes an error.
        """
        if not self.is_on_move_item_screen():
            return ""
        self._ensure_current_location_row_visible()

        labels = self.driver.find_elements(
            *self._text(self.MOVE_ITEM_CURRENT_LOCATION_LABEL)
        )
        if not labels:
            return self._scan_move_item_for_toggle_shelf()

        label = labels[0]
        row_candidates: list[str] = []

        for xpath in (
            "./following-sibling::android.widget.TextView[1]",
            "./following-sibling::android.view.ViewGroup[1]"
            "//android.widget.TextView",
            "./preceding-sibling::android.view.ViewGroup[1]"
            "//android.widget.TextView",
        ):
            try:
                for element in label.find_elements(AppiumBy.XPATH, xpath):
                    text = (element.text or "").strip()
                    if self._is_valid_move_item_location_value(text):
                        row_candidates.append(text)
            except Exception:
                continue

        try:
            parent = label.find_element(AppiumBy.XPATH, "..")
            after_label = False
            for child in parent.find_elements(AppiumBy.XPATH, "./*"):
                try:
                    child_text = (child.text or "").strip()
                    if child_text == self.MOVE_ITEM_CURRENT_LOCATION_LABEL:
                        after_label = True
                        continue
                    if not after_label:
                        continue
                    for element in child.find_elements(
                        AppiumBy.CLASS_NAME, "android.widget.TextView"
                    ):
                        text = (element.text or "").strip()
                        if self._is_valid_move_item_location_value(text):
                            row_candidates.append(text)
                    if child.get_attribute("className") == "android.widget.TextView":
                        text = (child.text or "").strip()
                        if self._is_valid_move_item_location_value(text):
                            row_candidates.append(text)
                    if (child.text or "").strip().startswith("IN -"):
                        break
                except Exception:
                    continue
        except Exception:
            pass

        for text in row_candidates:
            if self._is_toggle_shelf_key(self._normalize_location_key(text)):
                return text

        if row_candidates:
            return row_candidates[0]

        return self._scan_move_item_for_toggle_shelf()

    @staticmethod
    def _normalize_location_key(name: str) -> str:
        return re.sub(r"[\s\-–]+", "", (name or "")).upper()

    @classmethod
    def _toggle_target_for_current(cls, current_location: str) -> tuple[str, tuple[str, ...]]:
        """
        Return ``(display_label, search_prefixes)`` for the shelf location to assign.

        Toggles A 24 ↔ A 54 from the **Current location** row; never re-picks the same shelf.
        """
        current_key = cls._normalize_location_key(current_location)
        if current_key == "A24":
            return cls.LOCATION_A54, ("A 54", "A54", "A5", "A")
        if current_key == "A54":
            return cls.LOCATION_A24, ("A 24", "A24", "A2", "A")
        # Label row showed a reference name (e.g. Jewelry Safe) — scan card for A 24/A 54.
        return cls.LOCATION_A54, ("A 54", "A54", "A5", "A")

    @classmethod
    def _label_matches_location_key(cls, label: str, target_key: str) -> bool:
        return cls._normalize_location_key(label) == target_key

    @staticmethod
    def _label_from_suggestion(content_desc: str, resource_id: str) -> str:
        if content_desc:
            return content_desc.split(",")[0].strip()
        prefix = "suggestion-"
        if resource_id.startswith(prefix):
            return resource_id[len(prefix) :].strip()
        shelf_prefix = "shelfIdInput-suggestion-"
        if resource_id.startswith(shelf_prefix):
            return resource_id[len(shelf_prefix) :].strip()
        return ""

    def _is_unavailable_location(
        self,
        *,
        content_desc: str,
        label: str,
        current_label: str,
        current_location: str,
    ) -> bool:
        desc_lower = (content_desc or "").lower()
        if "assigned" in desc_lower:
            return True
        if "current" in desc_lower:
            return True
        normalized = self._normalize_location_key(label)
        if current_label and normalized == self._normalize_location_key(current_label):
            return True
        if current_location and normalized == self._normalize_location_key(current_location):
            return True
        return False

    def _collect_suggestion_elements(self, pattern: str) -> list[Any]:
        seen: set[str] = set()
        visible: list[Any] = []
        enabled: list[Any] = []
        for element in self.driver.find_elements(*self._resource_matches(pattern)):
            try:
                resource_id = (element.get_attribute("resourceId") or "").strip()
            except Exception:
                continue
            if not resource_id or resource_id in seen:
                continue
            seen.add(resource_id)
            try:
                if not element.is_enabled():
                    continue
                enabled.append(element)
                if element.is_displayed():
                    visible.append(element)
            except Exception:
                continue
        return visible or enabled

    def _pick_first_available_suggestion(
        self,
        *,
        pattern: str,
        current_label: str,
        current_location: str,
        shelf_suggestions: bool = False,
    ) -> str:
        for element in self._collect_suggestion_elements(pattern):
            resource_id = (element.get_attribute("resourceId") or "").strip()
            content_desc = (element.get_attribute("content-desc") or "").strip()
            label = self._label_from_suggestion(content_desc, resource_id)
            if not label:
                continue
            if self._is_unavailable_location(
                content_desc=content_desc,
                label=label,
                current_label=current_label,
                current_location=current_location,
            ):
                continue
            self._click_suggestion_element(element, shelf=shelf_suggestions)
            return label
        return ""

    def _pick_shelf_suggestion_by_key(
        self,
        *,
        target_key: str,
        current_location: str,
    ) -> str:
        """Select a shelf suggestion whose normalized label equals ``target_key``."""
        current_key = self._normalize_location_key(current_location)
        for element in self._collect_suggestion_elements(self.SHELF_SUGGESTION_RESOURCE_PATTERN):
            resource_id = (element.get_attribute("resourceId") or "").strip()
            content_desc = (element.get_attribute("content-desc") or "").strip()
            label = self._label_from_suggestion(content_desc, resource_id)
            if not label:
                continue
            label_key = self._normalize_location_key(label)
            if label_key != target_key:
                continue
            if label_key == current_key:
                continue
            if self._is_unavailable_location(
                content_desc=content_desc,
                label=label,
                current_label="",
                current_location=current_location,
            ):
                continue
            self._click_suggestion_element(element, shelf=True)
            return label
        return ""

    def _type_into_field(
        self,
        field: Any,
        text: str,
        *,
        for_suggestions: bool = False,
        suggestion_pattern: str | None = None,
    ) -> None:
        field.click()
        time.sleep(0.3)
        try:
            field.clear()
        except Exception:
            pass
        filled = False
        if for_suggestions:
            try:
                self.driver.execute_script(
                    "mobile: setValue",
                    {"elementId": field.id, "text": text},
                )
                filled = True
            except Exception:
                pass
        if not filled:
            try:
                self._fill_via_send_keys(field, text)
                filled = True
            except Exception:
                self._fill_via_adb(text)
        time.sleep(0.5)
        if for_suggestions:
            self._dismiss_keyboard_for_suggestions()
            if suggestion_pattern:
                self._wait_for_suggestions(suggestion_pattern, timeout=4.0)
            time.sleep(0.3)
        else:
            time.sleep(0.3)

    def _scroll_suggestion_list(self) -> None:
        if self.driver.find_elements(*self._resource(self.LOCATION_SUGGESTIONS_ID)):
            container = self.driver.find_element(*self._resource(self.LOCATION_SUGGESTIONS_ID))
            try:
                window = self.driver.get_window_size()
                cx = window["width"] // 2
                self.driver.swipe(cx, int(window["height"] * 0.65), cx, int(window["height"] * 0.45), 400)
                time.sleep(self.SCROLL_PAUSE_SECONDS)
                return
            except Exception:
                pass
        self.scroll_from_center(direction="down")

    def select_change_reference_location(self) -> str:
        """Pick any available location on Change location reference (not Assigned/Current)."""
        current_label = self.get_current_label_from_badge()
        field = self.wait.until_present(self._resource(self.LOCATION_NAME_INPUT_ID))

        for prefix in self.SEARCH_PREFIXES:
            self._type_into_field(
                field,
                prefix,
                for_suggestions=True,
                suggestion_pattern=self.SUGGESTION_RESOURCE_PATTERN,
            )
            self._dismiss_keyboard_for_suggestions()

            for _ in range(3):
                chosen = self._pick_first_available_suggestion(
                    pattern=self.SUGGESTION_RESOURCE_PATTERN,
                    current_label=current_label,
                    current_location="",
                )
                if chosen:
                    time.sleep(0.5)
                    return chosen
                self._scroll_suggestion_list()

        raise AssertionError(
            "No available location found on Change location reference "
            f"(current label: {current_label!r}). Tried prefixes: {self.SEARCH_PREFIXES}."
        )

    def scroll_to_item_location_field(self) -> None:
        """Scroll the Move item screen until the Item Location field is visible."""
        for _ in range(6):
            if self.driver.find_elements(*self._resource(self.SHELF_INPUT_ID)):
                try:
                    field = self.driver.find_element(*self._resource(self.SHELF_INPUT_ID))
                    if field.is_displayed():
                        return
                except Exception:
                    pass
            self.scroll_from_center(direction="down")

    def tap_item_location_field(self) -> Any:
        """Tap the Item Location text box (shelfIdInput) under 'Enter Item Location instead'."""
        self.scroll_to_item_location_field()
        wait_for_present(
            self.driver,
            self._text(self.ITEM_LOCATION_LABEL),
            timeout=self.wait.timeout,
            message="Item Location label not found on Move item screen.",
        )
        field = self.wait.until_present(self._resource(self.SHELF_INPUT_ID))
        field.click()
        time.sleep(0.3)
        return field

    def _scroll_shelf_suggestion_list(self) -> None:
        scroll_view = self._shelf_suggestions_scroll_view()
        if scroll_view is not None:
            try:
                rect = scroll_view.rect
                cx = rect["x"] + rect["width"] // 2
                top = rect["y"] + int(rect["height"] * 0.8)
                bottom = rect["y"] + int(rect["height"] * 0.2)
                self.driver.swipe(cx, top, cx, bottom, 400)
                time.sleep(self.SCROLL_PAUSE_SECONDS)
                return
            except Exception:
                pass
        self.scroll_from_center(direction="up", times=1)

    def select_move_item_shelf_location(self) -> str:
        """
        On Move item: read **Current location**, then assign the other shelf (A 24 ↔ A 54).
        """
        self._ensure_current_location_row_visible()
        current_location = self.get_current_location_on_move_item()
        shelf_on_card = self._scan_move_item_for_toggle_shelf()
        if shelf_on_card and self._is_toggle_shelf_key(
            self._normalize_location_key(shelf_on_card)
        ):
            current_location = shelf_on_card

        current_key = self._normalize_location_key(current_location)
        target_label, search_texts = self._toggle_target_for_current(current_location)
        target_key = self._normalize_location_key(target_label)

        if current_key == target_key:
            raise AssertionError(
                f"Current location {current_location!r} matches target {target_label!r}; "
                "assigning the same shelf will fail."
            )

        field = self.tap_item_location_field()

        for search_text in search_texts:
            self._type_into_field(
                field,
                search_text,
                for_suggestions=True,
                suggestion_pattern=self.SHELF_SUGGESTION_RESOURCE_PATTERN,
            )
            self._dismiss_keyboard_for_suggestions()

            for _ in range(4):
                chosen = self._pick_shelf_suggestion_by_key(
                    target_key=target_key,
                    current_location=current_location,
                )
                if chosen:
                    if self._normalize_location_key(chosen) == current_key:
                        raise AssertionError(
                            f"Picked {chosen!r} but Current location is {current_location!r}; "
                            "must choose a different shelf."
                        )
                    time.sleep(0.5)
                    return chosen
                self._scroll_shelf_suggestion_list()

        raise AssertionError(
            f"Could not select {target_label!r} on Move item "
            f"(Current location: {current_location!r}, must not reuse same shelf). "
            f"Tried search texts: {search_texts}."
        )

    def confirm_new_location_change(self) -> None:
        """Complete confirms after picking a new shelf location (modal → success)."""
        self.finish_assignment_after_location_pick()

    def select_available_location(self) -> str:
        """
        Choose a location for whichever post-scan screen is active.
        Returns the selected location label.
        """
        if self.is_on_change_reference_screen():
            return self.select_change_reference_location()
        if self.is_on_move_item_screen():
            return self.select_move_item_shelf_location()
        raise AssertionError(
            "Cannot select location: not on Move item or Change location reference."
        )

    def tap_continue_if_present(self) -> bool:
        buttons = self.driver.find_elements(*self._accessibility(self.CONTINUE_BUTTON_DESC))
        if not buttons:
            return False
        buttons[0].click()
        wait_until(
            self.driver,
            lambda: True if self.is_just_checking_visible() else None,
            timeout=self.wait.timeout,
            message="Just checking screen did not appear after Continue.",
        )
        return True

    def confirm_just_checking_if_present(self) -> bool:
        if not self.is_just_checking_visible():
            return False
        self.wait.until_present(self._resource(self.JUST_CHECKING_CONFIRM_ID)).click()
        return True

    def tap_confirm_final_if_present(self) -> bool:
        if not self.is_confirmation_modal_visible():
            return False
        self.wait.until_present(self._resource(self.CONFIRM_FINAL_BUTTON_ID)).click()
        return True

    def wait_for_assign_success(self) -> None:
        wait_until(
            self.driver,
            lambda: True if self.is_assign_success_visible() else None,
            timeout=self.wait.timeout,
            message=(
                "Success screen did not appear after assigning location "
                "(expected successView or successModal)."
            ),
        )

    def finish_assignment_after_location_pick(self) -> None:
        """Complete downstream confirms for Move item or Change location reference."""
        self._dismiss_keyboard_for_suggestions()
        deadline = time.time() + self.wait.timeout
        while time.time() < deadline:
            if self.is_assign_success_visible():
                return

            if self.is_confirmation_modal_visible():
                self.tap_confirm_final_if_present()
                time.sleep(0.5)
                continue

            if self.is_just_checking_visible():
                self.confirm_just_checking_if_present()
                time.sleep(0.5)
                continue

            continue_buttons = self.driver.find_elements(
                *self._accessibility(self.CONTINUE_BUTTON_DESC)
            )
            if continue_buttons:
                try:
                    if continue_buttons[0].is_displayed():
                        self.tap_continue_if_present()
                        continue
                except Exception:
                    pass

            if self.driver.find_elements(*self._resource(self.CONFIRM_FINAL_BUTTON_ID)):
                self.wait.until_present(self._resource(self.CONFIRM_FINAL_BUTTON_ID)).click()
                time.sleep(0.5)
                continue

            time.sleep(0.3)

        self.wait_for_assign_success()

    def go_to_home(self) -> None:
        if self.is_success_view_visible():
            if self.driver.find_elements(*self._resource(self.GO_HOME_BUTTON_ID)):
                self.wait.until_present(self._resource(self.GO_HOME_BUTTON_ID)).click()
            else:
                self.wait.until_present(self._accessibility(self.GO_HOME_DESC)).click()
        elif self.is_success_modal_visible():
            self.wait.until_present(self._resource(self.GO_TO_LOCATOR_HOME_ID)).click()
        else:
            self.wait.until_present(self._accessibility(self.GO_HOME_DESC)).click()

        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="Home screen did not appear after tapping Go to Home.",
        )

    def execute_full_assign_flow(
        self,
        barcode_image: Path | None = None,
        *,
        timeout: int | None = None,
    ) -> tuple[str, str]:
        """
        End-to-end assign flow. Returns ``(item_id, chosen_location)``.

        1. Item Locator → Assign Item Location
        2. Scan ``barcode_14401.png`` (or override) and confirm
        3. Move item **or** Change location reference → pick available location
        4. Continue / Just checking / Confirm modal (as shown)
        5. Success → Go to Home
        """
        if timeout is not None:
            self.wait = AppiumWait(self.driver, float(timeout))

        self.open_item_locator_from_home()
        self.tap_assign_item_location()
        item_id = self.scan_and_enter_item_number(barcode_image)
        screen_mode = self.confirm_item_number()

        if screen_mode == "assign_reference":
            self.tap_change_from_assign_reference()

        chosen_location = self.select_available_location()
        self.finish_assignment_after_location_pick()
        self.go_to_home()
        return item_id, chosen_location
