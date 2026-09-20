"""
Тесты для проверки работы с материалами.
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def click_with_js(driver, element):
    """Клик по элементу через JavaScript (обход перекрытий)"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", element)


def register_user(driver, site_url, username, password="TestPass123", role="student"):
    """Вспомогательная функция: регистрация пользователя"""
    driver.get(f"{site_url}/register/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(username)
    driver.find_element(By.ID, "id_password1").send_keys(password)
    driver.find_element(By.ID, "id_password2").send_keys(password)

    if role:
        try:
            role_select = driver.find_element(By.ID, "id_role")
            Select(role_select).select_by_value(role)
        except:
            pass

    # Клик через JS
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    click_with_js(driver, submit_btn)
    time.sleep(2)


class TestHomePage:
    """Тесты главной страницы"""

    def test_home_page_loads(self, driver, site_url):
        """TC-M1: Главная страница загружается"""
        driver.get("http://127.0.0.1:8000/")
        assert "Учебные материалы" in driver.page_source or \
               "welcome" in driver.current_url or \
               "Учебные" in driver.title
        print("✅ Главная страница загружена!")

    def test_welcome_for_anonymous(self, driver, site_url):
        """TC-M2: Неавторизованный видит приветствие"""
        driver.get("http://127.0.0.1:8000/")
        page_source = driver.page_source
        assert "Войти" in page_source or "Регистрация" in page_source or \
               "Добро пожаловать" in page_source
        print("✅ Приветствие для анонима отображается!")


class TestSearch:
    """Тесты поиска материалов"""

    def test_search_page_requires_login(self, driver):
        """TC-M3: Страница поиска требует авторизации"""
        driver.get("http://127.0.0.1:8000/search/")
        assert "login" in driver.current_url
        print("✅ Поиск требует авторизации!")

    def test_search_with_empty_query(self, driver, site_url):
        """TC-M4: Поиск с пустым запросом"""
        # Регистрируемся через хелпер
        register_user(driver, site_url, "search_test_user")

        # Переходим на поиск
        driver.get("http://127.0.0.1:8000/search/")
        time.sleep(1)

        # Проверяем, что страница открылась без ошибок
        assert "search" in driver.current_url
        assert "404" not in driver.page_source
        print("✅ Поиск с пустым запросом работает!")


class TestAddMaterial:
    """Тесты добавления материала (для админов)"""

    def test_add_material_requires_admin(self, driver, site_url):
        """TC-M5: Обычный пользователь не может добавлять материалы"""
        # Регистрируемся как обычный пользователь
        register_user(driver, site_url, "regular_user_test")

        # Пробуем открыть страницу добавления
        driver.get("http://127.0.0.1:8000/add/")
        time.sleep(1)

        # Должно перенаправить на логин или показать ошибку
        assert "login" in driver.current_url or \
               "404" in driver.page_source or \
               "доступ" in driver.page_source.lower() or \
               "permission" in driver.page_source.lower()
        print("✅ Обычный пользователь не может добавлять материалы!")


class TestSubjectPage:
    """Тесты страницы предмета"""

    def test_subject_page_requires_login(self, driver):
        """TC-M6: Страница предмета требует авторизации"""
        driver.get("http://127.0.0.1:8000/subject/1/")
        assert "login" in driver.current_url
        print("✅ Страница предмета требует авторизации!")

    def test_subject_404_for_invalid_id(self, driver, site_url):
        """TC-M7: Несуществующий предмет возвращает 404"""
        # Авторизуемся через хелпер
        register_user(driver, site_url, "subject_test_user")

        # Открываем несуществующий предмет
        driver.get("http://127.0.0.1:8000/subject/99999/")
        time.sleep(1)

        # Должна быть страница 404
        assert "404" in driver.page_source or \
               "not found" in driver.page_source.lower() or \
               "не найдено" in driver.page_source.lower() or \
               "Page not found" in driver.page_source
        print("✅ Несуществующий предмет возвращает 404!")