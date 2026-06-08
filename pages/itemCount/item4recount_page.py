"""Item Count — Closing Jewelry 4th Attempt (Manager Recount) Page Object."""

from __future__ import annotations

import random
import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_until
from pages.itemCount.item_count_page import ItemCountPage


class Item4RecountPage(ItemCountPage):
    """Closing jewelry count → 3 attempts → Approve → Recount (Attempt 4) → Unmatched."""

    JEWELRY_CASE_COUNT = 11
    MAX_RECOUNT_ATTEMPTS = 3

    CLOSING_JEWELRY_ID = "countRow-closing-500002"
    CLOSING_JEWELRY_COMPLETED_ID = "countRowCompleted-closing-500002"
    
    NEXT_CASE_BTN_ID = "nextCaseButton"
    REVIEW_COUNTS_BTN_ID = "reviewButton"
    RECOUNT_BTN_ID = "recountButton"
    
    # New locators for the Attempt 4 / Unmatched screen
    SUBMIT_UNMATCHED_BTN_ID = "submitUnmatchedButton"
    GO_TO_COUNT_HOME_BTN_ID = "closeButton"
    
    SUBCATEGORY_INPUT_XPATH = "//android.widget.EditText[contains(@resource-id, 'subcategoryInput-')]"

    REVIEW_SCREEN_TITLE = "Review Jewelry Count"
    APPROVE_SCREEN_TITLE = "Approve Jewelry Count"
    START_JEWELRY_RECOUNT_DESC = "Start Jewelry recount"
    REVIEW_SCROLL_PAUSE_SECONDS = 0.35

    def select_closing_jewelry(self) -> None:
        """Select Closing count → Jewelry on the hub."""
        self.select_radio(self.CLOSING_JEWELRY_ID)

    def is_closing_jewelry_completed(self) -> bool:
        """Checks if the Closing Jewelry count is already marked with a green tick."""
        elements = self.driver.find_elements(*self._resource(self.CLOSING_JEWELRY_COMPLETED_ID))
        return len(elements) > 0

    def wait_for_case_screen_ready(self) -> None:
        self.wait.until_present((AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH))

    def fill_visible_subcategories(self, amount: str | None = None) -> str:
        """Fill every visible subcategory input with a random or specified value."""
        value = amount if amount is not None else str(random.randint(1, 99))
        inputs = self.driver.find_elements(AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH)
        for input_field in inputs:
            if input_field.is_displayed():
                input_field.clear()
                input_field.send_keys(value)
        return value

    def has_next_case_button(self) -> bool:
        elements = self.driver.find_elements(*self._resource(self.NEXT_CASE_BTN_ID))
        return any(el.is_displayed() for el in elements)

    def tap_next_case(self) -> None:
        self.wait.until_present(self._resource(self.NEXT_CASE_BTN_ID)).click()

    def has_review_counts_button(self) -> bool:
        elements = self.driver.find_elements(*self._resource(self.REVIEW_COUNTS_BTN_ID))
        return any(el.is_displayed() for el in elements)

    def tap_review_jewelry_counts(self) -> None:
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
            message="Did not reach the Review Jewelry Count screen.",
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
            message="Did not reach the Approve Jewelry Count screen.",
        )

    def scroll_review_screen(self) -> None:
        """Scroll the review list from top to bottom before tapping recount."""
        window = self.driver.get_window_size()
        center_x = int(window["width"] * 0.5)
        top_y = int(window["height"] * 0.35)
        bottom_y = int(window["height"] * 0.65)
        for _ in range(6):
            self.driver.swipe(center_x, bottom_y, center_x, top_y, 400)
            time.sleep(self.REVIEW_SCROLL_PAUSE_SECONDS)

    def tap_start_jewelry_recount(self) -> None:
        """Taps the button to progress from Review to the next step (or Approve screen)."""
        if self.driver.find_elements(*self._accessibility(self.START_JEWELRY_RECOUNT_DESC)):
            self.wait.until_present(self._accessibility(self.START_JEWELRY_RECOUNT_DESC)).click()
        else:
            self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()

    def tap_recount_on_approve_screen(self) -> None:
        """Taps Recount from the Approve screen to trigger Attempt 4."""
        self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()

    def tap_submit_unmatched_counts(self) -> None:
        """Taps the final Submit unmatched counts button on Attempt 4."""
        self.wait.until_present(self._resource(self.SUBMIT_UNMATCHED_BTN_ID)).click()

    def tap_go_to_count_home(self) -> None:
        """Taps the 'Go to count home' button to abort submission on Attempt 4."""
        self.wait.until_present(self._resource(self.GO_TO_COUNT_HOME_BTN_ID)).click()
        
        # Tell Appium to wait for the transition back to step1.xml to finish!
        wait_until(
            self.driver,
            lambda: self.is_on_hub_screen(),
            timeout=self.wait.timeout,
            message="Did not navigate back to the Item Count hub screen after clicking 'Go to count home'."
        )

    def complete_jewelry_cases_for_attempt(self, *, amount: str | None = None) -> None:
        """Dynamically iterates through all cases until the Review button is found."""
        while True:
            self.wait_for_case_screen_ready()
            self.fill_visible_subcategories(amount=amount)

            if self.has_next_case_button():
                self.tap_next_case()
            elif self.has_review_counts_button():
                self.tap_review_jewelry_counts()
                break
            else:
                raise AssertionError("Expected 'Next case' or 'Review Jewelry counts' button.")