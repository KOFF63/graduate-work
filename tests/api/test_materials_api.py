import pytest

pytestmark = pytest.mark.api


class TestMaterialsAPI:
    def test_home_anonymous(self, api_session, base_url):
        resp = api_session.get(f"{base_url}/")
        assert resp.status_code == 200

    def test_home_authorized(self, auth_session, base_url):
        resp = auth_session.get(f"{base_url}/")
        assert resp.status_code == 200

    def test_search_requires_auth(self, api_session, base_url):
        resp = api_session.get(f"{base_url}/search/?q=test", allow_redirects=False)
        assert resp.status_code == 302
        assert "/users/login/" in resp.headers.get("Location", "")

    def test_search_empty_query(self, auth_session, base_url):
        resp = auth_session.get(f"{base_url}/search/?q=")
        assert resp.status_code == 200

    def test_add_material_forbidden_for_student(self, auth_session, base_url):
        resp = auth_session.get(f"{base_url}/add/", allow_redirects=False)
        assert resp.status_code == 302
        assert "/users/login/" in resp.headers.get("Location", "")

    def test_subject_404(self, auth_session, base_url):
        resp = auth_session.get(f"{base_url}/subject/999999/")
        assert resp.status_code == 404

    def test_subject_requires_auth(self, api_session, base_url):
        resp = api_session.get(f"{base_url}/subject/1/", allow_redirects=False)
        assert resp.status_code == 302
        assert "/users/login/" in resp.headers.get("Location", "")