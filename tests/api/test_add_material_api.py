import pytest
import uuid

pytestmark = pytest.mark.api


class TestAddMaterialAPI:
    def test_admin_can_add_material(self, admin_session, base_url, test_subject, get_csrf_token):
        subject_id, _ = test_subject
        title = f"Material_{uuid.uuid4().hex[:6]}"

        token = get_csrf_token(admin_session, f"{base_url}/add/")
        resp = admin_session.post(
            f"{base_url}/add/",
            data={
                "title": title,
                "description": "Test description",
                "subject": subject_id,
                "material_type": "text",
                "tags": "test,qa",
                "external_link": "",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/add/"},
            allow_redirects=False,
        )
        assert resp.status_code == 302
        assert f"/subject/{subject_id}/" in resp.headers.get("Location", "")

    def test_student_cannot_add_material(self, auth_session, base_url, test_subject):
        resp = auth_session.get(f"{base_url}/add/", allow_redirects=False)
        assert resp.status_code == 302
        assert "/users/login/" in resp.headers.get("Location", "")

    @pytest.mark.parametrize("payload, description", [
        ({"title": "", "description": "desc"}, "пустой title"),
        ({"title": "T", "description": ""}, "пустой description"),
    ])
    def test_admin_add_material_invalid(self, admin_session, base_url, test_subject, get_csrf_token, payload, description):
        subject_id, _ = test_subject
        token = get_csrf_token(admin_session, f"{base_url}/add/")
        data = dict(payload)
        data["subject"] = subject_id
        data["material_type"] = "text"
        data["csrfmiddlewaretoken"] = token
        resp = admin_session.post(
            f"{base_url}/add/",
            data=data,
            headers={"Referer": f"{base_url}/add/"},
            allow_redirects=False,
        )
        assert resp.status_code == 302, f"Кейс: {description}"
        assert "/add/" in resp.headers.get("Location", "")