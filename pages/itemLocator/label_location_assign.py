"""Setup Location flow — scan QR label, change location reference, confirm.

Full flow:
    1. Item Locator hub → Setup Location
    2. Scan label (camera + QR on host screen)
    3. Assign location reference → tap **Change**
    4. Change location reference → read **CURRENT LABEL**, tap ``locationNameInput``,
       type ``J``, pick from ``locationSuggestions`` (any option ≠ current), **Continue**
    5. Just checking → ``justCheckingConfirmButton``
    6. Confirmation modal → ``confirmFinalButton``
    7. Success modal → Go to Home
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

# #region agent log
_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / ".cursor" / "debug-c68c63.log"


def _agent_log(
    *,
    location: str,
    message: str,
    data: dict,
    hypothesis_id: str,
    run_id: str = "run1",
) -> None:
    try:
        payload = {
            "sessionId": "c68c63",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with _DEBUG_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
    except Exception:
        pass


# #endregion

from appium.webdriver.common.appiumby import AppiumBy

from pages.common import adb_helper
from pages.common.appium_wait import AppiumWait, wait_for_present, wait_until
from pages.login.home_page import HomePage

DEFAULT_LABEL_IMAGE = Path(__file__).resolve().parent.parent / "common" / "label.png"
SCAN_WAIT_TIMEOUT = 120.0
LOCATION_SEARCH_LETTER = "J"

# Example labels seen in store XML; current label is read dynamically at runtime.
LOCATION_CANDIDATES = ["JC", "J-03", "J-04", "END-J", "BACK JEWELRY SAFE"]

SUGGESTION_RESOURCE_PATTERN = "suggestion-.*"


class LabelLocationAssignPage:
    APP_PACKAGE = "com.ezpawnpal"
    DEFAULT_FLOW_TIMEOUT = 90

    SETUP_BUTTON_ID = "setupLocationButton"
    SETUP_TITLE = "Set up location"

    ASSIGN_REF_TITLE = "Assign location reference"
    CURRENT_LABEL_TEXT = "CURRENT LABEL"
    CURRENT_LABEL_BADGE_ID = "currentLabelBadge"
    CHANGE_BUTTON_ID = "changeButton"

    CHANGE_REF_TITLE = "Change location reference"
    TYPE_LOCATION_REF_LABEL = "Type location reference"
    ASSIGN_TITLE_ROW_ID = "assignTitleRow"
    LOCATION_NAME_INPUT_ID = "locationNameInput"
    LOCATION_SUGGESTIONS_ID = "locationSuggestions"
    CONTINUE_BUTTON_DESC = "Continue"

    JUST_CHECKING_TITLE_ID = "justCheckingTitle"
    JUST_CHECKING_CONFIRM_ID = "justCheckingConfirmButton"

    CONFIRMATION_MODAL_ID = "confirmationModal"
    CONFIRM_FINAL_BUTTON_ID = "confirmFinalButton"

    SUCCESS_MODAL_ID = "successModal"
    GO_HOME_BUTTON_ID = "goToLocatorHomeButton"

    HUB_SUBTITLE = "What would you like to do?"
    SCROLL_PAUSE_SECONDS = 0.35

    def __init__(self, driver, home: HomePage, timeout: int = DEFAULT_FLOW_TIMEOUT) -> None:
        self.driver = driver
        self.home = home
        self.wait = AppiumWait(driver, float(timeout))

    def _text(self, label: str) -> tuple[str, str]:
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{label}")')

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

    def _device_udid(self) -> str | None:
        return (
            self.driver.capabilities.get("appium:udid")
            or self.driver.capabilities.get("udid")
        )

    def _dismiss_keyboard_for_suggestions(self) -> None:
        """
        Hide keyboard without ``tapOutside`` — that often taps the hamburger (top-left).
        """
        # #region agent log
        _agent_log(
            location="label_location_assign.py:_dismiss_keyboard_for_suggestions",
            message="dismiss keyboard (safe)",
            data={"on_change_ref": self.is_on_change_reference()},
            hypothesis_id="H5",
        )
        # #endregion

        for locator in (
            self._text(self.TYPE_LOCATION_REF_LABEL),
            self._resource(self.LOCATION_NAME_INPUT_ID),
            self._text(self.CHANGE_REF_TITLE),
        ):
            elements = self.driver.find_elements(*locator)
            if elements:
                try:
                    elements[0].click()
                    time.sleep(0.3)
                    break
                except Exception:
                    continue

        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard(strategy="swipeDown")
                time.sleep(0.3)
        except Exception:
            pass

    def ensure_on_home(self) -> None:
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.return_to_home()

    def open_item_locator_from_home(self) -> None:
        self.ensure_on_home()
        self.home.item_locator_module.click()
        wait_for_present(
            self.driver,
            self._text(self.HUB_SUBTITLE),
            timeout=self.wait.timeout,
            message="Item Locator hub did not load.",
        )

    def tap_setup_location(self) -> None:
        self.wait.until_present(self._resource(self.SETUP_BUTTON_ID)).click()
        wait_for_present(
            self.driver,
            self._text(self.SETUP_TITLE),
            timeout=self.wait.timeout,
            message="Setup Location scan screen did not appear.",
        )

    def is_on_scan_screen(self) -> bool:
        try:
            for el in self.driver.find_elements(*self._text(self.SETUP_TITLE)):
                if el.is_displayed():
                    return True
        except Exception:
            pass
        return False

    def is_on_assign_reference(self) -> bool:
        try:
            for el in self.driver.find_elements(*self._text(self.ASSIGN_REF_TITLE)):
                if el.is_displayed():
                    return True
        except Exception:
            pass
        return False

    def is_on_change_reference(self) -> bool:
        try:
            for el in self.driver.find_elements(*self._text(self.CHANGE_REF_TITLE)):
                if el.is_displayed():
                    return True
        except Exception:
            pass
        return False

    def _left_scan_screen(self) -> bool:
        return self.is_on_assign_reference() or self.is_on_change_reference()

    @staticmethod
    def _open_label_fullscreen(image: Path | None = None) -> subprocess.Popen | None:
        path = (image or DEFAULT_LABEL_IMAGE).resolve()
        if not path.is_file():
            return None
        try:
            return subprocess.Popen(
                ["eog", "--fullscreen", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            return None

    @staticmethod
    def _close_label_viewer(proc: subprocess.Popen | None) -> None:
        if proc is None:
            return
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    def wait_for_scan(
        self,
        timeout: float = SCAN_WAIT_TIMEOUT,
        label_image: Path | None = None,
    ) -> None:
        if self._left_scan_screen():
            return

        viewer = self._open_label_fullscreen(label_image)
        try:
            wait_until(
                self.driver,
                lambda: True if self._left_scan_screen() else None,
                timeout=timeout,
                poll=1.0,
                message=(
                    f"QR scan did not complete within {timeout}s. "
                    "Ensure the device camera can see the QR on the host screen."
                ),
            )
        finally:
            self._close_label_viewer(viewer)

    @staticmethod
    def _normalize_label_key(name: str) -> str:
        return re.sub(r"[\s\-–]+", "", (name or "")).upper()

    def get_current_label_value(self) -> str:
        """
        Read the location name next to **CURRENT LABEL**.

        Layout: ``changeLocationrRef.xml`` / ``locationoptions.xml`` — value TextView
        (e.g. ``J-03``) sits beside ``CURRENT LABEL`` under ``assignTitleRow``.
        """
        wait_for_present(
            self.driver,
            self._text(self.CURRENT_LABEL_TEXT),
            timeout=self.wait.timeout,
            message="CURRENT LABEL heading not found on Change location reference.",
        )

        skip_texts = {
            self.CURRENT_LABEL_TEXT,
            self.CHANGE_REF_TITLE,
            self.TYPE_LOCATION_REF_LABEL,
            self.ASSIGN_REF_TITLE,
        }

        for label_el in self.driver.find_elements(*self._text(self.CURRENT_LABEL_TEXT)):
            try:
                value_el = label_el.find_element(
                    AppiumBy.XPATH,
                    "./following-sibling::android.widget.TextView[1]",
                )
                text = (value_el.text or "").strip()
                if text and text not in skip_texts:
                    # #region agent log
                    _agent_log(
                        location="label_location_assign.py:get_current_label_value",
                        message="current label from sibling",
                        data={"label": text},
                        hypothesis_id="H2",
                    )
                    # #endregion
                    return text
            except Exception:
                pass

            try:
                parent = label_el.find_element(AppiumBy.XPATH, "..")
                after_heading = False
                for tv in parent.find_elements(
                    AppiumBy.CLASS_NAME, "android.widget.TextView"
                ):
                    text = (tv.text or "").strip()
                    if text == self.CURRENT_LABEL_TEXT:
                        after_heading = True
                        continue
                    if after_heading and text and text not in skip_texts:
                        # #region agent log
                        _agent_log(
                            location="label_location_assign.py:get_current_label_value",
                            message="current label from parent walk",
                            data={"label": text},
                            hypothesis_id="H2",
                        )
                        # #endregion
                        return text
            except Exception:
                pass

        if self.driver.find_elements(*self._resource(self.ASSIGN_TITLE_ROW_ID)):
            try:
                row = self.driver.find_element(*self._resource(self.ASSIGN_TITLE_ROW_ID))
                for tv in row.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"):
                    text = (tv.text or "").strip()
                    if text and text not in skip_texts:
                        # #region agent log
                        _agent_log(
                            location="label_location_assign.py:get_current_label_value",
                            message="current label from assignTitleRow",
                            data={"label": text},
                            hypothesis_id="H2",
                        )
                        # #endregion
                        return text
            except Exception:
                pass

        try:
            for tv in self.driver.find_elements(
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="CURRENT LABEL"]'
                "/following-sibling::android.widget.TextView[1]",
            ):
                text = (tv.text or "").strip()
                if text and text not in skip_texts:
                    # #region agent log
                    _agent_log(
                        location="label_location_assign.py:get_current_label_value",
                        message="current label from global xpath",
                        data={"label": text},
                        hypothesis_id="H2",
                    )
                    # #endregion
                    return text
        except Exception:
            pass

        # #region agent log
        _agent_log(
            location="label_location_assign.py:get_current_label_value",
            message="current label not found",
            data={},
            hypothesis_id="H2",
        )
        # #endregion
        return ""

    def find_current_label_in_suggestions(self) -> str | None:
        """Return the suggestion label marked **Current** in ``content-desc``."""
        for element in self.driver.find_elements(
            *self._resource_matches(SUGGESTION_RESOURCE_PATTERN)
        ):
            try:
                desc = (element.get_attribute("content-desc") or "").strip()
            except Exception:
                continue
            if "current" not in desc.lower():
                continue
            resource_id = (element.get_attribute("resourceId") or "").strip()
            label = self._label_from_suggestion(desc, resource_id)
            if label:
                return label
        return None

    @staticmethod
    def _label_from_suggestion(content_desc: str, resource_id: str) -> str:
        if content_desc:
            return content_desc.split(",")[0].strip()
        prefix = "suggestion-"
        if resource_id.startswith(prefix):
            return resource_id[len(prefix) :].strip()
        return ""

    def _is_unavailable_suggestion(
        self,
        *,
        content_desc: str,
        label: str,
        current_label: str,
    ) -> bool:
        parts = [p.strip().lower() for p in (content_desc or "").split(",")]
        if "current" in parts:
            return True
        label_key = self._normalize_label_key(label)
        if current_label and label_key == self._normalize_label_key(current_label):
            return True
        return False

    def _collect_reference_suggestions(self) -> list[Any]:
        """Collect ``suggestion-*`` radios inside ``locationSuggestions`` (locationoptions.xml)."""
        seen: set[str] = set()
        elements: list[Any] = []
        roots: list[Any] = [self.driver]
        if self.driver.find_elements(*self._resource(self.LOCATION_SUGGESTIONS_ID)):
            try:
                roots = [
                    self.driver.find_element(*self._resource(self.LOCATION_SUGGESTIONS_ID))
                ]
            except Exception:
                pass

        for root in roots:
            for element in root.find_elements(*self._resource_matches(SUGGESTION_RESOURCE_PATTERN)):
                try:
                    resource_id = (element.get_attribute("resourceId") or "").strip()
                except Exception:
                    continue
                if not resource_id or resource_id in seen:
                    continue
                seen.add(resource_id)
                try:
                    if element.is_enabled():
                        elements.append(element)
                except Exception:
                    continue
        return elements

    def _wait_for_location_suggestions(self) -> None:
        """Wait for the dropdown list below the input (``locationoptions.xml`` index 8)."""
        wait_for_present(
            self.driver,
            self._resource(self.LOCATION_SUGGESTIONS_ID),
            timeout=self.wait.timeout,
            message=(
                "locationSuggestions list did not appear below locationNameInput "
                f"after typing {LOCATION_SEARCH_LETTER!r}."
            ),
        )
        wait_for_present(
            self.driver,
            self._resource_matches(SUGGESTION_RESOURCE_PATTERN),
            timeout=15,
            message="No suggestion-* radio buttons inside locationSuggestions.",
        )
        # #region agent log
        _agent_log(
            location="label_location_assign.py:_wait_for_location_suggestions",
            message="suggestions visible",
            data={"count": len(self._collect_reference_suggestions())},
            hypothesis_id="H6",
        )
        # #endregion

    def _scroll_reference_suggestions(self) -> None:
        if self.driver.find_elements(*self._resource(self.LOCATION_SUGGESTIONS_ID)):
            try:
                container = self.driver.find_element(
                    *self._resource(self.LOCATION_SUGGESTIONS_ID)
                )
                rect = container.rect
                cx = rect["x"] + rect["width"] // 2
                self.driver.swipe(
                    cx,
                    rect["y"] + int(rect["height"] * 0.8),
                    cx,
                    rect["y"] + int(rect["height"] * 0.2),
                    400,
                )
                time.sleep(self.SCROLL_PAUSE_SECONDS)
                return
            except Exception:
                pass
        window = self.driver.get_window_size()
        cx = window["width"] // 2
        self.driver.swipe(cx, int(window["height"] * 0.65), cx, int(window["height"] * 0.45), 400)
        time.sleep(self.SCROLL_PAUSE_SECONDS)

    def _pick_first_available_suggestion(self, current_label: str) -> str:
        """Pick the first ``locationSuggestions`` row that is not the current label."""
        for element in self._collect_reference_suggestions():
            resource_id = (element.get_attribute("resourceId") or "").strip()
            content_desc = (element.get_attribute("content-desc") or "").strip()
            label = self._label_from_suggestion(content_desc, resource_id)
            if not label:
                continue
            if self._is_unavailable_suggestion(
                content_desc=content_desc,
                label=label,
                current_label=current_label,
            ):
                continue
            element.click()
            return label
        return ""

    _pick_first_different_suggestion = _pick_first_available_suggestion

    def tap_location_name_input(self) -> Any:
        """
        Tap ``locationNameInput`` (``locationoptions.xml`` — EditText under
        ``Type location reference``).
        """
        wait_for_present(
            self.driver,
            self._text(self.TYPE_LOCATION_REF_LABEL),
            timeout=self.wait.timeout,
            message="Type location reference label not found.",
        )
        field = self.wait.until_present(self._resource(self.LOCATION_NAME_INPUT_ID))
        field.click()
        time.sleep(0.4)
        # #region agent log
        _agent_log(
            location="label_location_assign.py:tap_location_name_input",
            message="clicked locationNameInput",
            data={"resource_id": self.LOCATION_NAME_INPUT_ID},
            hypothesis_id="H5",
        )
        # #endregion
        return field

    def type_j_and_show_suggestions(self) -> None:
        """Click input, type ``J``, wait for ``locationSuggestions`` dropdown."""
        field = self.tap_location_name_input()
        try:
            field.clear()
        except Exception:
            pass
        try:
            field.send_keys(LOCATION_SEARCH_LETTER)
        except Exception:
            adb_helper.input_text(LOCATION_SEARCH_LETTER, udid=self._device_udid())
        time.sleep(0.6)

        try:
            self._wait_for_location_suggestions()
        except Exception:
            self._dismiss_keyboard_for_suggestions()
            self._wait_for_location_suggestions()

    def tap_change(self) -> None:
        self.wait.until_present(self._resource(self.CHANGE_BUTTON_ID)).click()
        wait_for_present(
            self.driver,
            self._text(self.CHANGE_REF_TITLE),
            timeout=self.wait.timeout,
            message="Change location reference screen did not appear.",
        )
        wait_for_present(
            self.driver,
            self._resource(self.LOCATION_NAME_INPUT_ID),
            timeout=self.wait.timeout,
            message="locationNameInput not found on Change location reference.",
        )

    def select_different_location(self, current_label: str) -> str:
        """
        ``locationoptions.xml``: tap ``locationNameInput`` → type ``J`` →
        ``locationSuggestions`` → pick any available row ≠ current label.
        """
        if not (current_label or "").strip():
            current_label = self.get_current_label_value()

        current_key = self._normalize_label_key(current_label)
        # #region agent log
        _agent_log(
            location="label_location_assign.py:select_different_location",
            message="before type J",
            data={"current_label": current_label, "current_key": current_key},
            hypothesis_id="H2",
        )
        # #endregion

        self.type_j_and_show_suggestions()

        tagged_current = self.find_current_label_in_suggestions()
        if tagged_current:
            current_label = tagged_current
            current_key = self._normalize_label_key(current_label)

        for attempt in range(5):
            chosen = self._pick_first_available_suggestion(current_label)
            if chosen:
                chosen_key = self._normalize_label_key(chosen)
                if current_key and chosen_key == current_key:
                    self._scroll_reference_suggestions()
                    continue
                # #region agent log
                _agent_log(
                    location="label_location_assign.py:select_different_location",
                    message="picked available label",
                    data={
                        "chosen": chosen,
                        "chosen_key": chosen_key,
                        "current_label": current_label,
                        "attempt": attempt,
                    },
                    hypothesis_id="H3",
                )
                # #endregion
                time.sleep(0.5)
                self._dismiss_keyboard_for_suggestions()
                self.wait.until_present(
                    self._accessibility(self.CONTINUE_BUTTON_DESC)
                ).click()
                wait_for_present(
                    self.driver,
                    self._resource(self.JUST_CHECKING_TITLE_ID),
                    timeout=self.wait.timeout,
                    message="Just checking screen did not appear after Continue.",
                )
                return chosen
            self._scroll_reference_suggestions()

        # #region agent log
        _agent_log(
            location="label_location_assign.py:select_different_location",
            message="no available suggestion found",
            data={"current_label": current_label},
            hypothesis_id="H4",
        )
        # #endregion
        raise AssertionError(
            f"No available location in locationSuggestions "
            f"(current label: {current_label!r}, typed {LOCATION_SEARCH_LETTER!r})."
        )

    def confirm_just_checking(self) -> None:
        self.wait.until_present(self._resource(self.JUST_CHECKING_CONFIRM_ID)).click()

    def confirm_final_popup(self) -> None:
        confirm_btn = wait_for_present(
            self.driver,
            self._resource(self.CONFIRM_FINAL_BUTTON_ID),
            timeout=self.wait.timeout,
            message="Final confirmation popup did not appear.",
        )
        confirm_btn.click()

    def tap_go_to_home(self) -> None:
        wait_for_present(
            self.driver,
            self._resource(self.SUCCESS_MODAL_ID),
            timeout=self.wait.timeout,
            message="Success modal did not appear.",
        )
        self.wait.until_present(self._resource(self.GO_HOME_BUTTON_ID)).click()
        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="Home screen did not appear after tapping Go to Home.",
        )

    def back_to_home(self) -> None:
        while not self.home.is_home_visible():
            self.driver.press_keycode(4)
        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="Back did not return to home from Setup Location flow.",
        )

    def execute_full_setup_flow(
        self,
        scan_timeout: float = SCAN_WAIT_TIMEOUT,
        *,
        flow_timeout: int | None = None,
    ) -> str:
        if flow_timeout is not None:
            self.wait = AppiumWait(self.driver, float(flow_timeout))

        self.open_item_locator_from_home()
        self.tap_setup_location()
        self.wait_for_scan(timeout=scan_timeout)

        if self.is_on_assign_reference():
            self.tap_change()
        elif not self.is_on_change_reference():
            self.tap_change()

        current_label = self.get_current_label_value()
        # #region agent log
        _agent_log(
            location="label_location_assign.py:execute_full_setup_flow",
            message="after tap_change",
            data={"current_label": current_label},
            hypothesis_id="H2",
        )
        # #endregion
        chosen = self.select_different_location(current_label)
        self.confirm_just_checking()
        self.confirm_final_popup()
        self.tap_go_to_home()
        return chosen
