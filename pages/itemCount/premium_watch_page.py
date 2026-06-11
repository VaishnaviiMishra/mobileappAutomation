"""Item Count — Additional Premium Watch Recount Flow Page Object."""

from __future__ import annotations

import random
import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_until
from pages.itemCount.item_count_page import ItemCountPage


class PremiumWatchRecountPage(ItemCountPage):
    """Additional counts → Premium Watch → 3 recount attempts → approve and submit."""

    MAX_RECOUNT_ATTEMPTS = 3

    # --- UPDATE THESE IDS TO MATCH YOUR ACTUAL HUB XML ---
    ADDITIONAL_PW_ID = "countRow-additional-708001" 
    ADDITIONAL_PW_COMPLETED_ID = "countRowCompleted-additional-708001"
    # -----------------------------------------------------

    REVIEW_COUNTS_BTN_ID = "reviewButton"
    RECOUNT_BTN_ID = "recountButton"
    SUBMIT_WITHOUT_RECOUNT_BTN_ID = "submitWithoutRecountButton"
    
    SUBCATEGORY_INPUT_XPATH = "//android.widget.EditText[contains(@resource-id, 'subcategoryInput-')]"

    REVIEW_SCREEN_TITLE = "Review Premium Watch Count"
    APPROVE_SCREEN_TITLE = "Approve Premium Watch Count"
    START_PW_RECOUNT_DESC = "Start Premium Watch recount"

    def select_additional_pw(self) -> None:
        """Select Additional counts → Premium Watch on the hub."""
        self.select_radio(self.ADDITIONAL_PW_ID)

    def is_additional_pw_completed(self) -> bool:
        """Checks if the Premium Watch count is already marked with a green tick."""
        elements = self.driver.find_elements(*self._resource(self.ADDITIONAL_PW_COMPLETED_ID))
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

    def tap_review_pw_counts(self) -> None:
        """Taps the 'Review Premium Watch counts' button."""
        self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def verify_review_screen(self) -> None:
        """Verifies we reached the review screen by looking for its title."""
        wait_until(
            self.driver,
            lambda: len(
                self.driver.find_elements(
                    AppiumBy.XPATH,
                    f"//android.widget.TextView[@text='{self.REVIEW_SCREEN_TITLE}']",
                )
            ) > 0,
            timeout=self.wait.timeout,
            message="Did not reach the Review Premium Watch Count screen.",
        )

    def verify_approve_screen(self) -> None:
        """Verifies we successfully reached the final 'Approve Premium Watch Count' screen."""
        wait_until(
            self.driver,
            lambda: len(
                self.driver.find_elements(
                    AppiumBy.XPATH,
                    f"//android.widget.TextView[@text='{self.APPROVE_SCREEN_TITLE}']",
                )
            ) > 0,
            timeout=self.wait.timeout,
            message="Did not reach the Approve Premium Watch Count screen.",
        )

    def scroll_review_screen(self) -> None:
        """No scrolling needed for Premium Watch. Just a brief pause to let UI settle."""
        time.sleep(1)

    def tap_start_pw_recount(self) -> None:
        """Taps the button to progress from Review to the next step (or Approve screen)."""
        # Attempts 1 & 2: Try finding 'Start Premium Watch recount' via accessibility ID
        if self.driver.find_elements(*self._accessibility(self.START_PW_RECOUNT_DESC)):
            self.wait.until_present(self._accessibility(self.START_PW_RECOUNT_DESC)).click()
            
        # Attempts 1 & 2 fallback: Try finding the 'recountButton' resource ID
        elif self.driver.find_elements(*self._resource(self.RECOUNT_BTN_ID)):
            self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()
            
        # Attempt 3 fallback: The button to proceed to Approve is 'Review Premium Watch counts'
        else:
            self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def tap_submit_without_recount(self) -> None:
        """Taps the final 'Submit without recount' button on the Approve screen."""
        self.wait.until_present(self._resource(self.SUBMIT_WITHOUT_RECOUNT_BTN_ID)).click()

    def complete_pw_counts_for_attempt(self, *, amount: str | None = None) -> None:
        """
        Fills all Premium Watch subcategories on the single page, hides the keyboard,
        and then proceeds to Review. No scrolling required.
        """
        self.wait_for_category_screen_ready()
        
        # Generate the value and fill the inputs
        fill_value = amount if amount is not None else str(random.randint(1, 99))
        self.fill_visible_subcategories(amount=fill_value)
            
        # Forcefully hide the keyboard so it doesn't swallow the 'Review' button click
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass 
            
        self.tap_review_pw_counts()