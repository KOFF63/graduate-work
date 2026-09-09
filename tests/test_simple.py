import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def click_with_js(driver, element):
    """Клик по элементу через JavaScript (обходит перекрытия)"""
    driver.execute_script("arguments[0].click();", element)


def test_registration_success(driver, site_url):
    """Тест: Успешная регистрация"""
    driver.get(f"{site_url}/register/")
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Заполняем форму
    wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys("testuser_auto")
    driver.find_element(By.ID, "id_display_name").send_keys("Test User")
    driver.find_element(By.ID, "id_email").send_keys("test@example.com")
    driver.find_element(By.ID, "id_password1").send_keys("TestPassword123")
    driver.find_element(By.ID, "id_password2").send_keys("TestPassword123")

    # Выбираем роль
    role_select = driver.find_element(By.ID, "id_role")
    select = Select(role_select)
    select.select_by_value("student")

    driver.find_element(By.ID, "id_department").send_keys("IT")

    # Находим и кликаем кнопку
    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(0.5)
    click_with_js(driver, submit_btn)

    # Проверяем результат
    try:
        success_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
        assert "Добро пожаловать" in success_msg.text
        print("✅ Тест регистрации пройден!")
    except:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        if "profile" in driver.current_url:
            print("✅ Тест регистрации пройден (перенаправление на профиль)!")
        else:
            errors = driver.find_elements(By.CLASS_NAME, "alert-danger")
            if errors:
                print(f"❌ Ошибки на странице: {errors[0].text}")
            print(f"❌ Текущий URL: {driver.current_url}")
            assert False, "Регистрация не удалась"


def test_login_success(driver, site_url):
    """Тест: Успешный вход"""
    # Сначала создаем пользователя
    driver.get(f"{site_url}/register/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Регистрируем пользователя
    wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys("login_test_user")
    driver.find_element(By.ID, "id_display_name").send_keys("Login Test")
    driver.find_element(By.ID, "id_email").send_keys("login_test@example.com")
    driver.find_element(By.ID, "id_password1").send_keys("LoginPass123")
    driver.find_element(By.ID, "id_password2").send_keys("LoginPass123")

    # Выбираем роль
    role_select = driver.find_element(By.ID, "id_role")
    select = Select(role_select)
    select.select_by_value("student")

    driver.find_element(By.ID, "id_department").send_keys("IT")

    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(0.5)
    click_with_js(driver, submit_btn)

    time.sleep(2)

    # Выходим
    driver.get(f"{site_url}/logout/")
    time.sleep(1)

    # Входим
    driver.get(f"{site_url}/login/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Заполняем форму входа
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("login_test_user")
    driver.find_element(By.NAME, "password").send_keys("LoginPass123")

    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(0.5)
    click_with_js(driver, submit_btn)

    # Проверяем успешный вход
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    if "login" not in driver.current_url:
        print("✅ Тест входа пройден!")
    else:
        errors = driver.find_elements(By.CLASS_NAME, "alert-danger")
        if errors:
            print(f"❌ Ошибка входа: {errors[0].text}")
        print(f"❌ Вход не удался. Текущий URL: {driver.current_url}")
        assert False, "Вход не удался"


def test_login_invalid_password(driver, site_url):
    """Тест: Вход с неверным паролем"""
    driver.get(f"{site_url}/login/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Заполняем форму входа
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("testuser")
    driver.find_element(By.NAME, "password").send_keys("WrongPassword123")

    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(0.5)
    click_with_js(driver, submit_btn)

    # Проверяем сообщение об ошибке
    try:
        error_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-danger")))
        assert "Неверное" in error_msg.text or "неверный" in error_msg.text
        print("✅ Тест неверного пароля пройден!")
    except:
        time.sleep(2)
        if "login" in driver.current_url:
            print("✅ Тест неверного пароля пройден (остались на странице входа)!")
        else:
            print(f"❌ Тест не пройден. Текущий URL: {driver.current_url}")
            assert False, "Неверный пароль пропущен"