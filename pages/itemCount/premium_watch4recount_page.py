"""Item Count — Additional Premium Watch 4th Attempt (Manager Recount) Page Object."""

from __future__ import annotations

import random
import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_until
from pages.itemCount.item_count_page import ItemCountPage


class PremiumWatch4RecountPage(ItemCountPage):
    """Additional Premium Watch → 3 attempts → Approve → Recount (Attempt 4) → Unmatched."""

    MAX_RECOUNT_ATTEMPTS = 3

    # --- UPDATE THESE IDS TO MATCH YOUR ACTUAL HUB XML ---
    ADDITIONAL_PW_ID = "countRow-additional-708001" 
    ADDITIONAL_PW_COMPLETED_ID = "countRowCompleted-additional-708001"
    # -----------------------------------------------------
    
    REVIEW_COUNTS_BTN_ID = "reviewButton"
    RECOUNT_BTN_ID = "recountButton"
    
    # Attempt 4 / Unmatched screen
    SUBMIT_UNMATCHED_BTN_ID = "submitUnmatchedButton"
    GO_TO_COUNT_HOME_BTN_ID = "closeButton"
    
    SUBCATEGORY_INPUT_XPATH = "//android.widget.EditText[contains(@resource-id, 'subcategoryInput-')]"

    REVIEW_SCREEN_TITLE = "Review Premium Watch Count"
    APPROVE_SCREEN_TITLE = "Approve Premium Watch Count"
    START_PW_RECOUNT_DESC = "Start Premium Watch recount"

    def select_additional_pw(self) -> None:
        self.select_radio(self.ADDITIONAL_PW_ID)

    def is_additional_pw_completed(self) -> bool:
        elements = self.driver.find_elements(*self._resource(self.ADDITIONAL_PW_COMPLETED_ID))
        return len(elements) > 0

    def wait_for_category_screen_ready(self) -> None:
        self.wait.until_present((AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH))

    def fill_visible_subcategories(self, amount: str | None = None) -> str:
        value = amount if amount is not None else str(random.randint(1, 99))
        inputs = self.driver.find_elements(AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH)
        for input_field in inputs:
            if input_field.is_displayed():
                input_field.clear()
                input_field.send_keys(value)
        return value

    def tap_review_pw_counts(self) -> None:
        self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def verify_review_screen(self) -> None:
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
        if self.driver.find_elements(*self._accessibility(self.START_PW_RECOUNT_DESC)):
            self.wait.until_present(self._accessibility(self.START_PW_RECOUNT_DESC)).click()
        elif self.driver.find_elements(*self._resource(self.RECOUNT_BTN_ID)):
            self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()
        else:
            self.wait.until_present(self._resource(self.REVIEW_COUNTS_BTN_ID)).click()

    def tap_recount_on_approve_screen(self) -> None:
        self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()

    def tap_submit_unmatched_counts(self) -> None:
        self.wait.until_present(self._resource(self.SUBMIT_UNMATCHED_BTN_ID)).click()

    def tap_go_to_count_home(self) -> None:
        time.sleep(1) # Let the UI animation settle completely before tapping
        self.wait.until_present(self._resource(self.GO_TO_COUNT_HOME_BTN_ID)).click()
        wait_until(
            self.driver,
            lambda: self.is_on_hub_screen(),
            timeout=self.wait.timeout,
            message="Did not navigate back to the Item Count hub screen."
        )

    def complete_pw_counts_for_attempt(self, *, amount: str | None = None) -> None:
        self.wait_for_category_screen_ready()
        fill_value = amount if amount is not None else str(random.randint(1, 99))
        self.fill_visible_subcategories(amount=fill_value)
        
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass 
            
        self.tap_review_pw_counts()