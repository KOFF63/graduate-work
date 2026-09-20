"""
Базовый класс для всех страниц.
Содержит общие методы для работы с элементами.
"""


import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



class BasePage:
    """Базовый класс для всех страниц сайта"""

    def __init__(self, driver, base_url):
        """
        Инициализация страницы.

        Args:
            driver: Selenium WebDriver
            base_url: Базовый URL сайта
        """
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def open(self, url_path=""):
        """Открывает страницу по указанному пути"""
        self.driver.get(f"{self.base_url}{url_path}")
        self.wait.until(EC.presence_of_element_located(("tag name", "body")))
        return self

    def find_element(self, by, value):
        """Находит элемент с ожиданием"""
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by, value):
        """Находит все элементы"""
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        """Кликает по элементу через JavaScript (обход перекрытий)"""
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def fill(self, by, value, text):
        """Заполняет поле ввода"""
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)
        return element

    def get_text(self, by, value):
        """Получает текст элемента"""
        return self.find_element(by, value).text

    def is_element_present(self, by, value, timeout=5):
        """Проверяет, есть ли элемент на странице (с ожиданием видимости)"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def get_current_url(self):
        """Возвращает текущий URL"""
        return self.driver.current_url