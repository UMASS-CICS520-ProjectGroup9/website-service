import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestCoursesViews:
    def test_add_course_invalid_input(self, client, monkeypatch):
        """Add course: invalid input returns error (POST)."""
        # Precondition: User is STAFF, create_course_api is mocked to return False
        monkeypatch.setattr("courses.views.create_course_api", lambda data, token=None: False)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STAFF"
        session.save()
        data = {"courseSubject": "", "courseID": "", "title": "", "instructor": ""}  # Invalid
        # Testing
        response = client.post(reverse("add_course"), data)
        # Should render page with error (not redirect)
        assert response.status_code == 200
        assert "error" in response.context
        # Postcondition: Session unchanged
        assert client.session["role"] == "STAFF"

    def test_delete_course_api_failure(self, client, monkeypatch):
        """Delete course: API failure returns error (POST)."""
        # Precondition: User is ADMIN, delete_course_api is mocked to return False
        monkeypatch.setattr("courses.views.delete_course_api", lambda courseSubject, courseID, token=None: False)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "ADMIN"
        session.save()
        # Testing
        response = client.post(reverse("delete_course", kwargs={"courseSubject": "CS", "courseID": 101}))
        # Should render page with error (not redirect)
        assert response.status_code == 200
        assert "error" in response.context
        # Postcondition: Session unchanged
        assert client.session["role"] == "ADMIN"

    def test_course_search_api_error(self, client, monkeypatch):
        """Course search: API error returns error in context."""
        # Precondition: User is logged in, courseAPI raises Exception
        def raise_api(*args, **kwargs):
            raise Exception("API error")
        monkeypatch.setattr("courses.views.courseAPI", raise_api)
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        # Testing
        response = client.get(reverse("course_search"), {"courseSubject": "CS"})
        assert response.status_code == 200
        assert "error" in response.context
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc"
    def test_add_course_success(self, client, monkeypatch):
        """Add course: staff/admin can add a course (POST)."""
        # Precondition: User is STAFF, create_course_api is mocked
        monkeypatch.setattr("courses.views.create_course_api", lambda data, token=None: True)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STAFF"
        session.save()
        data = {"courseSubject": "CS", "courseID": 102, "title": "Data Structures", "instructor": "Prof. C"}
        # Testing
        response = client.post(reverse("add_course"), data)
        # Should redirect to courses on success
        assert response.status_code == 302
        assert response.url == reverse("courses")
        # Postcondition: Session unchanged
        assert client.session["role"] == "STAFF"

    def test_delete_course_success(self, client, monkeypatch):
        """Delete course: staff/admin can delete a course (POST)."""
        # Precondition: User is ADMIN, delete_course_api is mocked
        monkeypatch.setattr("courses.views.delete_course_api", lambda courseSubject, courseID, token=None: True)
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "ADMIN"
        session.save()
        # Testing
        response = client.post(reverse("delete_course", kwargs={"courseSubject": "CS", "courseID": 101}))
        # Should redirect to courses on success
        assert response.status_code == 302
        assert response.url == reverse("courses")
        # Postcondition: Session unchanged
        assert client.session["role"] == "ADMIN"

    def test_course_search_no_results(self, client, monkeypatch):
        """Course search: returns empty list if no results."""
        # Precondition: User is logged in, courseAPI is mocked to return []
        monkeypatch.setattr("courses.views.courseAPI", lambda courseSubject, courseID, title, instructor, token=None: [])
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        # Testing
        response = client.get(reverse("course_search"), {"courseSubject": "ZZZ"})
        assert response.status_code == 200
        assert response.context["searched"] is True
        assert response.context["courseAPI"] == []
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc"
    def test_courses_page_renders(self, client, monkeypatch):
        """Courses page: renders with mocked courseAPI and auth context."""
        # Precondition: User is logged in, courseAPI is mocked
        fake_courses = [
            {"courseSubject": "CS", "courseID": 101, "title": "Intro CS", "instructor": "Prof. A"},
            {"courseSubject": "MATH", "courseID": 201, "title": "Calculus", "instructor": "Prof. B"},
        ]
        monkeypatch.setattr("courses.views.courseAPI", lambda token=None: fake_courses)
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        assert session["access_token"] == "abc", "Precondition: Session token set."
        # Testing
        response = client.get(reverse("courses"))
        assert response.status_code == 200, "Testing: Should return 200 OK."
        assert "courseAPI" in response.context, "Testing: courseAPI should be in context."
        assert response.context["authen"]["is_login"] is True, "Testing: User should be logged in."
        assert response.context["courseAPI"] == fake_courses, "Testing: courseAPI context should match fake data."
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc", "Postcondition: Session token unchanged."

    def test_course_search(self, client, monkeypatch):
        """Course search: returns filtered courses."""
        # Precondition: User is logged in, courseAPI is mocked
        fake_courses = [
            {"courseSubject": "CS", "courseID": 101, "title": "Intro CS", "instructor": "Prof. A"}
        ]
        monkeypatch.setattr("courses.views.courseAPI", lambda courseSubject, courseID, title, instructor, token=None: fake_courses)
        session = client.session
        session["access_token"] = "abc"
        session["email"] = "user@example.com"
        session["role"] = "STUDENT"
        session["user_id"] = 1
        session.save()
        # Testing
        response = client.get(reverse("course_search"), {"courseSubject": "CS"})
        assert response.status_code == 200
        assert response.context["searched"] is True
        assert response.context["courseAPI"] == fake_courses
        # Postcondition: No session or data changed
        assert client.session["access_token"] == "abc"

    def test_add_course_permission(self, client):
        """Add course: redirects if not staff/admin."""
        # Precondition: User is STUDENT
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STUDENT"
        session.save()
        # Testing
        response = client.get(reverse("add_course"))
        assert response.status_code == 302
        assert response.url == reverse("courses")
        # Postcondition: No session or data changed
        assert client.session["role"] == "STUDENT"

    def test_delete_course_permission(self, client):
        """Delete course: redirects if not staff/admin."""
        # Precondition: User is STUDENT
        session = client.session
        session["access_token"] = "abc"
        session["role"] = "STUDENT"
        session.save()
        # Testing
        response = client.post(reverse("delete_course", kwargs={"courseSubject": "CS", "courseID": 101}))
        assert response.status_code == 302
        assert response.url == reverse("courses")
        # Postcondition: No session or data changed
        assert client.session["role"] == "STUDENT"
