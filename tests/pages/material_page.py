"""
Page Object для страниц с материалами.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage


class HomePage(BasePage):
    """Главная страница"""

    URL_PATH = "/"

    # Локаторы
    SEARCH_LINK = (By.LINK_TEXT, "Поиск")
    SUBJECT_CARD = (By.CSS_SELECTOR, ".subject-card")
    RECENT_MATERIALS = (By.CSS_SELECTOR, ".material-card")
    ADD_MATERIAL_LINK = (By.LINK_TEXT, "Добавить материал")

    def open(self):
        return super().open(self.URL_PATH)

    def is_logged_in(self):
        """Проверяет, авторизован ли пользователь"""
        return "welcome" not in self.get_current_url() and \
            not self.is_element_present(By.LINK_TEXT, "Войти", timeout=2)

    def go_to_search(self):
        """Переходит на страницу поиска"""
        self.click(*self.SEARCH_LINK)
        return SearchPage(self.driver, self.base_url)

    def go_to_add_material(self):
        """Переходит на страницу добавления материала"""
        self.click(*self.ADD_MATERIAL_LINK)
        return AddMaterialPage(self.driver, self.base_url)


class SearchPage(BasePage):
    """Страница поиска материалов"""

    URL_PATH = "/search/"

    # Локаторы
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    RESULTS = (By.CSS_SELECTOR, ".material-card")
    NO_RESULTS = (By.CSS_SELECTOR, ".alert-info, .no-results")
    SEARCH_TIME = (By.CSS_SELECTOR, ".search-time")

    def open(self, query=""):
        """Открывает страницу поиска (можно сразу с запросом)"""
        if query:
            super().open(f"{self.URL_PATH}?q={query}")
        else:
            super().open(self.URL_PATH)
        return self

    def search(self, query):
        """Выполняет поиск"""
        self.fill(*self.SEARCH_INPUT, query)
        self.click(*self.SEARCH_BUTTON)
        time.sleep(0.5)
        return self

    def get_results_count(self):
        """Возвращает количество найденных результатов"""
        return len(self.find_elements(*self.RESULTS))

    def has_results(self):
        """Проверяет, есть ли результаты поиска"""
        return self.get_results_count() > 0

    def get_result_titles(self):
        """Возвращает список заголовков найденных материалов"""
        results = self.find_elements(*self.RESULTS)
        return [r.text for r in results]


class SubjectPage(BasePage):
    """Страница предмета с материалами"""

    URL_PATH = "/subject/{subject_id}/"

    # Локаторы
    SUBJECT_TITLE = (By.TAG_NAME, "h1")
    MATERIALS = (By.CSS_SELECTOR, ".material-card")
    FILTER_PDF = (By.CSS_SELECTOR, "a[href*='type=pdf']")
    FILTER_VIDEO = (By.CSS_SELECTOR, "a[href*='type=video']")
    NO_MATERIALS = (By.CSS_SELECTOR, ".alert-info, .no-materials")

    def open(self, subject_id):
        """Открывает страницу предмета по ID"""
        return super().open(self.URL_PATH.format(subject_id=subject_id))

    def get_materials_count(self):
        """Возвращает количество материалов на странице"""
        return len(self.find_elements(*self.MATERIALS))

    def get_title(self):
        """Возвращает заголовок страницы"""
        return self.get_text(*self.SUBJECT_TITLE)

    def filter_by_pdf(self):
        """Фильтрует материалы по PDF"""
        self.click(*self.FILTER_PDF)
        time.sleep(0.5)
        return self


class AddMaterialPage(BasePage):
    """Страница добавления материала (только для админов)"""

    URL_PATH = "/add/"

    # Локаторы
    TITLE_INPUT = (By.NAME, "title")
    DESCRIPTION_INPUT = (By.NAME, "description")
    SUBJECT_SELECT = (By.NAME, "subject")
    TYPE_SELECT = (By.NAME, "material_type")
    TAGS_INPUT = (By.NAME, "tags")
    EXTERNAL_LINK_INPUT = (By.NAME, "external_link")
    FILE_INPUT = (By.NAME, "file")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-error")

    def open(self):
        return super().open(self.URL_PATH)

    def fill_title(self, title):
        self.fill(*self.TITLE_INPUT, title)
        return self

    def fill_description(self, description):
        self.fill(*self.DESCRIPTION_INPUT, description)
        return self

    def select_subject(self, subject_value):
        select = Select(self.find_element(*self.SUBJECT_SELECT))
        select.select_by_value(str(subject_value))
        return self

    def select_type(self, type_value):
        select = Select(self.find_element(*self.TYPE_SELECT))
        select.select_by_value(type_value)
        return self

    def fill_tags(self, tags):
        if tags:
            self.fill(*self.TAGS_INPUT, tags)
        return self

    def fill_external_link(self, link):
        if link:
            self.fill(*self.EXTERNAL_LINK_INPUT, link)
        return self

    def submit(self):
        """Нажимает кнопку сохранения"""
        self.click(*self.SUBMIT_BUTTON)
        time.sleep(0.5)
        return self

    def create_material(self, title, description, subject_value, material_type="text", tags="", external_link=""):
        """Полный цикл создания материала"""
        self.fill_title(title)
        self.fill_description(description)
        self.select_subject(subject_value)
        self.select_type(material_type)
        self.fill_tags(tags)
        self.fill_external_link(external_link)
        self.submit()
        return self

    def is_success_message_displayed(self):
        return self.is_element_present(*self.SUCCESS_MESSAGE)

    def get_success_message(self):
        return self.get_text(*self.SUCCESS_MESSAGE)

    def is_error_message_displayed(self):
        return self.is_element_present(*self.ERROR_MESSAGE)

    def get_error_message(self):
        return self.get_text(*self.ERROR_MESSAGE)