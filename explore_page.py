from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def explore_register_page():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get("http://127.0.0.1:8000/register/")

        print("\n" + "=" * 80)
        print("ИССЛЕДОВАНИЕ СТРАНИЦЫ РЕГИСТРАЦИИ")
        print("=" * 80)

        # Находим все поля ввода
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n📝 Найдено полей ввода: {len(inputs)}")
        print("-" * 80)

        for i, inp in enumerate(inputs, 1):
            input_type = inp.get_attribute("type")
            input_name = inp.get_attribute("name")
            input_id = inp.get_attribute("id")
            input_class = inp.get_attribute("class")
            input_placeholder = inp.get_attribute("placeholder")

            print(f"{i}. type='{input_type}'")
            print(f"   name='{input_name}'")
            print(f"   id='{input_id}'")
            print(f"   class='{input_class}'")
            print(f"   placeholder='{input_placeholder}'")
            print("-" * 40)

        # Находим все кнопки
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Найдено кнопок: {len(buttons)}")
        print("-" * 80)

        for i, btn in enumerate(buttons, 1):
            btn_type = btn.get_attribute("type")
            btn_text = btn.text
            btn_class = btn.get_attribute("class")
            print(f"{i}. type='{btn_type}', text='{btn_text}', class='{btn_class}'")

        # Находим все формы
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"\n📋 Найдено форм: {len(forms)}")
        print("-" * 80)

        for i, form in enumerate(forms, 1):
            form_action = form.get_attribute("action")
            form_method = form.get_attribute("method")
            print(f"{i}. action='{form_action}', method='{form_method}'")

        print("\n" + "=" * 80)
        print("✅ Исследование завершено!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    explore_register_page()