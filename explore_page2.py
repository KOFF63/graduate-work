from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def explore_register_page():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        print("Загружаем страницу...")
        driver.get("http://127.0.0.1:8000/register/")

        # Ждем 3 секунды для полной загрузки
        time.sleep(3)

        print("\n" + "=" * 80)
        print("ИССЛЕДОВАНИЕ СТРАНИЦЫ РЕГИСТРАЦИИ")
        print("=" * 80)
        print(f"Заголовок страницы: {driver.title}")
        print(f"URL: {driver.current_url}")
        print("=" * 80)

        # Ждем появления хотя бы одного элемента
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Страница загружена")
        except:
            print("❌ Страница не загружена")

        # Ищем форму через разные способы
        print("\n🔍 Ищем элементы разными способами:")
        print("-" * 80)

        # Способ 1: Поиск всех элементов
        all_elements = driver.find_elements(By.XPATH, "//*")
        print(f"Всего элементов на странице: {len(all_elements)}")

        # Способ 2: Поиск по тегу form
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Найдено форм по тегу <form>: {len(forms)}")

        # Способ 3: Поиск по CSS
        inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        print(f"Найдено input по CSS: {len(inputs)}")

        # Способ 4: Поиск по XPath
        inputs_xpath = driver.find_elements(By.XPATH, "//input")
        print(f"Найдено input по XPath: {len(inputs_xpath)}")

        # Способ 5: Поиск с ожиданием
        try:
            wait = WebDriverWait(driver, 5)
            element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            print(f"✅ Элемент найден через wait: {element.get_attribute('outerHTML')[:100]}...")
        except:
            print("❌ Элемент не найден через wait")

        # Если элементов нет - выводим весь HTML
        if len(all_elements) < 50:
            print("\n📄 Похоже, страница не загрузилась полностью. Выводим HTML:")
            print("=" * 80)
            print(driver.page_source[:2000])
            print("=" * 80)

        # Проверяем, нет ли iframe
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"\nНайдено iframe: {len(frames)}")
        for i, frame in enumerate(frames):
            print(f"  iframe {i + 1}: {frame.get_attribute('src')}")

        # Проверяем shadow DOM
        print("\n🔍 Ищем элементы в Shadow DOM:")
        print("-" * 80)

        # Проверяем, есть ли элементы с shadow-root
        elements_with_shadow = driver.execute_script("""
            var elements = document.querySelectorAll('*');
            var result = [];
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].shadowRoot) {
                    result.push(elements[i].tagName);
                }
            }
            return result;
        """)

        if elements_with_shadow:
            print(f"Найдены элементы с Shadow DOM: {elements_with_shadow}")
            # Пытаемся получить содержимое первого shadow root
            try:
                shadow_content = driver.execute_script("""
                    var el = document.querySelector('*');
                    if (el && el.shadowRoot) {
                        return el.shadowRoot.innerHTML;
                    }
                    return 'Shadow root не найден';
                """)
                print(f"Содержимое Shadow DOM: {shadow_content[:500]}")
            except:
                pass
        else:
            print("Shadow DOM не найден")

        # Проверяем, есть ли реакт-приложение
        react_root = driver.execute_script("""
            return document.getElementById('root') || 
                   document.getElementById('app') || 
                   document.querySelector('[data-reactroot]') || 
                   'Не найден';
        """)
        print(f"\nReact root: {react_root}")

        # Пробуем найти элементы по тексту
        print("\n🔍 Ищем по тексту:")
        elements_with_text = driver.find_elements(By.XPATH,
                                                  "//*[contains(text(), 'регистрац') or contains(text(), 'Регистрац')]")
        print(f"Элементов с текстом 'регистрац': {len(elements_with_text)}")

        # Проверяем, не перенаправляет ли на другую страницу
        if "login" in driver.current_url:
            print("\n⚠️ Перенаправлено на страницу входа!")
        elif "register" in driver.current_url:
            print("\n✅ На странице регистрации")
        else:
            print(f"\n⚠️ Текущий URL: {driver.current_url}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


if __name__ == "__main__":
    explore_register_page()