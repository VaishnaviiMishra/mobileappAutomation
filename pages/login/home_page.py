"""Post-login home and Data Sync popup page object — xmlFiles/home.xml & dataSync.xml."""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import AppiumWait, AppiumWaitTimeout, wait_for_present, wait_until


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

    def is_data_sync_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._data_sync_title_locator()))

    def is_home_visible(self) -> bool:
        return bool(self.driver.find_elements(*self._home_modules_locator()))

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

    def wait_for_sync_downloads_complete(self) -> None:
        """Wait until both MDM and Item Locations show Downloaded."""

        def _both_downloaded() -> bool | None:
            downloaded = self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{self.DOWNLOADED_STATUS}")',
            )
            visible = [el for el in downloaded if el.is_displayed()]
            return True if len(visible) >= 2 else None

        wait_until(
            self.driver,
            _both_downloaded,
            timeout=self.DATA_SYNC_LOAD_TIMEOUT,
            poll=0.5,
            message="Data Sync did not finish — expected two 'Downloaded' statuses.",
        )

    def dismiss_data_sync_popup(self) -> None:
        self.data_sync_close_button.click()
        wait_until(
            self.driver,
            lambda: True if not self.is_data_sync_visible() else None,
            timeout=20,
            message="Data Sync popup did not close after tapping Close.",
        )

    DASHBOARD_MENU_ITEM = "Dashboard"

    def navigate_to_dashboard_via_menu(self) -> None:
        """Return to MODULES home via hamburger → Dashboard (never Android system Back)."""
        if self.is_data_sync_visible():
            self.dismiss_data_sync_popup()
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
        Case 2: Home screen directly.
        Returns which case ran: ``"data_sync"`` or ``"home"``.
        """
        screen = self.wait_for_post_login_screen()
        if screen == "data_sync":
            self.wait_for_sync_downloads_complete()
            self.dismiss_data_sync_popup()
            wait_for_present(
                self.driver,
                self._home_modules_locator(),
                timeout=self.wait.timeout,
                message="Home screen did not appear after closing Data Sync.",
            )
            return "data_sync"
        return "home"

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
