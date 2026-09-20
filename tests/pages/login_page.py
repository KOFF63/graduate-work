"""
Page Object для страницы входа.
"""

import time
from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    """Страница входа в систему"""

    # URL страницы
    URL_PATH = "/login/"

    # Локаторы
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-error")

    def open(self):
        """Открывает страницу входа"""
        return super().open(self.URL_PATH)

    def fill_username(self, username):
        """Заполняет имя пользователя"""
        self.fill(*self.USERNAME_INPUT, username)
        return self

    def fill_password(self, password):
        """Заполняет пароль"""
        self.fill(*self.PASSWORD_INPUT, password)
        return self

    def submit(self):
        """Нажимает кнопку входа"""
        self.click(*self.SUBMIT_BUTTON)
        time.sleep(0.5)  # Ждем ответа сервера
        return self

    def login(self, username, password):
        """
        Полный цикл входа.

        Args:
            username: Имя пользователя
            password: Пароль
        """
        self.fill_username(username)
        self.fill_password(password)
        self.submit()
        return self

    def is_success_message_displayed(self):
        """Проверяет, отображается ли сообщение об успехе"""
        return self.is_element_present(*self.SUCCESS_MESSAGE)

    def get_success_message(self):
        """Получает текст сообщения об успехе"""
        return self.get_text(*self.SUCCESS_MESSAGE)

    def is_error_message_displayed(self):
        """Проверяет, отображается ли сообщение об ошибке"""
        return self.is_element_present(*self.ERROR_MESSAGE)

    def get_error_message(self):
        """Получает текст сообщения об ошибке"""
        return self.get_text(*self.ERROR_MESSAGE)

    def is_on_login_page(self):
        """Проверяет, находимся ли мы на странице входа"""
        return "login" in self.get_current_url()