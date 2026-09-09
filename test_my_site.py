import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"


class TestUserAuth:

    def test_registration_success(self, driver, base_url):
        """TC-1: Успешная регистрация"""
        driver.get(f"{base_url}/register/")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("testuser_auto")
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password1").send_keys("TestPassword123")
        driver.find_element(By.NAME, "password2").send_keys("TestPassword123")
        driver.find_element(By.NAME, "display_name").send_keys("Test User")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
        assert "Добро пожаловать" in success_msg.text
        assert "profile" in driver.current_url

    def test_registration_duplicate_username(self, driver, base_url):
        """TC-2: Регистрация с существующим именем"""
        driver.get(f"{base_url}/register/")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("duplicate_user")
        driver.find_element(By.NAME, "email").send_keys("first@example.com")
        driver.find_element(By.NAME, "password1").send_keys("TestPass123")
        driver.find_element(By.NAME, "password2").send_keys("TestPass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        driver.get(f"{base_url}/logout/")

        driver.get(f"{base_url}/register/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("duplicate_user")
        driver.find_element(By.NAME, "email").send_keys("second@example.com")
        driver.find_element(By.NAME, "password1").send_keys("NewPass123")
        driver.find_element(By.NAME, "password2").send_keys("NewPass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-danger")))
        assert "уже существует" in error_msg.text

    def test_login_success(self, driver, base_url):
        """TC-3: Успешный вход"""
        driver.get(f"{base_url}/register/")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("login_test")
        driver.find_element(By.NAME, "email").send_keys("login@example.com")
        driver.find_element(By.NAME, "password1").send_keys("LoginPass123")
        driver.find_element(By.NAME, "password2").send_keys("LoginPass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        driver.get(f"{base_url}/logout/")

        driver.get(f"{base_url}/login/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("login_test")
        driver.find_element(By.NAME, "password").send_keys("LoginPass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
        assert "Добро пожаловать" in success_msg.text

    def test_login_invalid_password(self, driver, base_url):
        """TC-4: Вход с неверным паролем"""
        driver.get(f"{base_url}/login/")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("WrongPassword")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-danger")))
        assert "Неверное имя пользователя или пароль" in error_msg.text