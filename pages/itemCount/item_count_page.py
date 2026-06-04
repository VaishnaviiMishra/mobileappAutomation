"""Item Count page object — xmlFiles/itemcount/*.xml."""

from __future__ import annotations

import time
from dataclasses import dataclass

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import AppiumWait, wait_for_present, wait_until
from pages.login.home_page import HomePage


@dataclass(frozen=True)
class CountRowInfo:
    """One selectable count row on the Today's Counts hub."""

    resource_id: str
    label: str
    period: str
    is_completed: bool
    is_checked: bool
    is_enabled: bool
    is_displayed: bool


class ItemCountPage:
    MODULE_TITLE = "Item Count"
    PAGE_TITLE = "Today's Counts"
    INSTRUCTION = "Select the category you want to complete"
    OPENING_SECTION = "Opening count"
    CLOSING_SECTION = "Closing count"

    OPENING_SECTION_ID = "sectionOpeningCount"
    CLOSING_SECTION_ID = "sectionClosingCount"
    COUNT_ROW_PREFIX = "countRow-"

    # Known examples from itemcount.xml (store may show a subset dynamically).
    OPENING_JEWELRY_ID = "countRow-opening-500002"
    OPENING_FIREARMS_ID = "countRow-opening-500003"
    CLOSING_JEWELRY_ID = "countRow-closing-500002"
    CLOSING_FIREARMS_ID = "countRow-closing-500003"

    MANAGE_JEWELRY_CASES_DESC = "Manage jewelry cases"
    MANAGE_JEWELRY_CASES_ID = "manageJewelryCasesLink"

    JEWELRY_CASES_TITLE = "Jewelry cases"
    JEWELRY_CASES_TITLE_ID = "jewelryCasesTitle"
    JEWELRY_CASES_SUBTITLE_ID = "jewelryCasesSubtitle"
    INCREMENT_CASE_COUNT_DESC = "Increase case count"
    INCREMENT_BUTTON_ID = "incrementButton"
    DECREMENT_BUTTON_ID = "decrementButton"
    CASE_COUNT_VALUE_ID = "caseCountValue"

    START_COUNT_DESC = "Start count"
    START_COUNT_ID = "startCountButton"
    EXIT_DESC = "Exit"

    SAVE_AND_FINISH_DESC = "Save and finish"
    SAVE_BUTTON_ID = "saveButton"
    FOOTER_EXIT_BUTTON_ID = "exitButton"

    EXIT_CONFIRM_MODAL_ID = "exitConfirmModal"
    EXIT_CONFIRM_TITLE = "Are you sure you want to exit?"
    EXIT_CONFIRM_BODY = "There are incomplete counts in progress that will not be saved."
    EXIT_CONFIRM_EXIT_BUTTON_ID = "exitConfirmExitButton"
    EXIT_CONFIRM_STAY_BUTTON_ID = "exitConfirmStayButton"

    HUB_MARKER = PAGE_TITLE
    HUB_SCROLL_PAUSE_SECONDS = 0.35

    def __init__(self, driver, home: HomePage, timeout: int = 25) -> None:
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

    def _accessibility(self, desc: str) -> tuple[str, str]:
        return (AppiumBy.ACCESSIBILITY_ID, desc)

    def _count_rows_locator(self) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceIdMatches("{self.COUNT_ROW_PREFIX}.+")',
        )

    def _section_resources_locator(self) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceIdMatches("section.*")',
        )

    # --- Navigation ---

    def ensure_on_home(self) -> None:
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.navigate_to_dashboard_via_menu()

    def open_from_home(self) -> None:
        self.ensure_on_home()
        self.home.item_count_module.click()
        self.wait_for_screen()

    def wait_for_screen(self) -> None:
        wait_for_present(
            self.driver,
            self._text(self.PAGE_TITLE),
            timeout=self.wait.timeout,
            message="Item Count screen (Today's Counts) did not load.",
        )

    def is_on_jewelry_cases_screen(self) -> bool:
        if self.driver.find_elements(*self._resource(self.JEWELRY_CASES_TITLE_ID)):
            return True
        return bool(self.driver.find_elements(*self._text(self.JEWELRY_CASES_TITLE)))

    def is_on_hub_screen(self) -> bool:
        try:
            for el in self.driver.find_elements(*self._text(self.HUB_MARKER)):
                try:
                    if el.is_displayed():
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def is_exit_confirm_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.EXIT_CONFIRM_MODAL_ID)))

    def scroll_hub_down(self) -> None:
        window = self.driver.get_window_size()
        width = int(window["width"])
        height = int(window["height"])
        center_x = width // 2
        top_y = int(height * 0.30)
        bottom_y = int(height * 0.70)
        self.driver.swipe(center_x, bottom_y, center_x, top_y, 500)
        time.sleep(self.HUB_SCROLL_PAUSE_SECONDS)

    def scroll_hub_to_top(self) -> None:
        window = self.driver.get_window_size()
        width = int(window["width"])
        height = int(window["height"])
        center_x = width // 2
        top_y = int(height * 0.30)
        bottom_y = int(height * 0.70)
        for _ in range(4):
            self.driver.swipe(center_x, top_y, center_x, bottom_y, 400)

    # --- Dynamic hub discovery ---

    @staticmethod
    def _period_from_resource_id(resource_id: str) -> str:
        if "-opening-" in resource_id:
            return "opening"
        if "-closing-" in resource_id:
            return "closing"
        return "other"

    @staticmethod
    def _row_shows_completion_indicator(element) -> bool:
        """Completed counts show an inner checkmark (two ViewGroups before the label)."""
        try:
            if element.get_attribute("enabled") != "true":
                return True
        except Exception:
            pass
        try:
            view_groups = element.find_elements(
                AppiumBy.CLASS_NAME, "android.view.ViewGroup"
            )
            return len(view_groups) >= 2
        except Exception:
            return False

    def _read_count_row(self, element) -> CountRowInfo | None:
        try:
            resource_id = (element.get_attribute("resourceId") or "").strip()
        except Exception:
            return None
        if not resource_id.startswith(self.COUNT_ROW_PREFIX):
            return None
        try:
            is_displayed = element.is_displayed()
        except Exception:
            is_displayed = False
        label = (element.get_attribute("content-desc") or element.text or "").strip()
        is_completed = self._row_shows_completion_indicator(element)
        try:
            is_checked = element.get_attribute("checked") == "true"
        except Exception:
            is_checked = False
        try:
            is_enabled = element.get_attribute("enabled") == "true"
        except Exception:
            is_enabled = False
        return CountRowInfo(
            resource_id=resource_id,
            label=label,
            period=self._period_from_resource_id(resource_id),
            is_completed=is_completed,
            is_checked=is_checked,
            is_enabled=is_enabled,
            is_displayed=is_displayed,
        )

    def discover_count_rows(self, *, include_hidden: bool = False) -> list[CountRowInfo]:
        """Return all count rows currently in the UI tree."""
        rows: list[CountRowInfo] = []
        seen: set[str] = set()
        for element in self.driver.find_elements(*self._count_rows_locator()):
            info = self._read_count_row(element)
            if info is None or info.resource_id in seen:
                continue
            seen.add(info.resource_id)
            if include_hidden or info.is_displayed:
                rows.append(info)
        return rows

    def discover_all_count_rows(self) -> list[CountRowInfo]:
        """Collect every count row, scrolling the hub when many tags are present."""
        self.scroll_hub_to_top()
        by_id: dict[str, CountRowInfo] = {}
        stagnant_passes = 0
        for _ in range(8):
            before = len(by_id)
            for row in self.discover_count_rows(include_hidden=True):
                by_id[row.resource_id] = row
            if len(by_id) == before:
                stagnant_passes += 1
                if stagnant_passes >= 2:
                    break
            else:
                stagnant_passes = 0
            self.scroll_hub_down()
        self.scroll_hub_to_top()
        return list(by_id.values())

    def discover_section_labels(self) -> list[str]:
        """Section headings (Opening count, Closing count, or additional tags)."""
        labels: list[str] = []
        seen: set[str] = set()

        for element in self.driver.find_elements(*self._section_resources_locator()):
            try:
                label = (element.text or "").strip()
            except Exception:
                label = ""
            if label and label not in seen:
                seen.add(label)
                labels.append(label)

        for fallback in (self.OPENING_SECTION, self.CLOSING_SECTION):
            if fallback not in seen and self.driver.find_elements(*self._text(fallback)):
                seen.add(fallback)
                labels.append(fallback)

        return labels

    def get_pending_rows(self) -> list[CountRowInfo]:
        """Rows that are not completed and can still be selected."""
        rows = self.discover_all_count_rows()
        pending = [row for row in rows if row.is_enabled and not row.is_completed]
        if not pending:
            pending = [row for row in rows if row.is_enabled and not row.is_checked]
        return pending

    def get_completed_rows(self) -> list[CountRowInfo]:
        return [row for row in self.discover_all_count_rows() if row.is_completed]

    def has_manage_jewelry_cases_link(self) -> bool:
        if self.driver.find_elements(*self._resource(self.MANAGE_JEWELRY_CASES_ID)):
            return True
        return bool(self.driver.find_elements(*self._accessibility(self.MANAGE_JEWELRY_CASES_DESC)))

    def _footer_control_visible(self, locator: tuple[str, str]) -> bool:
        for element in self.driver.find_elements(*locator):
            try:
                if element.is_displayed():
                    return True
            except Exception:
                continue
        return False

    def has_footer_exit_button(self) -> bool:
        return self._footer_control_visible(
            self._resource(self.FOOTER_EXIT_BUTTON_ID)
        ) or self._footer_control_visible(self._accessibility(self.EXIT_DESC))

    def has_footer_start_count_button(self) -> bool:
        return self._footer_control_visible(
            self._resource(self.START_COUNT_ID)
        ) or self._footer_control_visible(self._accessibility(self.START_COUNT_DESC))

    def ensure_hub_footer_visible(self) -> None:
        """Scroll until footer actions (Start count / Exit) are on screen."""
        if self.has_footer_start_count_button() and self.has_footer_exit_button():
            return
        for _ in range(4):
            if self.has_footer_start_count_button():
                return
            self.scroll_hub_down()
        self.scroll_hub_to_top()

    def verify_hub_layout(self) -> dict[str, object]:
        """
        Verify hub UI for any store layout: variable sections, rows, and optional links.
        Returns a snapshot of what was found for tests to assert on.
        """
        self.scroll_hub_to_top()

        wait_for_present(self.driver, self._text(self.PAGE_TITLE), timeout=self.wait.timeout)
        wait_for_present(self.driver, self._text(self.INSTRUCTION), timeout=self.wait.timeout)

        sections = self.discover_section_labels()
        if not sections:
            raise AssertionError("No count section headings found on Item Count hub.")

        rows = self.discover_all_count_rows()
        if not rows:
            raise AssertionError("No count rows found on Item Count hub.")

        self.ensure_hub_footer_visible()
        wait_for_present(
            self.driver,
            self._accessibility(self.START_COUNT_DESC),
            timeout=self.wait.timeout,
            message=f"Footer button {self.START_COUNT_DESC!r} not found.",
        )
        has_footer_exit = self.has_footer_exit_button()
        if has_footer_exit:
            wait_for_present(
                self.driver,
                self._accessibility(self.EXIT_DESC),
                timeout=self.wait.timeout,
                message=f"Footer button {self.EXIT_DESC!r} not found.",
            )

        snapshot: dict[str, object] = {
            "sections": sections,
            "rows": rows,
            "pending": self.get_pending_rows(),
            "completed": self.get_completed_rows(),
            "has_manage_jewelry": self.has_manage_jewelry_cases_link(),
            "has_footer_exit": has_footer_exit,
        }
        return snapshot

    def return_to_hub(self) -> None:
        if self.is_on_hub_screen():
            return
        save_btns = self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, self.SAVE_AND_FINISH_DESC)
        if save_btns:
            save_btns[0].click()
            wait_until(
                self.driver,
                lambda: True if self.is_on_hub_screen() else None,
                timeout=self.wait.timeout,
                message="Item Count hub did not appear after tapping Save and finish.",
            )
            return
        try:
            self.home.hamburger_button.click()
            wait_for_present(
                self.driver,
                (AppiumBy.ACCESSIBILITY_ID, self.MODULE_TITLE),
                timeout=self.wait.timeout,
                message="Hamburger menu did not show Item Count option.",
            )
            self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, self.MODULE_TITLE).click()
        except Exception:
            for _ in range(4):
                if self.is_on_hub_screen():
                    return
                self.driver.press_keycode(4)
        wait_until(
            self.driver,
            lambda: True if self.is_on_hub_screen() else None,
            timeout=self.wait.timeout,
            message="Could not return to Item Count hub after sub-navigation.",
        )

    # --- Element accessors ---

    def get_hamburger_button(self):
        return self.home.hamburger_button

    def get_module_title(self):
        return self.wait.until_present(self._text(self.MODULE_TITLE))

    def get_page_title(self):
        return self.wait.until_present(self._text(self.PAGE_TITLE))

    def get_instruction(self):
        return self.wait.until_present(self._text(self.INSTRUCTION))

    def get_opening_section(self):
        return self.wait.until_present(self._resource(self.OPENING_SECTION_ID))

    def get_closing_section(self):
        return self.wait.until_present(self._resource(self.CLOSING_SECTION_ID))

    def get_radio_row(self, resource_id: str):
        return self.wait.until_present(self._resource(resource_id))

    def get_footer_button(self, accessibility_desc: str):
        if accessibility_desc in (self.START_COUNT_DESC, self.EXIT_DESC):
            self.ensure_hub_footer_visible()
        return self.wait.until_present(self._accessibility(accessibility_desc))

    def get_manage_jewelry_cases_link(self):
        if self.driver.find_elements(*self._resource(self.MANAGE_JEWELRY_CASES_ID)):
            return self.wait.until_present(self._resource(self.MANAGE_JEWELRY_CASES_ID))
        return self.wait.until_present(self._accessibility(self.MANAGE_JEWELRY_CASES_DESC))

    def get_increment_button(self):
        if self.driver.find_elements(*self._resource(self.INCREMENT_BUTTON_ID)):
            return self.wait.until_present(self._resource(self.INCREMENT_BUTTON_ID))
        return self.wait.until_present(self._accessibility(self.INCREMENT_CASE_COUNT_DESC))

    def get_case_count_value_element(self):
        return self.wait.until_present(self._resource(self.CASE_COUNT_VALUE_ID))

    def get_jewelry_cases_save_button(self):
        if self.driver.find_elements(*self._resource(self.SAVE_BUTTON_ID)):
            return self.wait.until_present(self._resource(self.SAVE_BUTTON_ID))
        return self.wait.until_present(self._accessibility(self.SAVE_AND_FINISH_DESC))

    def get_exit_confirm_title(self):
        return self.wait.until_present(self._text(self.EXIT_CONFIRM_TITLE))

    def get_exit_confirm_body(self):
        return self.wait.until_present(self._text(self.EXIT_CONFIRM_BODY))

    def get_exit_confirm_stay_button(self):
        return self.wait.until_present(self._resource(self.EXIT_CONFIRM_STAY_BUTTON_ID))

    def get_exit_confirm_exit_button(self):
        return self.wait.until_present(self._resource(self.EXIT_CONFIRM_EXIT_BUTTON_ID))

    # --- Actions ---

    def select_radio(self, resource_id: str) -> None:
        row = self.get_radio_row(resource_id)
        if row.get_attribute("enabled") != "true":
            raise AssertionError(f"Count row {resource_id!r} is not enabled for selection.")
        row.click()
        wait_until(
            self.driver,
            lambda: self.get_radio_row(resource_id).get_attribute("checked") == "true",
            timeout=self.wait.timeout,
            message=f"Radio {resource_id} was not selected after tap.",
        )

    def select_all_pending_rows(self) -> list[str]:
        """Select every incomplete row (works for 1-row image layout or multi-tag stores)."""
        pending = self.get_pending_rows()
        if not pending:
            self.scroll_hub_down()
            pending = self.get_pending_rows()
        if not pending:
            raise AssertionError("No pending count rows available to select.")
        selected: list[str] = []
        for row in pending:
            self.select_radio(row.resource_id)
            selected.append(row.resource_id)
        return selected

    def select_first_pending_row(self) -> str:
        """Select the first incomplete count row (e.g. Closing Jewelry on image scenario)."""
        pending = self.get_pending_rows()
        if not pending:
            self.scroll_hub_down()
            pending = self.get_pending_rows()
        if not pending:
            raise AssertionError("No pending count rows available to select.")
        self.select_radio(pending[0].resource_id)
        return pending[0].resource_id

    def select_row_by_label(self, label: str, *, period: str | None = None) -> str:
        """Select a row matching label and optional period (opening/closing)."""
        matches = [
            row
            for row in self.get_pending_rows()
            if row.label.lower() == label.lower()
            and (period is None or row.period == period)
        ]
        if not matches:
            raise AssertionError(
                f"No pending count row for label {label!r}"
                + (f" in period {period!r}" if period else "")
                + "."
            )
        self.select_radio(matches[0].resource_id)
        return matches[0].resource_id

    def wait_for_jewelry_cases_screen(self) -> None:
        wait_for_present(
            self.driver,
            self._resource(self.JEWELRY_CASES_TITLE_ID),
            timeout=self.wait.timeout,
            message="Jewelry cases screen did not load.",
        )

    def open_manage_jewelry_cases(self) -> None:
        """Hub → Manage jewelry cases."""
        self.ensure_hub_footer_visible()
        if not self.has_manage_jewelry_cases_link():
            raise AssertionError("Manage jewelry cases link is not available on this layout.")
        self.get_manage_jewelry_cases_link().click()
        self.wait_for_jewelry_cases_screen()

    def get_case_count_value(self) -> int:
        return int(self.get_case_count_value_element().text.strip())

    def tap_increment_case_count(self, times: int = 1) -> int:
        """Tap + to increase the jewelry case count."""
        before = self.get_case_count_value()
        for _ in range(times):
            self.get_increment_button().click()
        after = self.get_case_count_value()
        if after <= before:
            raise AssertionError(
                f"Case count did not increase after tapping + (before={before}, after={after})."
            )
        return after

    def tap_save_and_finish_jewelry_cases(self) -> None:
        """Save on Jewelry cases and wait for Today's Counts hub."""
        self.get_jewelry_cases_save_button().click()
        wait_until(
            self.driver,
            lambda: True if self.is_on_hub_screen() else None,
            timeout=self.wait.timeout,
            message="Item Count hub (Today's Counts) did not appear after Save and finish.",
        )

    def complete_manage_jewelry_cases_flow(self) -> int:
        """
        Manage jewelry cases → tap + → Save and finish → return to hub.
        Returns the new case count value.
        """
        self.open_manage_jewelry_cases()
        new_count = self.tap_increment_case_count()
        self.tap_save_and_finish_jewelry_cases()
        if not self.is_on_hub_screen():
            raise AssertionError("Expected to return to Item Count hub after saving jewelry cases.")
        return new_count

    def tap_start_count(self) -> None:
        self.get_footer_button(self.START_COUNT_DESC).click()
        wait_until(
            self.driver,
            lambda: True if not self.is_on_hub_screen() else None,
            timeout=self.wait.timeout,
            message='"Start count" did not navigate away from Item Count hub.',
        )

    def tap_exit(self) -> None:
        self.ensure_hub_footer_visible()
        if self.driver.find_elements(*self._resource(self.FOOTER_EXIT_BUTTON_ID)):
            self.wait.until_present(self._resource(self.FOOTER_EXIT_BUTTON_ID)).click()
        else:
            self.wait.until_present(self._accessibility(self.EXIT_DESC)).click()
        wait_until(
            self.driver,
            lambda: True if self.is_exit_confirm_visible() else None,
            timeout=self.wait.timeout,
            message="Exit confirmation dialog did not appear after footer Exit.",
        )

    def confirm_exit(self) -> None:
        self.get_exit_confirm_exit_button().click()
        wait_until(
            self.driver,
            lambda: True if not self.is_exit_confirm_visible() else None,
            timeout=self.wait.timeout,
            message="Exit confirmation modal did not close after tapping Exit.",
        )

    def exit_to_home(self) -> None:
        if self.is_on_hub_screen() and self.has_footer_exit_button():
            self.tap_exit()
            self.confirm_exit()
        else:
            self.home.return_to_home()
        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="MODULES dashboard did not appear after exiting Item Count.",
        )
