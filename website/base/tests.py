import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_index_renders_posts_and_auth(client):
    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert response.context["authen"]["is_login"] is False
    assert response.context["posts"]  # uses base.models.posts


def test_index_flags_logged_in(client):
    session = client.session
    session["access_token"] = "abc"
    session.save()

    response = client.get(reverse("index"))

    assert response.context["authen"]["is_login"] is True


def test_register_view_ok(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200


def test_register_create_password_mismatch(client):
    response = client.post(
        reverse("registerCreate"),
        {"username": "u", "email": "e@example.com", "password": "a", "confirm_password": "b"},
    )

    assert response.status_code == 200
    assert response.context["error"] == "Confirm Password must be same!"


def test_register_create_success_redirects(client, monkeypatch):
    class FakeResponse:
        status_code = 201

        @staticmethod
        def json():
            return {"ok": True}

    monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

    response = client.post(
        reverse("registerCreate"),
        {"username": "u", "email": "e@example.com", "password": "pw", "confirm_password": "pw"},
    )

    assert response.status_code == 302
    assert response.url == reverse("login")


def test_register_create_handles_api_error(client, monkeypatch):
    class FakeResponse:
        status_code = 400

        @staticmethod
        def json():
            return {"detail": "bad"}

    monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

    response = client.post(
        reverse("registerCreate"),
        {"username": "u", "email": "e@example.com", "password": "pw", "confirm_password": "pw"},
    )

    assert response.status_code == 200
    assert response.context["error"] == {"detail": "bad"}


def test_login_view_ok(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200


def test_login_process_success_sets_session(client, monkeypatch):
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "access": "tok-access",
                "refresh": "tok-refresh",
                "email": "user@example.com",
                "user_id": 99,
                "role": "ADMIN",
            }

    monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

    response = client.post(reverse("loginProcess"), {"Email": "user@example.com", "password": "pw"})

    assert response.status_code == 302
    assert response.url == reverse("index")
    session = client.session
    assert session["access_token"] == "tok-access"
    assert session["refresh_token"] == "tok-refresh"
    assert session["email"] == "user@example.com"
    assert session["user_id"] == 99
    assert session["role"] == "ADMIN"


def test_login_process_invalid_credentials(client, monkeypatch):
    class FakeResponse:
        status_code = 400

        @staticmethod
        def json():
            return {"detail": "nope"}

    monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

    response = client.post(reverse("loginProcess"), {"Email": "user@example.com", "password": "bad"})

    assert response.status_code == 200
    assert response.context["error"] == "Invalid login credentials"


def test_login_process_rejects_get(client):
    response = client.get(reverse("loginProcess"))
    assert response.status_code == 405


def test_logout_clears_session(client):
    session = client.session
    session["access_token"] = "abc"
    session.save()

    response = client.get(reverse("logout"))

    assert response.status_code == 302
    assert response.url == reverse("login")
    assert "access_token" not in client.session
