import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
def driver(request):
    """Фикстура для Selenium WebDriver с поддержкой скриншотов Allure"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver

    # Если тест упал — делаем скриншот
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="Скриншот при падении",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(
                driver.page_source,
                name="HTML страницы при падении",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as e:
            print(f"⚠️ Не удалось сделать скриншот: {e}")

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для получения статуса теста (нужен для скриншотов)"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def site_url():
    """Базовый URL сайта"""
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