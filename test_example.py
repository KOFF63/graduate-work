from playwright.sync_api import sync_playwright


def test_playwright_yandex():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://yandex.ru")

        # Способ 1: Ищем по text (если на русском)
        # Способ 2: Ищем по атрибуту (универсально)
        # Способ 3: Ищем по placeholder

        # Попробуем найти поле ввода разными способами
        try:
            # Пробуем найти по name="text" (старый вариант)
            page.wait_for_selector("input[name='text']", timeout=5000)
            page.fill("input[name='text']", "QA Automation Python")
        except:
            try:
                # Пробуем найти по name="q" (новый вариант)
                page.wait_for_selector("input[name='q']", timeout=5000)
                page.fill("input[name='q']", "QA Automation Python")
            except:
                # Пробуем найти по placeholder
                page.wait_for_selector("input[placeholder*='Найти']", timeout=5000)
                page.fill("input[placeholder*='Найти']", "QA Automation Python")

        page.keyboard.press("Enter")

        # Ждем появления результатов
        page.wait_for_selector("li.serp-item", state="visible", timeout=10000)

        # Проверяем, что заголовок содержит наш запрос
        assert "QA Automation" in page.title()

        browser.close()