"""
Тесты для проверки регистрации и авторизации.
Используют Page Object Model.
"""

import pytest
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage


class TestRegistration:
    """Тесты регистрации"""

    def test_registration_success(self, driver, site_url):
        """TC-1: Успешная регистрация нового пользователя"""
        register_page = RegisterPage(driver, site_url)
        register_page.open()

        register_page.register(
            username="testuser_auto",
            email="test@example.com",
            password="TestPassword123",
            display_name="Test User",
            role="student",
            department="IT"
        )

        # Проверяем успех
        assert register_page.is_success_message_displayed(), "Сообщение об успехе не появилось"
        assert "profile" in register_page.get_current_url(), "Не перенаправило на профиль"
        print("✅ Тест регистрации пройден!")

    def test_registration_duplicate_username(self, driver, site_url):
        """TC-2: Регистрация с существующим именем"""
        # Создаем первого пользователя
        register_page = RegisterPage(driver, site_url)
        register_page.open()
        register_page.register(
            username="duplicate_test",
            email="first@example.com",
            password="TestPassword123",
            role="student"
        )

        # Выходим
        driver.get(f"{site_url}/logout/")

        # Пробуем зарегистрировать с тем же именем
        register_page.open()
        register_page.register(
            username="duplicate_test",
            email="second@example.com",
            password="NewPassword123",
            role="student"
        )

        # Проверяем ошибку
        assert register_page.is_error_message_displayed(), "Ошибка не появилась"
        assert "уже существует" in register_page.get_error_message().lower()
        print("✅ Тест дубликата пройден!")


class TestLogin:
    """Тесты входа в систему"""

    def test_login_success(self, driver, site_url):
        """TC-3: Успешный вход"""
        # Создаем пользователя
        register_page = RegisterPage(driver, site_url)
        register_page.open()
        register_page.register(
            username="login_test_user",
            email="login@example.com",
            password="LoginPass123",
            role="student"
        )

        # Выходим
        driver.get(f"{site_url}/logout/")

        # Входим
        login_page = LoginPage(driver, site_url)
        login_page.open()
        login_page.login("login_test_user", "LoginPass123")

        # Проверяем успех
        assert login_page.is_success_message_displayed(), "Сообщение об успехе не появилось"
        assert not login_page.is_on_login_page(), "Остались на странице входа"
        print("✅ Тест входа пройден!")

    def test_login_invalid_password(self, driver, site_url):
        """TC-4: Вход с неверным паролем"""
        login_page = LoginPage(driver, site_url)
        login_page.open()
        login_page.login("testuser", "WrongPassword123")

        # Проверяем ошибку
        assert login_page.is_error_message_displayed(), "Ошибка не появилась"
        assert "неверное" in login_page.get_error_message().lower() or \
               "неверный" in login_page.get_error_message().lower()
        print("✅ Тест неверного пароля пройден!")

    def test_login_empty_fields(self, driver, site_url):
        """TC-5: Вход с пустыми полями"""
        login_page = LoginPage(driver, site_url)
        login_page.open()
        login_page.submit()  # Просто нажимаем кнопку без заполнения

        # Проверяем, что остались на странице входа
        assert login_page.is_on_login_page(), "Должны остаться на странице входа"
        print("✅ Тест пустых полей пройден!")


class TestProfile:
    """Тесты профиля"""

    def test_profile_access_after_login(self, driver, site_url):
        """TC-6: Доступ к профилю после входа"""
        # Регистрируемся
        register_page = RegisterPage(driver, site_url)
        register_page.open()
        register_page.register(
            username="profile_test",
            email="profile@example.com",
            password="ProfilePass123",
            role="student"
        )

        # Проверяем, что мы на странице профиля
        profile_page = ProfilePage(driver, site_url)
        assert profile_page.is_on_profile_page(), "Не на странице профиля"
        print("✅ Тест доступа к профилю пройден!")