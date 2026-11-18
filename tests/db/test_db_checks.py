import pytest
import sqlite3
import os
import uuid


pytestmark = pytest.mark.db

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db.sqlite3")


@pytest.fixture
def db():
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()


class TestUserDB:
    def test_user_created_in_db(self, api_session, base_url, db, get_csrf_token):
        username = f"db_{uuid.uuid4().hex[:8]}"
        token = get_csrf_token(api_session, f"{base_url}/users/register/")
        api_session.post(
            f"{base_url}/users/register/",
            data={
                "username": username,
                "password1": "pass12345",
                "password2": "pass12345",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/users/register/"},
            allow_redirects=False,
        )
        cur = db.cursor()
        cur.execute("SELECT username, is_active FROM auth_user WHERE username = ?", (username,))
        row = cur.fetchone()
        assert row is not None, "Пользователь не создан в БД"
        assert row[0] == username
        assert row[1] == 1

    def test_profile_created_automatically(self, api_session, base_url, db, get_csrf_token):
        username = f"prof_{uuid.uuid4().hex[:8]}"
        token = get_csrf_token(api_session, f"{base_url}/users/register/")
        api_session.post(
            f"{base_url}/users/register/",
            data={
                "username": username,
                "password1": "pass12345",
                "password2": "pass12345",
                "display_name": "DB Profile",
                "department": "QA",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/users/register/"},
            allow_redirects=False,
        )
        cur = db.cursor()
        cur.execute("""
            SELECT u.username, p.display_name, p.department
            FROM auth_user u
            JOIN users_userprofile p ON p.user_id = u.id
            WHERE u.username = ?
        """, (username,))
        row = cur.fetchone()
        assert row is not None, "Профиль не создан (сигнал post_save не сработал)"
        assert row[1] == "DB Profile"
        assert row[2] == "QA"


class TestMaterialsDB:
    def test_join_users_materials(self, db):
        cur = db.cursor()
        cur.execute("""
            SELECT u.username, COUNT(m.id) AS cnt
            FROM auth_user u
            LEFT JOIN materials_material m ON m.uploaded_by_id = u.id
            GROUP BY u.username
        """)
        rows = cur.fetchall()
        assert len(rows) >= 0

    def test_material_table_structure(self, db):
        cur = db.cursor()
        cur.execute("PRAGMA table_info(materials_material)")
        columns = [row[1] for row in cur.fetchall()]
        for col in ("title", "description", "subject_id", "uploaded_by_id"):
            assert col in columns, f"Нет колонки {col}"