"""Item Count — Additional Electronics Recount Flow Page Object."""

from __future__ import annotations

import random
import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_until
from pages.itemCount.item_count_page import ItemCountPage


class ElectronicsRecountPage(ItemCountPage):
    """Additional counts → Electronics → 3 recount attempts → approve and submit."""

    MAX_RECOUNT_ATTEMPTS = 3
    REVIEW_SCREEN_TITLE = "Review Electronics Count"
    # Locators specific to Electronics
    ADDITIONAL_ELECTRONICS_ID = "countRow-additional-502002"
    ADDITIONAL_ELECTRONICS_COMPLETED_ID = "countRowCompleted-additional-502002"
    
    REVIEW_COUNTS_BTN_ID = "reviewButton"
    RECOUNT_BTN_ID = "recountButton"
    SUBMIT_WITHOUT_RECOUNT_BTN_ID = "submitWithoutRecountButton"
    
    SUBCATEGORY_INPUT_XPATH = "//android.widget.EditText[contains(@resource-id, 'subcategoryInput-')]"

    APPROVE_SCREEN_TITLE = "Approve Electronics Count"
    START_ELECTRONICS_RECOUNT_DESC = "Start Electronics recount"
    REVIEW_SCROLL_PAUSE_SECONDS = 0.35

    def select_additional_electronics(self) -> None:
        """Select Additional counts → Electronics on the hub."""
        self.select_radio(self.ADDITIONAL_ELECTRONICS_ID)

    def is_additional_electronics_completed(self) -> bool:
        """Checks if the Electronics count is already marked with a green tick."""
        elements = self.driver.find_elements(*self._resource(self.ADDITIONAL_ELECTRONICS_COMPLETED_ID))
        return len(elements) > 0

    def wait_for_category_screen_ready(self) -> None:
        """Wait until the input fields are present."""
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

    def tap_review_electronics_counts(self) -> None:
        """Taps the 'Review Electronics counts' button."""
        self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def verify_review_screen(self) -> None:
        """Verifies we reached the review screen by looking for its title instead of a specific button."""
        wait_until(
            self.driver,
            lambda: len(
                self.driver.find_elements(
                    AppiumBy.XPATH,
                    f"//android.widget.TextView[@text='{self.REVIEW_SCREEN_TITLE}']",
                )
            ) > 0,
            timeout=self.wait.timeout,
            message="Did not reach the Review Electronics Count screen.",
        )

    def verify_approve_screen(self) -> None:
        """Verifies we successfully reached the final 'Approve Electronics Count' screen."""
        wait_until(
            self.driver,
            lambda: len(
                self.driver.find_elements(
                    AppiumBy.XPATH,
                    f"//android.widget.TextView[@text='{self.APPROVE_SCREEN_TITLE}']",
                )
            ) > 0,
            timeout=self.wait.timeout,
            message="Did not reach the Approve Electronics Count screen.",
        )

    def scroll_review_screen(self) -> None:
        """Scrolls the long review list before tapping recount to ensure buttons are visible."""
        # 1. Wait for the screen transition and keyboard animations to completely finish
        time.sleep(1)
        
        window = self.driver.get_window_size()
        center_x = int(window["width"] * 0.5)
        
        # 2. Tighten the swipe area to the safe middle of the screen 
        # (Swiping from 60% down to 40% up) to avoid system bars throwing W3C errors
        top_y = int(window["height"] * 0.40)
        bottom_y = int(window["height"] * 0.60)
        
        for _ in range(5):
            try:
                self.driver.swipe(center_x, bottom_y, center_x, top_y, 400)
                time.sleep(self.REVIEW_SCROLL_PAUSE_SECONDS)
            except Exception as e:
                # Failsafe: If a swipe fails due to screen size limits, catch it and move on
                print(f"\nWarning during swipe: {e}")
                break

    def tap_start_electronics_recount(self) -> None:
        """Taps the button to progress from Review to the next step (or Approve screen)."""
        
        # Attempts 1 & 2: Try finding 'Start Electronics recount' via accessibility ID
        if self.driver.find_elements(*self._accessibility(self.START_ELECTRONICS_RECOUNT_DESC)):
            self.wait.until_present(self._accessibility(self.START_ELECTRONICS_RECOUNT_DESC)).click()
            
        # Attempts 1 & 2 fallback: Try finding the 'recountButton' resource ID
        elif self.driver.find_elements(*self._resource(self.RECOUNT_BTN_ID)):
            self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()
            
        # Attempt 3 fallback: The button to proceed to Approve is 'Review Electronics counts'
        else:
            self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def tap_submit_without_recount(self) -> None:
        """Taps the final 'Submit without recount' button on the Approve screen."""
        self.wait.until_present(self._resource(self.SUBMIT_WITHOUT_RECOUNT_BTN_ID)).click()

    def complete_electronics_counts_for_attempt(self, *, amount: str | None = None) -> None:
        """
        Fills all electronics subcategories on the single page, hides the keyboard,
        and then proceeds to Review.
        """
        self.wait_for_category_screen_ready()
        
        # Generate the value and fill the inputs (no scrolling needed on this screen)
        fill_value = amount if amount is not None else str(random.randint(1, 99))
        self.fill_visible_subcategories(amount=fill_value)
            
        # Forcefully hide the keyboard so it doesn't swallow the 'Review' button click
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass # Failsafe if the keyboard is already hidden
            
        self.tap_review_electronics_counts()