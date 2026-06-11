"""Login and Store Location Setup (IP) page object — xmlFiles/login.xml & ipaddress.xml."""

from __future__ import annotations

import time
from typing import Any

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import AppiumWait, AppiumWaitTimeout, wait_for_present
from pages.login.home_page import HomePage


class LoginPage:
    APP_PACKAGE = "com.ezpawnpal"

    # Login screen (login.xml)
    HEADER_TITLE = "Mobile Item Manager"
    STG_ENV_BADGE = "STG ENVIRONMENT"
    LOGIN_TITLE = "Log in"
    LOGIN_SUBTITLE = "Enter your credentials to continue"
    EMPLOYEE_ID_LABEL = "Employee ID"
    PASSWORD_LABEL = "Password"
    EMPLOYEE_HINT = "Enter Employee EzId"
    PASSWORD_HINT = "Enter your password"
    APP_VERSION_FOOTER = "App version 1.0.0 · STG"

    # IP modal (ipaddress.xml)
    IP_MODAL_ENV_BADGE = "NON-PRODUCTION ENVIRONMENT"
    IP_MODAL_TITLE = "Store Location Setup"
    IP_MODAL_INSTRUCTION = (
        "Enter the IP address of this device to automatically detect the store location."
    )
    IP_ADDRESS_LABEL = "IP Address"

    def __init__(self, driver, timeout: int = 25) -> None:
        self.driver = driver
        self.wait = AppiumWait(driver, float(timeout))

    # --- Navigation ---

    def launch_app(self) -> None:
        self.driver.press_keycode(3)  # HOME
        try:
            self.driver.terminate_app(self.APP_PACKAGE)
        except Exception:
            pass
        self.driver.activate_app(self.APP_PACKAGE)
        time.sleep(2)
        self.wait_for_login_screen()

    def wait_for_login_screen(self) -> None:
        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, "Employee ID"),
            timeout=self.wait.timeout,
            message="Login screen (Employee ID field) did not appear.",
        )

    # --- Login element accessors ---

    @property
    def header_title(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.HEADER_TITLE}")')
        )

    @property
    def stg_environment_badge(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.STG_ENV_BADGE}")')
        )

    @property
    def login_title(self):
        return self.wait.until_present(
            (AppiumBy.XPATH, '(//android.widget.TextView[@text="Log in"])[1]')
        )

    @property
    def login_subtitle(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.LOGIN_SUBTITLE}")')
        )

    @property
    def employee_id_label(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.EMPLOYEE_ID_LABEL}")')
        )

    @property
    def employee_id_input(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, "Employee ID"))

    @property
    def password_label(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.PASSWORD_LABEL}")')
        )

    @property
    def password_input(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, "Password"))

    @property
    def show_password_toggle(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, "Show password"))

    @property
    def login_button(self):
        return self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, "Log In"))

    @property
    def app_version_footer(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.APP_VERSION_FOOTER}")')
        )

    # --- IP modal element accessors ---

    @property
    def ip_modal_root(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.IP_MODAL_TITLE}")')
        )

    @property
    def ip_environment_badge(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.IP_MODAL_ENV_BADGE}")')
        )

    @property
    def ip_modal_title(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.IP_MODAL_TITLE}")')
        )

    @property
    def ip_modal_instruction(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.IP_MODAL_INSTRUCTION}")')
        )

    @property
    def ip_address_label(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.IP_ADDRESS_LABEL}")')
        )

    @property
    def ip_address_input(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, "IP Address"))

    @property
    def ip_continue_button(self):
        return self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, "Continue"))

    # --- Actions ---

    def enter_credentials(self, employee_id: str, password: str) -> None:
        employee_field = self.employee_id_input
        employee_field.click()
        employee_field.clear()
        employee_field.send_keys(employee_id)
        self._dismiss_keyboard_if_visible()

        password_field = self.password_input
        password_field.click()
        password_field.clear()
        password_field.send_keys(password)
        self._dismiss_keyboard_if_visible()

    def click_log_in(self) -> None:
        self.login_button.click()

    def wait_for_ip_modal(self) -> None:
        wait_for_present(
            self.driver,
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.IP_MODAL_TITLE}")'),
            timeout=30,
            message="Store Location Setup modal did not appear after login.",
        )

    def ensure_ip_address_and_continue(self, expected_ip: str) -> None:
        field = self.ip_address_input
        current = self._read_field_text(field)
        if current != expected_ip:
            field.click()
            time.sleep(0.2)
            field = self.ip_address_input
            field.clear()
            field.send_keys(expected_ip)
            current = self._read_field_text(self.ip_address_input)
            if current != expected_ip:
                raise AppiumWaitTimeout(
                    f"IP field expected {expected_ip!r} after entry, got {current!r}."
                )
        self.ip_continue_button.click()
        self._wait_for_ip_modal_dismissed()

    def read_ip_field_value(self) -> str:
        return self._read_field_text(self.ip_address_input)

    def complete_login_flow(
        self,
        employee_id: str,
        password: str,
        ip_address: str,
        home: HomePage | None = None,
    ) -> str | None:
        """
        Launch app → login screen → credentials → IP modal → Continue.

        When ``home`` is passed, also handles the post-login Data Sync popup
        (wait for downloads → Close) or direct home navigation.
        Returns ``"data_sync"``, ``"home"``, or ``None`` if ``home`` was omitted.
        """
        self.launch_app()
        self.enter_credentials(employee_id, password)
        self.click_log_in()
        self.wait_for_ip_modal()
        self.ensure_ip_address_and_continue(ip_address)
        if home is None:
            return None
        return home.handle_post_login_either_path()

    # --- Helpers ---

    _FIELD_HINTS = frozenset(
        {"Enter Employee EzId", "Enter your password", "e.g. 192.168.1.100"}
    )
    _FIELD_LABELS = frozenset({"Employee ID", "Password", "IP Address"})

    @classmethod
    def _read_field_text(cls, element: Any) -> str:
        text = (element.text or "").strip()
        if text and text not in cls._FIELD_HINTS and text not in cls._FIELD_LABELS:
            return text
        for attr in ("text", "value"):
            try:
                value = (element.get_attribute(attr) or "").strip()
            except Exception:
                value = ""
            if value and value not in cls._FIELD_HINTS and value not in cls._FIELD_LABELS:
                return value
        return ""

    def _dismiss_keyboard_if_visible(self) -> None:
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            try:
                self.driver.press_keycode(4)  # BACK
            except Exception:
                pass

    def _wait_for_ip_modal_dismissed(self, timeout: float = 20) -> None:
        end = time.time() + timeout
        title_loc = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{self.IP_MODAL_TITLE}")',
        )
        while time.time() < end:
            if not self.driver.find_elements(*title_loc):
                return
            time.sleep(0.3)
        raise AppiumWaitTimeout("IP address modal did not close after tapping Continue.")
