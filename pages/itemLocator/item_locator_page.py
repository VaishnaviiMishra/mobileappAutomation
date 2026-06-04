"""Item Locator hub page object — xmlFiles/itemlocator.xml."""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import AppiumWait, wait_for_present, wait_until
from pages.login.home_page import HomePage


class ItemLocatorPage:
    MODULE_TITLE = "Item Locator"
    SUBTITLE = "What would you like to do?"
    ASSIGN_TITLE = "Assign Item Location"
    ASSIGN_BLURB = "Scan an item and assign it to a shelf location"
    SETUP_TITLE = "Setup Location"
    SETUP_BLURB = "Configure shelf labels in the back room"

    ASSIGN_BUTTON_ID = "assignItemLocationButton"
    SETUP_BUTTON_ID = "setupLocationButton"

    def __init__(self, driver, home: HomePage, timeout: int = 25) -> None:
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

    # --- Navigation ---

    def ensure_on_home(self) -> None:
        if self.home.is_data_sync_visible():
            self.home.dismiss_data_sync_popup()
        if not self.home.is_home_visible():
            self.home.wait_for_post_login_screen()

    def open_from_home(self) -> None:
        self.ensure_on_home()
        self.home.item_locator_module.click()
        self.wait_for_hub()

    def wait_for_hub(self) -> None:
        wait_for_present(
            self.driver,
            self._text(self.SUBTITLE),
            timeout=self.wait.timeout,
            message="Item Locator hub did not load.",
        )

    def is_on_hub(self) -> bool:
        try:
            for el in self.driver.find_elements(*self._text(self.SUBTITLE)):
                try:
                    if el.is_displayed():
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def return_to_hub(self) -> None:
        if self.is_on_hub():
            return
        if self.home.is_home_visible():
            self.open_from_home()
            return
        for _ in range(8):
            self.driver.press_keycode(4)
            if self.is_on_hub():
                return
            if self.home.is_home_visible():
                self.open_from_home()
                return
        wait_until(
            self.driver,
            lambda: True if self.is_on_hub() else None,
            timeout=self.wait.timeout,
            message="Could not return to Item Locator hub.",
        )

    def back_to_home(self) -> None:
        while not self.home.is_home_visible():
            self.driver.press_keycode(4)
        wait_until(
            self.driver,
            lambda: True if self.home.is_home_visible() else None,
            timeout=self.wait.timeout,
            message="Back did not return to home from Item Locator.",
        )

    # --- Element accessors ---

    def get_hamburger_button(self):
        return self.home.hamburger_button

    def get_module_title(self):
        return self.wait.until_present(self._text(self.MODULE_TITLE))

    def get_subtitle(self):
        return self.wait.until_present(self._text(self.SUBTITLE))

    def get_assign_button(self):
        return self.wait.until_present(self._resource(self.ASSIGN_BUTTON_ID))

    def get_setup_button(self):
        return self.wait.until_present(self._resource(self.SETUP_BUTTON_ID))

    def get_assign_title(self):
        return self.wait.until_present(self._text(self.ASSIGN_TITLE))

    def get_assign_blurb(self):
        return self.wait.until_present(self._text(self.ASSIGN_BLURB))

    def get_setup_title(self):
        return self.wait.until_present(self._text(self.SETUP_TITLE))

    def get_setup_blurb(self):
        return self.wait.until_present(self._text(self.SETUP_BLURB))

    # --- Actions ---

    def tap_setup_location(self) -> None:
        self.get_setup_button().click()
        wait_until(
            self.driver,
            lambda: True if not self.is_on_hub() else None,
            timeout=self.wait.timeout,
            message='"Setup Location" card did not navigate away from the Item Locator hub.',
        )
