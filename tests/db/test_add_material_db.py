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


class TestAddMaterialDB:
    def test_material_saved_in_db(self, admin_session, base_url, test_subject, db, get_csrf_token):
        subject_id, subject_name = test_subject
        title = f"DB_Material_{uuid.uuid4().hex[:6]}"

        token = get_csrf_token(admin_session, f"{base_url}/add/")
        resp = admin_session.post(
            f"{base_url}/add/",
            data={
                "title": title,
                "description": "DB check description",
                "subject": subject_id,
                "material_type": "text",
                "tags": "db,check",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/add/"},
            allow_redirects=False,
        )
        assert resp.status_code == 302

        cur = db.cursor()
        cur.execute("""
            SELECT m.title, m.description, m.material_type, s.name
            FROM materials_material m
            JOIN materials_subject s ON s.id = m.subject_id
            WHERE m.title = ?
        """, (title,))
        row = cur.fetchone()
        assert row is not None, "Материал не сохранён в БД"
        assert row[0] == title
        assert row[1] == "DB check description"
        assert row[2] == "text"
        assert row[3] == subject_name

    def test_material_linked_to_uploader(self, admin_session, base_url, test_subject, db, get_csrf_token):
        subject_id, _ = test_subject
        title = f"Uploader_{uuid.uuid4().hex[:6]}"

        token = get_csrf_token(admin_session, f"{base_url}/add/")
        admin_session.post(
            f"{base_url}/add/",
            data={
                "title": title,
                "description": "Uploader check",
                "subject": subject_id,
                "material_type": "link",
                "external_link": "https://example.com",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/add/"},
            allow_redirects=False,
        )

        cur = db.cursor()
        cur.execute("""
            SELECT m.title, u.username, u.is_superuser
            FROM materials_material m
            JOIN auth_user u ON u.id = m.uploaded_by_id
            WHERE m.title = ?
        """, (title,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == title
        assert row[2] == 1, "Автор материала не суперюзер"