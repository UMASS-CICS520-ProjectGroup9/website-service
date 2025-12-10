import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestProfessorsViews:
    def test_add_review_success(self, client, monkeypatch):
            """Add review: valid POST creates review and redirects."""
            # Precondition: User is logged in, create_review_api is mocked to succeed
            monkeypatch.setattr("professors.views.get_professor_api", lambda pk, token=None: {"id": pk, "name": "Prof. X"})
            monkeypatch.setattr("professors.views.create_review_api", lambda pk, data, token=None: True)
            session = client.session
            session["access_token"] = "abc"
            session["email"] = "user@example.com"
            session["role"] = "STUDENT"
            session["user_id"] = 1
            session.save()
            assert session["access_token"] == "abc", "Precondition: Session token set."
            # Testing
            data = {"author": "user@example.com", "rating": "5", "comment": "Great!"}
            response = client.post(reverse("professor_detail", kwargs={"pk": 1}), data)
            assert response.status_code == 302, "Testing: Should redirect after review."
            assert response.url == reverse("professor_detail", kwargs={"pk": 1}), "Testing: Should redirect to detail."
            # Postcondition: Session unchanged
            assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."

    def test_add_review_invalid_input(self, client, monkeypatch):
            """Add review: invalid POST returns error (API returns False)."""
            monkeypatch.setattr("professors.views.get_professor_api", lambda pk, token=None: {"id": pk, "name": "Prof. X"})
            monkeypatch.setattr("professors.views.create_review_api", lambda pk, data, token=None: False)
            session = client.session
            session["access_token"] = "abc"
            session["email"] = "user@example.com"
            session["role"] = "STUDENT"
            session["user_id"] = 1
            session.save()
            assert session["access_token"] == "abc", "Precondition: Session token set."
            # Testing
            data = {"author": "", "rating": "", "comment": ""}
            response = client.post(reverse("professor_detail", kwargs={"pk": 1}), data)
            assert response.status_code == 200, "Testing: Should render with error."
            assert "error" in response.context or response.context.get("form_errors"), "Testing: Error should be in context."
            # Postcondition: Session unchanged
            assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."

    def test_add_review_api_error(self, client, monkeypatch):
            """Add review: API error returns error in context."""
            monkeypatch.setattr("professors.views.get_professor_api", lambda pk, token=None: {"id": pk, "name": "Prof. X"})
            def raise_api(*args, **kwargs):
                raise Exception("API error")
            monkeypatch.setattr("professors.views.create_review_api", raise_api)
            session = client.session
            session["access_token"] = "abc"
            session["email"] = "user@example.com"
            session["role"] = "STUDENT"
            session["user_id"] = 1
            session.save()
            assert session["access_token"] == "abc", "Precondition: Session token set."
            # Testing
            data = {"author": "user@example.com", "rating": "5", "comment": "Great!"}
            response = client.post(reverse("professor_detail", kwargs={"pk": 1}), data)
            assert response.status_code == 200, "Testing: Should render with error."
            assert "error" in response.context, "Testing: Error should be in context."
            # Postcondition: Session unchanged
            assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."
    def test_professors_page_renders(self, client, monkeypatch):
        """Professors page: renders with mocked API and auth context."""
        # Precondition: User is logged in, API is mocked
        fake_professors = [
            {"id": 1, "name": "Prof. X", "department": "CS"},
            {"id": 2, "name": "Prof. Y", "department": "Math"},
        ]
        monkeypatch.setattr("professors.views.get_professors_api", lambda query, token=None: fake_professors)
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        assert session["access_token"] == "abc", "Precondition: Session token set."
        # Testing
        response = client.get(reverse("professors"))
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert response.context["professors"] == fake_professors, "Testing: Professors context should match fake data."
        assert response.context["authen"]["is_login"] is True, "Testing: User should be logged in."
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."

    def test_professor_search(self, client, monkeypatch):
        """Professors search: returns filtered professors."""
        # Precondition: User is logged in, API is mocked
        fake_professors = [
            {"id": 1, "name": "Prof. X", "department": "CS"}
        ]
        monkeypatch.setattr("professors.views.get_professors_api", lambda query, token=None: fake_professors)
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        assert session["access_token"] == "abc", "Precondition: Session token set."
        # Testing
        response = client.get(reverse("professors"), {"query": "CS"})
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert response.context["professors"] == fake_professors, "Testing: Professors context should match filtered data."
        assert response.context["query"] == "CS", "Testing: Query context should match input."
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."

    def test_add_professor_permission(self, client):
        """Add professor: redirects if not staff/admin."""
        # Precondition: User is STUDENT
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STUDENT"
        session.save()
        assert session["role"] == "STUDENT", "Precondition: User role is STUDENT."
        # Testing
        response = client.get(reverse("add_professor"))
        assert response.status_code == 302, "Testing: Should redirect."
        assert response.url == reverse("professors"), "Testing: Should redirect to professors."
        # Postcondition: No session or data changed
        assert client.session["role"] == "STUDENT", "Postcondition: User role unchanged."

    def test_delete_professor_permission(self, client):
        """Delete professor: redirects if not staff/admin."""
        # Precondition: User is STUDENT
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STUDENT"
        session.save()
        assert session["role"] == "STUDENT", "Precondition: User role is STUDENT."
        # Testing
        response = client.post(reverse("delete_professor", kwargs={"pk": 1}))
        assert response.status_code == 302, "Testing: Should redirect."
        assert response.url == reverse("professors"), "Testing: Should redirect to professors."
        # Postcondition: No session or data changed
        assert client.session["role"] == "STUDENT", "Postcondition: User role unchanged."

    def test_add_professor_success(self, client, monkeypatch):
        """Add professor: staff/admin can add (POST)."""
        # Precondition: User is STAFF, create_professor_api is mocked
        monkeypatch.setattr("professors.views.create_professor_api", lambda data, token=None: True)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STAFF"
        session.save()
        data = {"name": "Prof. Z", "department": "Physics", "email": "z@u.edu", "office": "Rm 1"}
        assert session["role"] == "STAFF", "Precondition: User role is STAFF."
        # Testing
        response = client.post(reverse("add_professor"), data)
        assert response.status_code == 302, "Testing: Should redirect."
        assert response.url == reverse("professors"), "Testing: Should redirect to professors."
        # Postcondition: Session unchanged
        assert client.session["role"] == "STAFF", "Postcondition: User role unchanged."

    def test_delete_professor_success(self, client, monkeypatch):
        """Delete professor: staff/admin can delete (POST)."""
        # Precondition: User is ADMIN, delete_professor_api is mocked
        monkeypatch.setattr("professors.views.delete_professor_api", lambda pk, token=None: True)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "ADMIN"
        session.save()
        assert session["role"] == "ADMIN", "Precondition: User role is ADMIN."
        # Testing
        response = client.post(reverse("delete_professor", kwargs={"pk": 1}))
        assert response.status_code == 302, "Testing: Should redirect."
        assert response.url == reverse("professors"), "Testing: Should redirect to professors."
        # Postcondition: Session unchanged
        assert client.session["role"] == "ADMIN", "Postcondition: User role unchanged."

    def test_add_professor_invalid_input(self, client, monkeypatch):
        """Add professor: invalid input returns error (POST)."""
        # Precondition: User is STAFF, create_professor_api is mocked to return False
        monkeypatch.setattr("professors.views.create_professor_api", lambda data, token=None: False)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STAFF"
        session.save()
        data = {"name": "", "department": "", "email": "", "office": ""}
        assert session["role"] == "STAFF", "Precondition: User role is STAFF."
        # Testing
        response = client.post(reverse("add_professor"), data)
        assert response.status_code == 200, "Testing: Should render with error."
        assert "error" in response.context, "Testing: Error should be in context."
        # Postcondition: Session unchanged
        assert client.session["role"] == "STAFF", "Postcondition: User role unchanged."

    def test_delete_professor_api_failure(self, client, monkeypatch):
        """Delete professor: API failure returns error (POST)."""
        # Precondition: User is ADMIN, delete_professor_api is mocked to return False
        monkeypatch.setattr("professors.views.delete_professor_api", lambda pk, token=None: False)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "ADMIN"
        session.save()
        assert session["role"] == "ADMIN", "Precondition: User role is ADMIN."
        # Testing
        response = client.post(reverse("delete_professor", kwargs={"pk": 1}))
        assert response.status_code == 200, "Testing: Should render with error."
        assert "error" in response.context, "Testing: Error should be in context."
        # Postcondition: Session unchanged
        assert client.session["role"] == "ADMIN", "Postcondition: User role unchanged."

    def test_professors_api_error(self, client, monkeypatch):
        """Professors page: API error returns error in context."""
        # Precondition: User is logged in, API raises Exception
        def raise_api(*args, **kwargs):
            raise Exception("API error")
        monkeypatch.setattr("professors.views.get_professors_api", raise_api)
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        assert session["access_token"] == "abc", "Precondition: Session token set."
        # Testing
        response = client.get(reverse("professors"))
        assert response.status_code == 200, "Testing: Should render with error."
        assert "error" in response.context, "Testing: Error should be in context."
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."
