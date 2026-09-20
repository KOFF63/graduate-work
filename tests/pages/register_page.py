"""
Page Object для страницы регистрации.
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage


class RegisterPage(BasePage):
    """Страница регистрации пользователя"""

    # URL страницы
    URL_PATH = "/register/"

    # Локаторы
    USERNAME_INPUT = (By.ID, "id_username")
    DISPLAY_NAME_INPUT = (By.ID, "id_display_name")
    EMAIL_INPUT = (By.ID, "id_email")
    PASSWORD1_INPUT = (By.ID, "id_password1")
    PASSWORD2_INPUT = (By.ID, "id_password2")
    ROLE_SELECT = (By.ID, "id_role")
    DEPARTMENT_INPUT = (By.ID, "id_department")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div[role='alert'].alert-error")

    def open(self):
        """Открывает страницу регистрации"""
        return super().open(self.URL_PATH)

    def fill_username(self, username):
        """Заполняет поле имени пользователя"""
        self.fill(*self.USERNAME_INPUT, username)
        return self

    def fill_display_name(self, display_name):
        """Заполняет отображаемое имя"""
        if display_name:
            self.fill(*self.DISPLAY_NAME_INPUT, display_name)
        return self

    def fill_email(self, email):
        """Заполняет email"""
        self.fill(*self.EMAIL_INPUT, email)
        return self

    def fill_password(self, password):
        """Заполняет пароль (оба поля)"""
        self.fill(*self.PASSWORD1_INPUT, password)
        self.fill(*self.PASSWORD2_INPUT, password)
        return self

    def select_role(self, role_value):
        """Выбирает роль из выпадающего списка"""
        role_element = self.find_element(*self.ROLE_SELECT)
        select = Select(role_element)
        select.select_by_value(role_value)
        return self

    def fill_department(self, department):
        """Заполняет факультет/кафедру"""
        if department:
            self.fill(*self.DEPARTMENT_INPUT, department)
        return self

    def submit(self):
        """Нажимает кнопку регистрации"""
        self.click(*self.SUBMIT_BUTTON)
        time.sleep(0.5)  # Ждем ответа сервера
        return self

    def register(self, username, email, password, display_name="", role="student", department=""):
        """
        Полный цикл регистрации.

        Args:
            username: Имя пользователя
            email: Email
            password: Пароль
            display_name: Отображаемое имя
            role: Роль (student/teacher/other)
            department: Факультет
        """
        self.fill_username(username)
        self.fill_display_name(display_name)
        self.fill_email(email)
        self.fill_password(password)
        self.select_role(role)
        self.fill_department(department)
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