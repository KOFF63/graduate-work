import pytest
import uuid


pytestmark = pytest.mark.api


class TestRegisterAPI:
    def test_register_success(self, api_session, base_url, get_csrf_token):
        username = f"user_{uuid.uuid4().hex[:8]}"
        token = get_csrf_token(api_session, f"{base_url}/users/register/")
        resp = api_session.post(
            f"{base_url}/users/register/",
            data={
                "username": username,
                "email": f"{username}@test.com",
                "password1": "pass12345",
                "password2": "pass12345",
                "display_name": "New User",
                "role": "student",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/users/register/"},
            allow_redirects=False,
        )
        assert resp.status_code == 302
        assert "/users/profile/" in resp.headers.get("Location", "")

    def test_register_duplicate_username(self, api_session, base_url, registered_user, get_csrf_token):
        username, _ = registered_user
        token = get_csrf_token(api_session, f"{base_url}/users/register/")
        resp = api_session.post(
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
        assert resp.status_code == 302
        assert "/users/register/" in resp.headers.get("Location", "")

    @pytest.mark.parametrize("payload, description", [
        ({"password1": "a", "password2": "a"}, "пустой username"),
        ({"username": "u", "password1": "", "password2": ""}, "пустой пароль"),
        ({"username": "u", "password1": "a", "password2": "b"}, "пароли не совпадают"),
    ])
    def test_register_invalid(self, api_session, base_url, payload, description, get_csrf_token):
        token = get_csrf_token(api_session, f"{base_url}/users/register/")
        data = dict(payload)
        data["csrfmiddlewaretoken"] = token
        resp = api_session.post(
            f"{base_url}/users/register/",
            data=data,
            headers={"Referer": f"{base_url}/users/register/"},
            allow_redirects=False,
        )
        assert resp.status_code == 302, f"Кейс: {description}"
        assert "/users/register/" in resp.headers.get("Location", "")


class TestLoginAPI:
    def test_login_success(self, api_session, base_url, registered_user, get_csrf_token):
        username, password = registered_user
        token = get_csrf_token(api_session, f"{base_url}/users/login/")
        resp = api_session.post(
            f"{base_url}/users/login/",
            data={
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/users/login/"},
            allow_redirects=False,
        )
        assert resp.status_code == 302
        assert resp.headers.get("Location") != "/users/login/"

    def test_login_wrong_password(self, api_session, base_url, registered_user, get_csrf_token):
        username, _ = registered_user
        token = get_csrf_token(api_session, f"{base_url}/users/login/")
        resp = api_session.post(
            f"{base_url}/users/login/",
            data={
                "username": username,
                "password": "wrong",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{base_url}/users/login/"},
            allow_redirects=False,
        )
        assert resp.status_code == 200

    def test_profile_requires_auth(self, api_session, base_url):
        resp = api_session.get(f"{base_url}/users/profile/", allow_redirects=False)
        assert resp.status_code == 302
        assert "/users/login/" in resp.headers.get("Location", "")

    def test_profile_accessible_after_login(self, auth_session, base_url):
        resp = auth_session.get(f"{base_url}/users/profile/")
        assert resp.status_code == 200