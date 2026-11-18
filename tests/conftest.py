import pytest
import allure
import os
import sys
import uuid
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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


# ===== Selenium (UI) =====
@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if os.getenv('CI'):
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.maximize_window()
    yield driver

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
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def site_url():
    return "http://127.0.0.1:8000/users"


@pytest.fixture(autouse=True)
def clean_database():
    yield
    if DJANGO_AVAILABLE and User:
        try:
            test_users = User.objects.filter(
                username__regex=r'^(user_|db_|prof_|test|admin_)'
            )
            for user in test_users:
                if not user.is_superuser and not user.is_staff:
                    username = user.username
                    user.delete()
                    print(f"🧹 Очистка: удален пользователь {username}")
        except Exception as e:
            print(f"⚠️ Ошибка при очистке: {e}")


# ===== API / DB =====
API_BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def base_url():
    return API_BASE_URL


@pytest.fixture
def api_session():
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def get_csrf_token():
    """Возвращает функцию для получения CSRF-токена."""
    def _get(session, url):
        session.get(url)
        return session.cookies.get("csrftoken")
    return _get


@pytest.fixture
def unique_username():
    return f"user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def registered_user(api_session, base_url, unique_username, get_csrf_token):
    password = "testpass123"
    token = get_csrf_token(api_session, f"{base_url}/users/register/")
    resp = api_session.post(
        f"{base_url}/users/register/",
        data={
            "username": unique_username,
            "email": f"{unique_username}@test.com",
            "password1": password,
            "password2": password,
            "display_name": "Test User",
            "role": "student",
            "department": "IT",
            "csrfmiddlewaretoken": token,
        },
        headers={"Referer": f"{base_url}/users/register/"},
        allow_redirects=False,
    )
    assert resp.status_code == 302, f"Регистрация не удалась: {resp.status_code}"
    return unique_username, password


@pytest.fixture
def auth_session(api_session, base_url, registered_user, get_csrf_token):
    username, password = registered_user
    token = get_csrf_token(api_session, f"{base_url}/users/login/")
    resp = api_session.post(
        f"{base_url}/users/login/",
        data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": token,
        },
        headers={"Referer": f"{base_url}/users/login/"},
        allow_redirects=False,
    )
    assert resp.status_code == 302, f"Логин не удался: {resp.status_code}"
    return api_session

@pytest.fixture
def admin_session(api_session, base_url, get_csrf_token):
    """Создаёт суперюзера и логинит его. Возвращает сессию."""
    username = f"admin_{uuid.uuid4().hex[:8]}"
    password = "adminpass123"

    if DJANGO_AVAILABLE and User:
        User.objects.create_superuser(
            username=username,
            email=f"{username}@test.com",
            password=password,
        )
    else:
        pytest.skip("Django недоступен — пропускаем админ-тесты")

    token = get_csrf_token(api_session, f"{base_url}/users/login/")
    resp = api_session.post(
        f"{base_url}/users/login/",
        data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": token,
        },
        headers={"Referer": f"{base_url}/users/login/"},
        allow_redirects=False,
    )
    assert resp.status_code == 302, f"Логин админа не удался: {resp.status_code}"
    return api_session


@pytest.fixture
def test_subject():
    """Создаёт тестовый предмет через Django ORM. Возвращает (id, name)."""
    if not (DJANGO_AVAILABLE and User):
        pytest.skip("Django недоступен")

    from materials.models import Subject
    name = f"TestSubject_{uuid.uuid4().hex[:6]}"
    subject = Subject.objects.create(name=name, description="Created by test")
    yield subject.id, subject.name
    subject.delete()