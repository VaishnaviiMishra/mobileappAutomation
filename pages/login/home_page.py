"""Post-login home and Data Sync popup page object — xmlFiles/home.xml & dataSync.xml."""

from __future__ import annotations

import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import (
    AppiumWait,
    AppiumWaitTimeout,
    is_fatal_driver_error,
    wait_for_clickable,
    wait_for_present,
    wait_until,
)


class HomePage:
    APP_PACKAGE = "com.ezpawnpal"

    # dataSync.xml
    DATA_SYNC_TITLE = "Data Sync"
    PRODUCT_MDM_LABEL = "PRODUCT MDM DATA"
    ITEM_LOCATIONS_LABEL = "ITEM LOCATIONS"
    DOWNLOADED_STATUS = "Downloaded"
    CLOSE_BUTTON_DESC = "Close"

    # home.xml
    HEADER_TITLE = "Mobile Item Manager"
    MODULES_HEADING = "MODULES"
    WELCOME_PREFIX = "Welcome,"
    STORE_PREFIX = "Store#"
    ITEM_COUNT = "Item Count"
    ITEM_LOCATOR = "Item Locator"
    RETAIL_ITEM_MANAGER = "Retail Item Manager"
    DROP_COLLECTION = "Drop Collection"
    APP_VERSION_FOOTER = "App version: 1.0.0"
    HAMBURGER_DESC = "Open navigation menu"
    PROFILE_DESC = "Open profile menu"

    DATA_SYNC_LOAD_TIMEOUT = 120.0
    POST_LOGIN_DETECT_TIMEOUT = 45.0
    LATE_DATA_SYNC_TIMEOUT = 12.0

    ANDROID_BACK_KEYCODE = 4

    def __init__(self, driver, timeout: int = 25) -> None:
        self.driver = driver
        self.wait = AppiumWait(driver, float(timeout))

    # --- State checks ---

    def _data_sync_title_locator(self) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{self.DATA_SYNC_TITLE}")',
        )

    def _home_modules_locator(self) -> tuple[str, str]:
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{self.MODULES_HEADING}")',
        )

    def _is_locator_displayed(self, locator: tuple[str, str]) -> bool:
        try:
            elements = self.driver.find_elements(*locator)
        except Exception as exc:
            if is_fatal_driver_error(exc):
                raise
            return False
        for el in elements:
            try:
                if el.is_displayed():
                    return True
            except Exception as exc:
                if is_fatal_driver_error(exc):
                    raise
                continue
        return False

    def is_data_sync_visible(self) -> bool:
        return self._is_locator_displayed(self._data_sync_title_locator())

    def is_home_visible(self) -> bool:
        """MODULES home is visible and not blocked by the Data Sync overlay."""
        if self.is_data_sync_visible():
            return False
        return self._is_locator_displayed(self._home_modules_locator())

    # --- Navigation ---

    def wait_for_post_login_screen(self) -> str:
        """
        Wait until either Data Sync popup or home screen appears.
        Returns ``"data_sync"`` or ``"home"``.
        """

        def _detect() -> str | None:
            if self.is_data_sync_visible():
                return "data_sync"
            if self.is_home_visible():
                return "home"
            return None

        return wait_until(
            self.driver,
            _detect,
            timeout=self.POST_LOGIN_DETECT_TIMEOUT,
            message="Neither Data Sync popup nor home screen appeared after login.",
        )

    def _data_sync_close_locators(self) -> tuple[tuple[str, str], ...]:
        return (
            (AppiumBy.ACCESSIBILITY_ID, self.CLOSE_BUTTON_DESC),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.CLOSE_BUTTON_DESC}")'),
            (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Close"]'),
            (
                AppiumBy.XPATH,
                '//android.widget.Button[.//android.widget.TextView[@text="Close"]]',
            ),
        )

    def _find_data_sync_close_button(self):
        for locator in self._data_sync_close_locators():
            for el in self.driver.find_elements(*locator):
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except Exception:
                    continue
        return None

    def wait_for_sync_downloads_complete(self) -> None:
        """Wait until sync finishes (two Downloaded rows or an enabled Close button)."""

        def _sync_ready() -> bool | None:
            if not self.is_data_sync_visible():
                return None

            close_btn = self._find_data_sync_close_button()
            downloaded = self.get_downloaded_elements()
            if len(downloaded) >= 2:
                return True
            if close_btn is not None:
                return True
            return None

        wait_until(
            self.driver,
            _sync_ready,
            timeout=self.DATA_SYNC_LOAD_TIMEOUT,
            poll=0.5,
            message=(
                "Data Sync did not finish — expected two 'Downloaded' statuses "
                "or an enabled Close button."
            ),
        )

    def _wait_for_late_data_sync_popup(self) -> bool:
        """Data Sync can appear shortly after MODULES renders underneath."""
        if self.is_data_sync_visible():
            return True

        end = time.time() + self.LATE_DATA_SYNC_TIMEOUT
        while time.time() < end:
            if self.is_data_sync_visible():
                return True
            time.sleep(0.3)
        return False

    def dismiss_data_sync_popup(self) -> None:
        if not self.is_data_sync_visible():
            return

        self.wait_for_sync_downloads_complete()

        last_error: Exception | None = None
        for locator in self._data_sync_close_locators():
            try:
                close_btn = wait_for_clickable(
                    self.driver,
                    locator,
                    timeout=10,
                    poll=0.25,
                    message=f"Data Sync Close button not clickable: {locator!r}",
                )
                close_btn.click()
                break
            except AppiumWaitTimeout as exc:
                last_error = exc
        else:
            raise AppiumWaitTimeout(
                "Data Sync Close button was not clickable on any known locator."
            ) from last_error

        wait_until(
            self.driver,
            lambda: True if not self.is_data_sync_visible() else None,
            timeout=20,
            message="Data Sync popup did not close after tapping Close.",
        )

    def ensure_data_sync_cleared(self) -> bool:
        """
        If the Data Sync overlay is showing, wait for downloads and tap Close.
        Returns True when a popup was dismissed, False when none was visible.
        """
        if not self.is_data_sync_visible() and not self._wait_for_late_data_sync_popup():
            return False
        self.dismiss_data_sync_popup()
        return True

    def wait_for_home_ready(self, timeout: float | None = None) -> None:
        """
        Block until MODULES home is usable.

        Data Sync can appear seconds or minutes after login while tests 01–02
        are still running — call this before each test method in a shared session.
        """
        sync_handled = False

        def _ready() -> bool | None:
            nonlocal sync_handled
            if self.is_data_sync_visible():
                self.dismiss_data_sync_popup()
                sync_handled = True
                return None
            if self.is_home_visible():
                return True
            return None

        wait_until(
            self.driver,
            _ready,
            timeout=timeout or self.DATA_SYNC_LOAD_TIMEOUT,
            poll=0.5,
            message="Home screen not ready — Data Sync overlay or MODULES dashboard missing.",
        )

    DASHBOARD_MENU_ITEM = "Dashboard"

    def navigate_to_dashboard_via_menu(self) -> None:
        """Return to MODULES home via hamburger → Dashboard (never Android system Back)."""
        self.ensure_data_sync_cleared()
        if self.is_home_visible():
            return

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                if attempt > 0:
                    try:
                        self.hamburger_button.click()
                    except Exception:
                        pass
                self.hamburger_button.click()
                wait_for_present(
                    self.driver,
                    (AppiumBy.ACCESSIBILITY_ID, self.DASHBOARD_MENU_ITEM),
                    timeout=self.wait.timeout,
                    message="Hamburger menu did not show Dashboard option.",
                )
                self.driver.find_element(
                    AppiumBy.ACCESSIBILITY_ID, self.DASHBOARD_MENU_ITEM
                ).click()
                wait_until(
                    self.driver,
                    lambda: True if self.is_home_visible() else None,
                    timeout=self.wait.timeout,
                    message="Home screen (MODULES) did not appear after tapping Dashboard.",
                )
                return
            except Exception as exc:
                last_error = exc

        raise AppiumWaitTimeout(
            "Home screen (MODULES) did not appear after navigating via Dashboard menu. "
            f"Last error: {last_error}"
        )

    def return_to_home(self) -> None:
        """Return to the home screen (MODULES) via hamburger menu → Dashboard."""
        self.navigate_to_dashboard_via_menu()

    def handle_post_login_either_path(self) -> str:
        """
        Case 1: Data Sync → wait for load → Close → home.
        Case 2: Home screen directly (Data Sync may still appear shortly after).
        Returns which case ran: ``"data_sync"`` or ``"home"``.
        """
        screen = self.wait_for_post_login_screen()
        handled_sync = screen == "data_sync"
        if not handled_sync:
            handled_sync = self._wait_for_late_data_sync_popup()
        if handled_sync or self.is_data_sync_visible():
            self.dismiss_data_sync_popup()
            handled_sync = True
        wait_until(
            self.driver,
            lambda: True if self.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="Home screen (MODULES, no Data Sync overlay) did not appear after post-login handling.",
        )
        return "data_sync" if handled_sync else "home"

    # --- Data Sync element accessors (dataSync.xml) ---

    @property
    def data_sync_title(self):
        return self.wait.until_present(self._data_sync_title_locator())

    @property
    def product_mdm_label(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.PRODUCT_MDM_LABEL}")')
        )

    @property
    def item_locations_label(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.ITEM_LOCATIONS_LABEL}")')
        )

    @property
    def data_sync_close_button(self):
        return self.wait.until_clickable((AppiumBy.ACCESSIBILITY_ID, self.CLOSE_BUTTON_DESC))

    def get_downloaded_elements(self) -> list:
        downloaded = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{self.DOWNLOADED_STATUS}")',
        )
        return [el for el in downloaded if el.is_displayed()]

    # --- Home element accessors (home.xml) ---

    @property
    def hamburger_button(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.HAMBURGER_DESC))

    @property
    def header_title(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.HEADER_TITLE}")')
        )

    @property
    def profile_button(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.PROFILE_DESC))

    @property
    def welcome_message(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{self.WELCOME_PREFIX}")')
        )

    @property
    def store_line(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{self.STORE_PREFIX}")')
        )

    @property
    def modules_heading(self):
        return self.wait.until_present(self._home_modules_locator())

    @property
    def item_count_module(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.ITEM_COUNT))

    @property
    def item_locator_module(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.ITEM_LOCATOR))

    @property
    def retail_item_manager_module(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.RETAIL_ITEM_MANAGER))

    @property
    def drop_collection_module(self):
        return self.wait.until_present((AppiumBy.ACCESSIBILITY_ID, self.DROP_COLLECTION))

    @property
    def app_version_footer(self):
        return self.wait.until_present(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.APP_VERSION_FOOTER}")')
        )
