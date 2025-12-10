import math
from unittest.mock import patch
import pytest
from django.urls import reverse
from django.http import HttpResponse


pytestmark = pytest.mark.django_db


class TestWebViews:
    """
    Robust tests for all main web views, following best practices:
    - Explicit precondition, testing, and postcondition assertions
    - Clear docstrings for each test
    - Monkeypatching for external dependencies
    - Edge case and error handling
    """

    def test_index_renders_posts_and_auth(self, client):
        """Index page: not logged in, posts and auth context present."""
        # Precondition: No session token
        assert "access_token" not in client.session, "Precondition: No session token should exist."
        # Testing
        response = client.get(reverse("index"))
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert response.context["authen"]["is_login"] is False, "Testing: Should not be logged in."
        # Postcondition: posts context key exists
        assert "posts" in response.context, "Postcondition: Posts context key should exist."

    # ...existing tests for index, register, login, events, discussions, etc...



    def test_myworkplace_page_renders(self, client, monkeypatch):
        """MyWorkplace page: renders with mocked API responses and session."""
        # Precondition: User is logged in, requests.get is mocked
        class FakeResponse:
            def __init__(self, data):
                self._data = data
                self.status_code = 200
            def json(self):
                return self._data
        monkeypatch.setattr("requests.get", lambda *args, **kwargs: FakeResponse([]))
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        assert session["access_token"] == "abc", "Precondition: Session token set."
        # Testing
        response = client.get(reverse("myworkplace"))
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert "authen" in response.context, "Testing: authen should be in context."
        assert response.context["authen"]["is_login"] is True, "Testing: User should be logged in."
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."

    def test_index_flags_logged_in(self, client):
        """Index page: logged in, is_login True."""
        # Precondition: Set session token
        session = client.session
        session["access_token"] = "abc"
        session.save()
        # Testing
        response = client.get(reverse("index"))
        assert response.context["authen"]["is_login"] is True, "Testing: Should be logged in."
        # Postcondition: session unchanged
        assert client.session["access_token"] == "abc", "Postcondition: Session token should remain."

    def test_register_view_ok(self, client):
        """Register page: renders with no error when not logged in."""
        # Precondition: No user is logged in
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        # Testing
        response = client.get(reverse("register"))
        assert response.status_code == 200
        # Postcondition: No error in context
        assert "error" not in getattr(response, "context", {}), "Postcondition: No error should be present."

    def test_register_create_password_mismatch(self, client):
        """Register: password mismatch returns error."""
        # Precondition: No user is logged in and passwords do not match
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"username": "u", "email": "e@example.com", "password": "a", "confirm_password": "b"}
        assert data["password"] != data["confirm_password"], "Precondition: Passwords must not match."
        # Testing
        response = client.post(
            reverse("registerCreate"),
            data,
        )
        assert response.status_code == 200
        # Postcondition: Error message for password mismatch
        assert response.context["error"] == "Confirm Password must be same!"

    def test_register_create_success_redirects(self, client, monkeypatch):
        """Register: successful registration redirects to login."""
        class FakeResponse:
            status_code = 201

            @staticmethod
            def json():
                return {"ok": True}

        monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

        # Precondition: No user is logged in and passwords match
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"username": "u", "email": "e@example.com", "password": "pw", "confirm_password": "pw"}
        assert data["password"] == data["confirm_password"], "Precondition: Passwords must match."
        response = client.post(
            reverse("registerCreate"),
            data,
        )
        # Testing
        assert response.status_code == 302
        assert response.url == reverse("login")
        # Postcondition: Redirects to login
        assert response.url == reverse("login")

    def test_register_create_handles_api_error(self, client, monkeypatch):
        """Register: API error returns error context."""
        class FakeResponse:
            status_code = 400

            @staticmethod
            def json():
                return {"detail": "bad"}

        monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

        # Precondition: No user is logged in and passwords match
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"username": "u", "email": "e@example.com", "password": "pw", "confirm_password": "pw"}
        assert data["password"] == data["confirm_password"], "Precondition: Passwords must match."
        response = client.post(
            reverse("registerCreate"),
            data,
        )
        # Testing
        assert response.status_code == 200
        # Postcondition: Error context from API
        assert response.context["error"] == {"detail": "bad"}

    def test_login_view_ok(self, client):
        """Login page: renders with no error when not logged in."""
        # Precondition: No user is logged in
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        response = client.get(reverse("login"))
        # Testing
        assert response.status_code == 200
        # Postcondition: No error in context
        assert "error" not in getattr(response, "context", {}), "Postcondition: No error should be present."

    def test_login_process_success_sets_session(self, client, monkeypatch):
        """Login: valid credentials set session and redirect."""
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

        # Precondition: No user is logged in
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"Email": "user@example.com", "password": "pw"}
        response = client.post(reverse("loginProcess"), data)
        # Testing
        assert response.status_code == 302
        assert response.url == reverse("index")
        # Postcondition: Session tokens set
        session = client.session
        assert session["access_token"] == "tok-access"
        assert session["refresh_token"] == "tok-refresh"
        assert session["email"] == "user@example.com"
        assert session["user_id"] == 99
        assert session["role"] == "ADMIN"

    def test_login_process_invalid_credentials(self, client, monkeypatch):
        """Login: invalid credentials returns error."""
        class FakeResponse:
            status_code = 400

            @staticmethod
            def json():
                return {"detail": "nope"}

        monkeypatch.setattr("base.views.requests.post", lambda *args, **kwargs: FakeResponse())

        # Precondition: No user is logged in, invalid credentials
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"Email": "user@example.com", "password": "bad"}
        response = client.post(reverse("loginProcess"), data)
        # Testing
        assert response.status_code == 200
        # Postcondition: Error message for invalid credentials
        assert response.context["error"] == "Invalid login credentials"

    def test_login_process_rejects_get(self, client):
        """Login: GET method not allowed."""
        # Precondition: No user is logged in
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        response = client.get(reverse("loginProcess"))
        # Testing
        assert response.status_code == 405

    def test_logout_clears_session(self, client):
        """Logout: clears session and redirects to login."""
        # Precondition: Set session token
        session = client.session
        session["access_token"] = "abc"
        session.save()
        # Testing
        response = client.get(reverse("logout"))
        assert response.status_code == 302
        assert response.url == reverse("login")
        # Postcondition: Session cleared
        assert "access_token" not in client.session

    def test_events_page_pagination(self, client, monkeypatch):
        """Events page: paginates events and renders total pages."""
        # Precondition: Mock eventsSortedByStartDate_model to return 7 events
        fake_events = [
            {"created_at": "2024-01-01T00:00:00Z", "event_start_date": "2024-01-01T10:00:00Z", "event_end_date": "2024-01-01T12:00:00Z"} for _ in range(7)
        ]
        monkeypatch.setattr("base.views.eventsSortedByStartDate_model", lambda: fake_events)
        # Testing
        response = client.get(reverse("events_page", kwargs={"page": 1}))
        assert response.status_code == 200
        # Postcondition: Pagination context in HTML
        total_pages = math.ceil(len(fake_events) / 3)
        assert str(total_pages) in response.content.decode()

    def test_discussions_page_pagination(self, client, monkeypatch):
        """Discussions page: paginates discussions and renders total pages."""
        # Precondition: Mock discussionAPI to return 12 discussions with id
        fake_discussions = [
            {"id": i, "updated_at": f"2024-01-{i:02d}T10:00:00Z"} for i in range(12)
        ]
        monkeypatch.setattr("base.views.discussionAPI", lambda token=None: fake_discussions)
        session = client.session
        session["access_token"] = "abc"
        session.save()
        # Testing
        response = client.get(reverse("discussions_page", kwargs={"page": 2}))
        assert response.status_code == 200
        # Postcondition: Pagination context in HTML
        total_pages = math.ceil(len(fake_discussions) / 5)
        assert str(total_pages) in response.content.decode()

    @pytest.mark.parametrize("view,page", [("events_page", 1), ("discussions_page", 1)])
    def test_page_handles_external_exception(self, client, monkeypatch, view, page):
        """Events/Discussions page: handles external API failure gracefully."""
        # Precondition: Simulate external API failure
        if view == "events_page":
            monkeypatch.setattr("base.views.eventsSortedByStartDate_model", lambda: (_ for _ in ()).throw(Exception("fail")))
        else:
            monkeypatch.setattr("base.views.discussionAPI", lambda token=None: (_ for _ in ()).throw(Exception("fail")))
        session = client.session
        session["access_token"] = "abc"
        session.save()
        # Testing
        response = client.get(reverse(view, kwargs={"page": page}))
        assert response.status_code == 200, "Testing: Should return 200 OK even on error."
        # Postcondition: Should still render HTML fragment
        assert "<html" not in response.content.decode().lower(), "Postcondition: Should render HTML fragment, not full page."

    def test_register_create_empty_fields(self, client):
        """Register: empty fields returns error."""
        # Precondition: No user is logged in
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"username": "", "email": "", "password": "", "confirm_password": ""}
        # Testing
        response = client.post(reverse("registerCreate"), data)
        assert response.status_code == 200, "Testing: Should return 200 OK."
        # Postcondition: Error message for empty fields (dict of errors)
        assert isinstance(response.context["error"], dict), "Postcondition: Should return a dict of field errors."

    def test_login_process_empty_fields(self, client):
        """Login: empty fields returns error."""
        # Precondition: No user is logged in
        assert "access_token" not in client.session, "Precondition: No user should be logged in."
        data = {"Email": "", "password": ""}
        response = client.post(reverse("loginProcess"), data)
        # Testing
        assert response.status_code == 200, "Testing: Should return 200 OK."
        # Postcondition: Error message for empty fields or invalid credentials
        assert response.context["error"] in ("Invalid login credentials", "All fields are required!"), "Postcondition: Should return a relevant error message."
