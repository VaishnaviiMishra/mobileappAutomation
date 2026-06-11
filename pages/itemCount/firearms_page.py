"""Item Count — Firearms Recount Flow Page Object."""

from __future__ import annotations

import random
import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_until
from pages.itemCount.item_count_page import ItemCountPage


class FirearmsRecountPage(ItemCountPage):
    """Opening firearms count → 3 recount attempts → approve and submit."""

    MAX_RECOUNT_ATTEMPTS = 3

    # Locators specific to Firearms
    OPENING_FIREARMS_ID = "countRow-opening-500003"
    REVIEW_COUNTS_BTN_ID = "reviewButton"
    RECOUNT_BTN_ID = "recountButton"
    SUBMIT_WITHOUT_RECOUNT_BTN_ID = "submitWithoutRecountButton"
    
    SUBCATEGORY_INPUT_XPATH = "//android.widget.EditText[contains(@resource-id, 'subcategoryInput-')]"

    REVIEW_SCREEN_TITLE = "Review Firearms Count"
    APPROVE_SCREEN_TITLE = "Approve Firearms Count"
    START_FIREARMS_RECOUNT_DESC = "Start Firearms recount"
    REVIEW_SCROLL_PAUSE_SECONDS = 0.35

    def select_opening_firearms(self) -> None:
        """Select Opening count → Firearms on the hub."""
        self.select_radio(self.OPENING_FIREARMS_ID)

    def wait_for_category_screen_ready(self) -> None:
        """Wait until the input fields for Handguns, Long Guns, etc., are present."""
        self.wait.until_present((AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH))

    def fill_visible_subcategories(self, amount: str | None = None) -> str:
        """Fill every visible subcategory input; uses a random value when amount is omitted."""
        value = amount if amount is not None else str(random.randint(1, 99))
        inputs = self.driver.find_elements(AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH)
        for input_field in inputs:
            if input_field.is_displayed():
                input_field.clear()
                input_field.send_keys(value)
        return value

    def tap_review_firearms_counts(self) -> None:
        """Taps the 'Review Firearms counts' button at the bottom of the screen."""
        self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def verify_review_screen(self) -> None:
        """Verifies we successfully reached the 'Review Firearms Count' screen."""
        wait_until(
            self.driver,
            lambda: len(
                self.driver.find_elements(
                    AppiumBy.XPATH,
                    f"//android.widget.TextView[@text='{self.REVIEW_SCREEN_TITLE}']",
                )
            )
            > 0,
            timeout=self.wait.timeout,
            message="Did not reach the Review Firearms Count screen.",
        )

    def verify_approve_screen(self) -> None:
        """Verifies we successfully reached the final 'Approve Firearms Count' screen."""
        wait_until(
            self.driver,
            lambda: len(
                self.driver.find_elements(
                    AppiumBy.XPATH,
                    f"//android.widget.TextView[@text='{self.APPROVE_SCREEN_TITLE}']",
                )
            )
            > 0,
            timeout=self.wait.timeout,
            message="Did not reach the Approve Firearms Count screen.",
        )

    def scroll_review_screen(self) -> None:
        """Scroll the review list slightly before tapping recount to ensure buttons are visible."""
        window = self.driver.get_window_size()
        center_x = int(window["width"] * 0.5)
        top_y = int(window["height"] * 0.35)
        bottom_y = int(window["height"] * 0.65)
        for _ in range(2): # Firearms has fewer categories, less scrolling needed than jewelry
            self.driver.swipe(center_x, bottom_y, center_x, top_y, 400)
            time.sleep(self.REVIEW_SCROLL_PAUSE_SECONDS)

    def tap_start_firearms_recount(self) -> None:
        """Taps 'Start Firearms recount' to trigger the next attempt."""
        if self.driver.find_elements(*self._accessibility(self.START_FIREARMS_RECOUNT_DESC)):
            self.wait.until_present(self._accessibility(self.START_FIREARMS_RECOUNT_DESC)).click()
        else:
            self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()

    def tap_submit_without_recount(self) -> None:
        """Taps the final 'Submit without recount' button on the Approve screen."""
        self.wait.until_present(self._resource(self.SUBMIT_WITHOUT_RECOUNT_BTN_ID)).click()

    def complete_firearms_counts_for_attempt(self, *, amount: str | None = None) -> None:
        """
        Unlike Jewelry, Firearms lists all inputs on a single page.
        This fills the counts and immediately proceeds to Review.
        """
        self.wait_for_category_screen_ready()
        self.fill_visible_subcategories(amount=amount)
        self.tap_review_firearms_counts()