"""Item Count jewelry recount flow — xmlFiles/itemcount/14401/*.xml."""

from __future__ import annotations

import random
import time

from appium.webdriver.common.appiumby import AppiumBy

from pages.common.appium_wait import wait_until
from pages.itemCount.item_count_page import ItemCountPage


class ItemRecountPage(ItemCountPage):
    """Opening jewelry count → 3 recount attempts → approve and submit."""

    JEWELRY_CASE_COUNT = 11
    MAX_RECOUNT_ATTEMPTS = 3

    NEXT_CASE_BTN_ID = "nextCaseButton"
    REVIEW_COUNTS_BTN_ID = "reviewButton"
    RECOUNT_BTN_ID = "recountButton"
    SUBMIT_WITHOUT_RECOUNT_BTN_ID = "submitWithoutRecountButton"
    OPENING_JEWELRY_COMPLETED_ID = "countRowCompleted-opening-500002"
    SUBCATEGORY_INPUT_XPATH = "//android.widget.EditText[contains(@resource-id, 'subcategoryInput-')]"

    REVIEW_SCREEN_TITLE = "Review Jewelry Count"
    APPROVE_SCREEN_TITLE = "Approve Jewelry Count"
    START_JEWELRY_RECOUNT_DESC = "Start Jewelry recount"
    REVIEW_JEWELRY_COUNTS_DESC = "Review Jewelry counts"
    GO_TO_HOME_DESC = "Go to Home"
    GO_TO_HOME_PAGE_DESC = "Go to home page"
    REVIEW_SCROLL_PAUSE_SECONDS = 0.35

    def select_opening_jewelry(self) -> None:
        """Select Opening count → Jewelry on the hub (step1.xml)."""
        self.select_radio(self.OPENING_JEWELRY_ID)

    def wait_for_case_screen_ready(self) -> None:
        self.wait.until_present((AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH))

    def is_opening_jewelry_completed(self) -> bool:
        """Checks if the Opening Jewelry count is already marked with a green tick."""
        # Using find_elements (plural) returns an empty list instead of crashing if not found
        elements = self.driver.find_elements(*self._resource(self.OPENING_JEWELRY_COMPLETED_ID))
        return len(elements) > 0

    def fill_visible_subcategories(self, amount: str | None = None) -> str:
        """Fill every visible subcategory input; uses a random value when amount is omitted."""
        value = amount if amount is not None else str(random.randint(1, 99))
        inputs = self.driver.find_elements(AppiumBy.XPATH, self.SUBCATEGORY_INPUT_XPATH)
        for input_field in inputs:
            if input_field.is_displayed():
                input_field.clear()
                input_field.send_keys(value)
        return value

    def has_next_case_button(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.NEXT_CASE_BTN_ID)))

    def tap_next_case(self) -> None:
        self.wait.until_present(self._resource(self.NEXT_CASE_BTN_ID)).click()

    def has_review_counts_button(self) -> bool:
        return bool(self.driver.find_elements(*self._resource(self.REVIEW_COUNTS_BTN_ID)))

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
            )
            > 0,
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
            )
            > 0,
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
        if self.driver.find_elements(*self._accessibility(self.START_JEWELRY_RECOUNT_DESC)):
            self.wait.until_present(self._accessibility(self.START_JEWELRY_RECOUNT_DESC)).click()
        else:
            self.wait.until_present(self._resource(self.RECOUNT_BTN_ID)).click()

    def tap_submit_without_recount(self) -> None:
        self.wait.until_present(self._resource(self.SUBMIT_WITHOUT_RECOUNT_BTN_ID)).click()

    def _go_home_popup_locators(self) -> list[tuple[str, str]]:
        return [
            self._accessibility(self.GO_TO_HOME_DESC),
            self._accessibility(self.GO_TO_HOME_PAGE_DESC),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().textContains("Go to home")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().descriptionContains("home")',
            ),
            (
                AppiumBy.XPATH,
                "//android.widget.Button["
                "contains(@content-desc, 'home') or contains(@content-desc, 'Home') or "
                ".//android.widget.TextView[contains(translate(@text, 'HOME', 'home'), 'home')]"
                "]",
            ),
        ]

    def _find_go_home_popup_button(self):
        for locator in self._go_home_popup_locators():
            for element in self.driver.find_elements(*locator):
                try:
                    if element.is_displayed():
                        return element
                except Exception:
                    continue
        return None

    def is_submit_success_popup_visible(self) -> bool:
        return self._find_go_home_popup_button() is not None

    def wait_for_submit_success_popup(self) -> None:
        wait_until(
            self.driver,
            lambda: self._find_go_home_popup_button(),
            timeout=self.wait.timeout,
            message="Success popup with a 'Go to home' button did not appear after submit.",
        )

    def tap_go_to_home_from_success_popup(self) -> None:
        button = wait_until(
            self.driver,
            lambda: self._find_go_home_popup_button(),
            timeout=self.wait.timeout,
            message="Success popup 'Go to home' button did not appear.",
        )
        button.click()
        wait_until(
            self.driver,
            lambda: True
            if self.home.is_home_visible() or self.is_on_hub_screen()
            else None,
            timeout=self.wait.timeout,
            message="Neither MODULES home nor Item Count hub appeared after Go to home.",
        )

    def complete_jewelry_cases_for_attempt(self, *, amount: str | None = None) -> None:
        """
        Fill counts for each jewelry case until Review Jewelry counts appears.
        Cases 1–10 use Next case; case 11 uses Review Jewelry counts (step12.xml).
        """
        while True:
            self.wait_for_case_screen_ready()
            self.fill_visible_subcategories(amount=amount)

            if self.has_next_case_button():
                self.tap_next_case()
            elif self.has_review_counts_button():
                self.tap_review_jewelry_counts()
                break
            else:
                raise AssertionError(
                    "Expected 'Next case' or 'Review Jewelry counts' on the case screen."
                )

    def complete_recount_attempt(self, *, amount: str | None = None) -> None:
        """Run one full attempt: all cases → review screen → scroll → start next recount."""
        self.complete_jewelry_cases_for_attempt(amount=amount)
        self.verify_review_screen()
        self.scroll_review_screen()
        self.tap_start_jewelry_recount()

    def complete_full_jewelry_recount_flow(self, *, amount: str | None = None) -> None:
        """
        Hub → Opening Jewelry → Start count → 3 attempts → Approve → Submit without recount.
        Matches store 14401 flow (step1 through step18).
        """
        self.open_from_home()
        self.select_opening_jewelry()
        self.tap_start_count()

        for attempt in range(1, self.MAX_RECOUNT_ATTEMPTS + 1):
            self.complete_jewelry_cases_for_attempt(amount=amount)
            self.verify_review_screen()
            self.scroll_review_screen()
            self.tap_start_jewelry_recount()

        self.verify_approve_screen()
        self.tap_submit_without_recount()
        self.wait_for_submit_success_popup()