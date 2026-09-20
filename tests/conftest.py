"""
Общие фикстуры для тестов.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys

# Добавляем папку tests в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django

    django.setup()
    from django.contrib.auth.models import User

    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Django не загружен: {e}")
    DJANGO_AVAILABLE = False
    User = None


@pytest.fixture
def driver():
    """Фикстура для Selenium WebDriver"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def site_url():
    """Базовый URL сайта (приложение users)"""
    return "http://127.0.0.1:8000/users"


@pytest.fixture(autouse=True)
def clean_database():
    """Автоматически очищает тестовых пользователей после каждого теста"""
    yield

    if DJANGO_AVAILABLE and User:
        try:
            test_users = User.objects.filter(username__icontains='test')
            for user in test_users:
                if not user.is_superuser and not user.is_staff:
                    username = user.username
                    user.delete()
                    print(f"🧹 Очистка: удален пользователь {username}")
        except Exception as e:
            print(f"⚠️ Ошибка при очистке: {e}")