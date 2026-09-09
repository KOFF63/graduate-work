from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def test_search_with_selenium():
    # Автоматически скачивает и подключает драйвер
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get("https://duckduckgo.com")

        # Ждем поле ввода
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        search_box.send_keys("QA Automation Python")
        search_box.submit()

        # Ждем результаты
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )

        assert "QA Automation" in driver.title
        print("✅ Тест успешно выполнен!")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_search_with_selenium()