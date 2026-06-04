"""
Profile / account menu and refresh-data flows (MDM + Item Locations).

Locators from xmlFiles/accountlogo.xml, datamdmQ.xml, datasync.xml,
refreshlocationQ.xml, and datasyncretailer.xml.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import AppiumWait, wait_for_present, wait_until
from pages.login.home_page import HomePage


@dataclass(frozen=True)
class _RefreshFlowConfig:
    button_id: str
    confirm_title: str
    confirm_body: str
    sync_section_label: str
    progress_name: str
    timeout_env: str
    default_timeout: float


class RefreshDataPage:
    # accountlogo.xml
    REFRESH_MDM_BUTTON_ID = "ddRefreshMdmButton"
    REFRESH_LOCATIONS_BUTTON_ID = "ddRefreshLocationsButton"
    LOGOUT_BUTTON_ID = "ddLogoutButton"

    REFRESH_MDM_LABEL = "Refresh Product MDM Data"
    REFRESH_LOCATIONS_LABEL = "Refresh Item Locations Data"
    DEVICE_IP_PREFIX = "Device IP:"
    APP_VERSION_LABEL = "App version: 1.0.0"
    BUILD_LABEL_PREFIX = "Build"
    LOGOUT_LABEL = "Logout"
    STORE_PREFIX = "Store#"

    # Shared confirm modal (datamdmQ.xml — same structure for both refresh types)
    CONFIRM_MODAL_ID = "refreshConfirmModal"
    CONFIRM_YES_ID = "confirmRefreshButton"
    CONFIRM_NO_ID = "cancelRefreshButton"
    CONFIRM_YES_DESC = "Yes"
    CONFIRM_NO_DESC = "No"

    MDM_CONFIRM_TITLE = "Refresh Product MDM Data?"
    MDM_CONFIRM_BODY = "Are you sure you want to refresh product MDM data?"

    # refreshlocationQ.xml
    LOCATIONS_CONFIRM_TITLE = "Refresh Item Locations?"
    LOCATIONS_CONFIRM_BODY = "Are you sure you want to refresh item location data?"

    # Data Sync popups (datasync.xml / datasyncretailer.xml)
    PRODUCT_MDM_LABEL = HomePage.PRODUCT_MDM_LABEL
    ITEM_LOCATIONS_LABEL = HomePage.ITEM_LOCATIONS_LABEL
    DOWNLOADED_STATUS = HomePage.DOWNLOADED_STATUS
    CLOSE_BUTTON_DESC = HomePage.CLOSE_BUTTON_DESC

    DEFAULT_SYNC_TIMEOUT = 900.0

    _MDM_FLOW = _RefreshFlowConfig(
        button_id=REFRESH_MDM_BUTTON_ID,
        confirm_title=MDM_CONFIRM_TITLE,
        confirm_body=MDM_CONFIRM_BODY,
        sync_section_label=PRODUCT_MDM_LABEL,
        progress_name="Product MDM",
        timeout_env="EZPAWNPAL_MDM_REFRESH_TIMEOUT",
        default_timeout=DEFAULT_SYNC_TIMEOUT,
    )

    _LOCATIONS_FLOW = _RefreshFlowConfig(
        button_id=REFRESH_LOCATIONS_BUTTON_ID,
        confirm_title=LOCATIONS_CONFIRM_TITLE,
        confirm_body=LOCATIONS_CONFIRM_BODY,
        sync_section_label=ITEM_LOCATIONS_LABEL,
        progress_name="Item Locations",
        timeout_env="EZPAWNPAL_LOCATIONS_REFRESH_TIMEOUT",
        default_timeout=DEFAULT_SYNC_TIMEOUT,
    )

    def __init__(self, driver, home: HomePage, timeout: int = 25) -> None:
        self.driver = driver
        self.home = home
        self.wait = AppiumWait(driver, float(timeout))

    @classmethod
    def _timeout_for(cls, flow: _RefreshFlowConfig) -> float:
        return float(os.environ.get(flow.timeout_env, flow.default_timeout))

    def _text(self, label: str) -> tuple[str, str]:
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{label}")')

    def _text_contains(self, fragment: str) -> tuple[str, str]:
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{fragment}")')

    def _resource(self, resource_id: str) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceId("{resource_id}")',
        )

    def _accessibility(self, desc: str) -> tuple[str, str]:
        return (AppiumBy.ACCESSIBILITY_ID, desc)

    def _section_label_locator(self, label: str) -> tuple[str, str]:
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{label}")')

    def ensure_on_home(self) -> None:
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.wait_for_post_login_screen()
            if self.home.is_data_sync_visible():
                self.home.handle_post_login_either_path()
            elif not self.home.is_home_visible():
                wait_for_present(
                    self.driver,
                    self.home._home_modules_locator(),
                    timeout=self.wait.timeout,
                    message="Home screen (MODULES) did not appear.",
                )

    def open_profile_menu_from_home(self) -> None:
        self.ensure_on_home()
        self.home.profile_button.click()
        wait_for_present(
            self.driver,
            self._resource(self.REFRESH_MDM_BUTTON_ID),
            timeout=self.wait.timeout,
            message="Profile menu did not open (refresh actions missing).",
        )

    def is_profile_menu_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.REFRESH_MDM_BUTTON_ID)))

    def close_profile_menu(self) -> None:
        if self.is_profile_menu_visible():
            self.driver.press_keycode(self.home.ANDROID_BACK_KEYCODE)
            wait_until(
                self.driver,
                lambda: True if not self.is_profile_menu_visible() else None,
                timeout=self.wait.timeout,
                message="Profile menu did not close after Back.",
            )

    def verify_account_menu_layout(self) -> None:
        """Static UI from accountlogo.xml / accountlogo.png."""
        store_lines = self.driver.find_elements(*self._text_contains(self.STORE_PREFIX))
        assert any(el.is_displayed() for el in store_lines), (
            f'Expected store line containing "{self.STORE_PREFIX}".'
        )

        mdm_btn = self.wait.until_present(self._resource(self.REFRESH_MDM_BUTTON_ID))
        loc_btn = self.wait.until_present(self._resource(self.REFRESH_LOCATIONS_BUTTON_ID))
        logout_btn = self.wait.until_present(self._resource(self.LOGOUT_BUTTON_ID))

        assert mdm_btn.is_displayed() and mdm_btn.is_enabled()
        assert loc_btn.is_displayed() and loc_btn.is_enabled()
        assert logout_btn.is_displayed() and logout_btn.is_enabled()

        assert self.wait.until_present(self._text(self.REFRESH_MDM_LABEL)).is_displayed()
        assert self.wait.until_present(self._text(self.REFRESH_LOCATIONS_LABEL)).is_displayed()

        device_ip = self.wait.until_present(self._text_contains(self.DEVICE_IP_PREFIX))
        assert device_ip.is_displayed(), f'"{self.DEVICE_IP_PREFIX}" row not visible.'
        ip_text = (device_ip.text or "").strip()
        assert self.DEVICE_IP_PREFIX in ip_text, f"Device IP row text unexpected: {ip_text!r}."

        assert self.wait.until_present(self._text(self.APP_VERSION_LABEL)).is_displayed()
        assert self.wait.until_present(self._text_contains(self.BUILD_LABEL_PREFIX)).is_displayed()
        assert self.wait.until_present(self._text(self.LOGOUT_LABEL)).is_displayed()

    def _tap_refresh_button(self, button_id: str) -> None:
        self.wait.until_present(self._resource(button_id)).click()

    def verify_confirm_dialog(self, title: str, body: str) -> None:
        """Confirmation popup (datamdmQ.xml structure; title/body vary by refresh type)."""
        wait_for_present(
            self.driver,
            self._resource(self.CONFIRM_MODAL_ID),
            timeout=self.wait.timeout,
            message="Refresh confirmation modal did not appear.",
        )
        assert self.wait.until_present(self._text(title)).is_displayed()
        assert self.wait.until_present(self._text(body)).is_displayed()

        yes_btn = self.wait.until_present(self._resource(self.CONFIRM_YES_ID))
        no_btn = self.wait.until_present(self._resource(self.CONFIRM_NO_ID))
        assert yes_btn.is_displayed() and yes_btn.is_enabled()
        assert no_btn.is_displayed() and no_btn.is_enabled()
        assert self.wait.until_present(self._text("Yes")).is_displayed()
        assert self.wait.until_present(self._text("No")).is_displayed()

    def tap_confirm_yes(self) -> None:
        """Tap Yes (confirmRefreshButton in datamdmQ.xml / refreshlocationQ.xml)."""
        self.wait.until_present(self._resource(self.CONFIRM_YES_ID)).click()

    def is_data_sync_visible(self) -> bool:
        return self.home.is_data_sync_visible()

    def wait_for_sync_section_complete(
        self,
        section_label: str,
        *,
        timeout: float,
        progress_name: str,
        timeout_env: str,
    ) -> None:
        """Wait until the given Data Sync section shows Downloaded (5–15+ minutes)."""
        wait_for_present(
            self.driver,
            self.home._data_sync_title_locator(),
            timeout=self.wait.timeout,
            message="Data Sync popup did not appear after confirming refresh.",
        )

        print(
            f"Waiting up to {timeout / 60:.0f} min for {progress_name} download "
            f"(set {timeout_env} to override)…"
        )
        started = time.monotonic()
        last_log = started

        def _section_downloaded() -> bool | None:
            nonlocal last_log
            now = time.monotonic()
            if now - last_log >= 60.0:
                elapsed_min = (now - started) / 60.0
                print(f"  … {progress_name} still syncing ({elapsed_min:.1f} min elapsed)")
                last_log = now

            if not self.is_data_sync_visible():
                return None

            section_els = self.driver.find_elements(*self._section_label_locator(section_label))
            if not any(el.is_displayed() for el in section_els):
                return None

            downloaded = self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{self.DOWNLOADED_STATUS}")',
            )
            visible = [el for el in downloaded if el.is_displayed()]
            return True if visible else None

        wait_until(
            self.driver,
            _section_downloaded,
            timeout=timeout,
            poll=2.0,
            message=(
                f"{progress_name} did not reach Downloaded within {timeout:.0f}s "
                f"({section_label!r})."
            ),
        )
        elapsed_min = (time.monotonic() - started) / 60.0
        print(f"{progress_name} sync finished in {elapsed_min:.1f} min.")

    def verify_sync_result_layout(self, section_label: str) -> None:
        """Completed single-section Data Sync (datasync.xml style)."""
        assert self.wait.until_present(self.home._data_sync_title_locator()).is_displayed()
        assert self.wait.until_present(self._section_label_locator(section_label)).is_displayed()

        downloaded = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{self.DOWNLOADED_STATUS}")',
        )
        visible = [el for el in downloaded if el.is_displayed()]
        assert visible, (
            f'Expected "{self.DOWNLOADED_STATUS}" on Data Sync after refreshing {section_label!r}.'
        )

        close_btn = self.wait.until_present(self._accessibility(self.CLOSE_BUTTON_DESC))
        assert close_btn.is_displayed() and close_btn.is_enabled()

    def close_data_sync_and_return_home(self) -> None:
        self.home.data_sync_close_button.click()
        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="Home screen did not appear after closing Data Sync.",
        )

    def _run_refresh_flow(self, flow: _RefreshFlowConfig) -> None:
        timeout = self._timeout_for(flow)
        self.open_profile_menu_from_home()
        self._tap_refresh_button(flow.button_id)
        self.verify_confirm_dialog(flow.confirm_title, flow.confirm_body)
        self.tap_confirm_yes()
        self.wait_for_sync_section_complete(
            flow.sync_section_label,
            timeout=timeout,
            progress_name=flow.progress_name,
            timeout_env=flow.timeout_env,
        )
        self.verify_sync_result_layout(flow.sync_section_label)
        self.close_data_sync_and_return_home()

    def run_refresh_product_mdm_flow(self) -> None:
        """Profile menu → Refresh Product MDM Data → Yes → Data Sync → Close → home."""
        self._run_refresh_flow(self._MDM_FLOW)

    def run_refresh_item_locations_flow(self) -> None:
        """Profile menu → Refresh Item Locations Data → Yes → Data Sync → Close → home."""
        self._run_refresh_flow(self._LOCATIONS_FLOW)
