"""Login error scenarios — invalid employee ID, password, and IP address."""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_for_present
from pages.login.login_page import LoginPage


class LoginErrorsPage(LoginPage):
    """Locators from xmlFiles/login/login.xml, ipaddress.xml, and ipError.xml."""

    EMPLOYEE_NOT_FOUND_ERROR = "Employee not found."
    PASSWORD_INCORRECT_ERROR = "Password is incorrect."
    IP_LOCATION_NOT_FOUND_ERROR = (
        "Location not found. Call the Service Desk at 1-866-963-1230 for assistance."
    )

    INVALID_EMPLOYEE_ID = "500000054"
    INVALID_PASSWORD = "000000"
    INVALID_IP_ADDRESS = "10.10.10.235"

    def _text_locator(self, text: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{text}")',
        )

    def _text_contains_locator(self, substring: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{substring}")',
        )

    def wait_for_employee_not_found_error(self):
        return wait_for_present(
            self.driver,
            self._text_locator(self.EMPLOYEE_NOT_FOUND_ERROR),
            timeout=self.wait.timeout,
            message=f'"{self.EMPLOYEE_NOT_FOUND_ERROR}" did not appear on login screen.',
        )

    def wait_for_password_incorrect_error(self):
        return wait_for_present(
            self.driver,
            self._text_locator(self.PASSWORD_INCORRECT_ERROR),
            timeout=self.wait.timeout,
            message=f'"{self.PASSWORD_INCORRECT_ERROR}" did not appear on login screen.',
        )

    def wait_for_ip_location_error(self):
        """Location error on login screen or IP modal after Continue."""
        return wait_for_present(
            self.driver,
            self._text_contains_locator("Location not found"),
            timeout=self.wait.timeout,
            message=f'"{self.IP_LOCATION_NOT_FOUND_ERROR}" did not appear after IP Continue.',
        )

    def submit_login_attempt(self, employee_id: str, password: str) -> None:
        """Enter credentials and tap Log in (same as login_test.py)."""
        self.enter_credentials(employee_id, password)
        self.click_log_in()

    def submit_login_and_wait_for_ip_modal(self, employee_id: str, password: str) -> None:
        """Valid credentials → Log in → Store Location Setup popup."""
        self.submit_login_attempt(employee_id, password)
        self.wait_for_ip_address_modal()

    def wait_for_ip_address_modal(self) -> None:
        """Store Location Setup popup (ipaddress.xml)."""
        self.wait_for_ip_modal()
        wait_for_present(
            self.driver,
            self._text_locator(self.IP_MODAL_TITLE),
            timeout=self.wait.timeout,
            message=f'"{self.IP_MODAL_TITLE}" did not appear on IP popup.',
        )
        wait_for_present(
            self.driver,
            self._text_locator(self.IP_ADDRESS_LABEL),
            timeout=self.wait.timeout,
            message=f'"{self.IP_ADDRESS_LABEL}" label did not appear on IP popup.',
        )
        wait_for_present(
            self.driver,
            (AppiumBy.ACCESSIBILITY_ID, "IP Address"),
            timeout=self.wait.timeout,
            message="IP Address input did not appear on popup.",
        )

    def enter_ip_on_modal_and_continue(self, ip_address: str) -> None:
        """Enter IP on popup, dismiss keyboard, tap Continue (ipaddress.xml)."""
        field = self.ip_address_input
        field.click()
        field.clear()
        field.send_keys(ip_address)
        self._dismiss_keyboard_if_visible()
        self.ip_continue_button.click()
