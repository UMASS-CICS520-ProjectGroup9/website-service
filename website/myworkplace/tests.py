import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestMyWorkplaceView:
    def test_myworkplace_page_renders_student(self, client, monkeypatch):
        """MyWorkplace page: renders for student with mocked API responses."""
        # Precondition: User is logged in as STUDENT, all API calls are mocked
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "student@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 42
        session.save()
        # Mock all requests.get calls
        class FakeResponse:
            def __init__(self, data):
                self._data = data
                self.status_code = 200
            def json(self):
                return self._data
        monkeypatch.setattr("myworkplace.views.requests.get", lambda url, headers=None: FakeResponse([]))
        # Testing
        response = client.get(reverse("myworkplace"))
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert response.context["authen"]["is_login"] is True, "Testing: User should be logged in."
        assert response.context["authen"]["role"] == "STUDENT", "Testing: User role should be STUDENT."
        # Postcondition: Context keys exist
        for key in ["events", "discussions", "comments", "courses", "professors", "professorsReviews", "coursesDiscussions", "coursesDiscussionComments"]:
            assert key in response.context, f"Postcondition: {key} should be in context."

    def test_myworkplace_page_renders_admin(self, client, monkeypatch):
        """MyWorkplace page: renders for admin with mocked API responses."""
        # Precondition: User is logged in as ADMIN, all API calls are mocked
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "admin@example.com"
        session["role"] = "ADMIN"
        session["user_id"] = 1
        session.save()
        # Mock all requests.get calls
        class FakeResponse:
            def __init__(self, data):
                self._data = data
                self.status_code = 200
            def json(self):
                return self._data
        monkeypatch.setattr("myworkplace.views.requests.get", lambda url, headers=None: FakeResponse([]))
        # Testing
        response = client.get(reverse("myworkplace"))
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert response.context["authen"]["is_login"] is True, "Testing: User should be logged in."
        assert response.context["authen"]["role"] == "ADMIN", "Testing: User role should be ADMIN."
        # Postcondition: Context keys exist
        for key in ["events", "discussions", "comments", "courses", "professors", "professorsReviews", "coursesDiscussions", "coursesDiscussionComments"]:
            assert key in response.context, f"Postcondition: {key} should be in context."

    def test_myworkplace_redirects_if_not_logged_in(self, client):
        """MyWorkplace page: redirects to login if not logged in."""
        # Precondition: No session token
        assert "access_token" not in client.session, "Precondition: No session token."
        # Testing
        response = client.get(reverse("myworkplace"))
        assert response.status_code == 302, "Testing: Should redirect."
        assert response.url == reverse("login"), "Testing: Should redirect to login."
