# Портфолио AQA на Python — Django-проект с автотестами

Учебная платформа (Django) с полным набором автотестов: **UI (Selenium), API (requests), DB (SQL)**.  
Демонстрирует навыки для позиции **Junior QA Automation Engineer** с уклоном в backend.

## 🛠 Стек

- **Python 3.13**, Django 5.2
- **Pytest** — фикстуры, параметризация, маркеры (`api`, `ui`, `db`)
- **Selenium WebDriver** + Page Object Model (UI)
- **requests** — API-тесты с CSRF-сессиями
- **SQLite** — проверки БД, JOIN из нескольких таблиц
- **Allure** — отчётность
- **GitHub Actions** — CI/CD

## 📊 Что тестируется (42 автотеста)

### UI-тесты (16) — Selenium + POM
- Авторизация: регистрация, вход, неверный пароль, пустые поля, доступ к профилю
- Материалы: главная, приветствие анонима, поиск (требует логина), пустой запрос, добавление (только админ), 404
- Дополнительные: базовые проверки Selenium

### API-тесты (20) — requests + CSRF
- **Регистрация:** успех, дубликат, невалидные данные (параметризация: пустой username, пустой пароль, пароли не совпадают)
- **Логин:** успех, неверный пароль
- **Доступ:** профиль требует авторизации, профиль доступен после логина
- **Материалы:** главная (аноним/авторизован), поиск требует логина, пустой запрос, запрет добавления студенту, 404 для несуществующего предмета
- **Добавление материала (админ):** успешное добавление, запрет студенту, невалидные данные (пустой title, пустой description)

### DB-тесты (6) — SQL + JOIN
- Пользователь создаётся в `auth_user`
- Профиль создаётся автоматически (сигнал `post_save`) — **JOIN** `auth_user` + `users_userprofile`
- **JOIN** `auth_user` + `materials_material`
- Структура таблицы `materials_material`
- Материал сохраняется в БД с правильными полями — **JOIN** `materials_material` + `materials_subject`
- Материал привязан к автору-админу — **JOIN** `materials_material` + `auth_user`

## 🧪 Тест-кейсы (пример)

| ID | Шаги | Ожидаемый результат | Тип |
|----|------|---------------------|-----|
| TC-01 | POST `/users/register/` с валидными данными | 302 → `/users/profile/`, пользователь в БД | API |
| TC-02 | POST `/users/register/` с дубликатом | 302 → `/users/register/` | API |
| TC-03 | GET `/users/profile/` без авторизации | 302 → `/users/login/` | API |
| TC-04 | GET `/subject/999999/` | 404 | API |
| TC-05 | POST `/add/` от админа | 302 → `/subject/<id>/`, материал в БД | API |
| TC-06 | POST `/add/` от студента | 302 → `/users/login/` | API |
| TC-07 | POST `/add/` с пустым title | 302 → `/add/` | API |
| TC-08 | Проверка БД после регистрации | запись в `auth_user` + `users_userprofile` | DB |
| TC-09 | JOIN `auth_user` + `materials_material` | запрос выполняется, данные корректны | DB |
| TC-10 | Проверка БД после добавления материала | запись в `materials_material` + `materials_subject` | DB |

## 📁 Структура проекта
```
graduate_work/
├── config/ # настройки Django
├── materials/ # приложение материалов
├── users/ # приложение пользователей
├── tests/
│ ├── conftest.py # фикстуры: driver, api_session, admin_session, test_subject, clean_database
│ ├── api/
│ │ ├── test_auth_api.py # 9 тестов
│ │ ├── test_materials_api.py # 7 тестов
│ │ └── test_add_material_api.py # 4 теста
│ ├── db/
│ │ ├── test_db_checks.py # 4 теста (JOIN)
│ │ └── test_add_material_db.py # 2 теста (JOIN)
│ ├── pages/ # Page Object Model для UI
│ ├── test_auth.py # UI-тесты авторизации
│ ├── test_materials.py # UI-тесты материалов
│ └── test_simple.py # базовые UI-тесты
├── pytest.ini # маркеры, Allure
├── requirements.txt
└── .github/workflows/ # CI

```
```
bash
pip install -r requirements.txt
2. Запуск сервера (терминал №1)
bash
python manage.py runserver
3. Запуск тестов (терминал №2)
Все API + DB тесты (26):

bash
pytest tests/api tests/db -v
Только API (20):

bash
pytest tests/api -v
Только DB (6):

bash
pytest tests/db -v
Только UI (16):

bash
pytest tests/ -v -m ui
По маркерам:

bash
pytest -m api -v
pytest -m db -v
С отчётом Allure:

bash
pytest tests/api tests/db --alluredir=allure-results
allure serve allure-results
🔧 CI (GitHub Actions)
При каждом push запускаются:

API-тесты

DB-тесты

UI-тесты (headless Chrome)

📌 Ключевые навыки
✅ PyTest: фикстуры (включая autouse), параметризация, маркеры, conftest.py

✅ API-тестирование: requests, CSRF-сессии, проверка статусов и редиректов

✅ SQL: запросы с JOIN из нескольких таблиц, PRAGMA table_info

✅ Интеграционное тестирование: регистрация → профиль в БД → добавление материала

✅ Page Object Model для UI-тестов

✅ CI/CD: GitHub Actions

✅ Allure — отчётность

✅ Клиент-серверная архитектура, HTTP-методы и коды статусов

✅ Git

📬 Контакты
GitHub: KOFF63

Проект: graduate-work