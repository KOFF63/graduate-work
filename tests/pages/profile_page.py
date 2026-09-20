"""
Page Object для страницы профиля.
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage


class ProfilePage(BasePage):
    """Страница профиля пользователя"""

    # URL страницы
    URL_PATH = "/profile/"

    # Локаторы
    DISPLAY_NAME_INPUT = (By.NAME, "display_name")
    BIO_INPUT = (By.NAME, "bio")
    ROLE_SELECT = (By.NAME, "role")
    DEPARTMENT_INPUT = (By.NAME, "department")
    EMAIL_INPUT = (By.NAME, "email")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")

    def open(self):
        """Открывает страницу профиля"""
        return super().open(self.URL_PATH)

    def is_on_profile_page(self):
        """Проверяет, находимся ли мы на странице профиля"""
        return "profile" in self.get_current_url()

    def is_success_message_displayed(self):
        """Проверяет, отображается ли сообщение об успехе"""
        return self.is_element_present(*self.SUCCESS_MESSAGE)

    def get_success_message(self):
        """Получает текст сообщения об успехе"""
        return self.get_text(*self.SUCCESS_MESSAGE)