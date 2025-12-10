import pytest
import datetime
from django.urls import reverse
from myworkplace.views import format_event_dates
from django.conf import settings

pytestmark = pytest.mark.django_db


# ============================================================
# Smart Mock Response
# ============================================================
class SmartMockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


# ============================================================
# Utility: build session
# ============================================================
def setup_session(client, role="STUDENT", user_id=10):
    s = client.session
    s["access_token"] = "mock_token"
    s["email"] = f"{role.lower()}@example.com"
    s["role"] = role
    s["user_id"] = user_id
    s.save()


# ============================================================
# UNIVERSAL MOCK (full coverage)
# ============================================================
def universal_mock(url, *args, **kwargs):
    # ---------------- Discussions List (main site discussions) ----------------
    if "discussions" in url and "course" not in url:
        return SmartMockResponse([
            {
                "id": 1,
                "pk": 1,
                "title": "General Discussion",
                "body": "Testing discussion",
                "author": "UserA",
                "creator_id": 10,
                "created_at": "2025-01-01T10:00:00Z",
                "comments": [
                    {
                        "creator_id": 10,
                        "author": "UserA",
                        "body": "My comment",
                        "created_at": "2025-01-02T08:00:00Z",
                        "discussion": 1
                    },
                    {
                        "creator_id": 999,
                        "author": "Other",
                        "body": "Not mine",
                        "created_at": "2025-01-02T09:00:00Z",
                        "discussion": 1
                    }
                ]
            },
            {
                "id": 2,
                "pk": 2,
                "title": "Other Discussion",
                "body": "Other",
                "author": "UserX",
                "creator_id": 999,
                "created_at": "2025-01-03T10:00:00Z",
                "comments": []
            }
        ])

    # ---------------- Professors API ----------------
    if "professors" in url:
        return SmartMockResponse([
            {
                "id": 50,
                "name": "Dr. Smith",
                "reviews": [
                    {
                        "creator_id": 999,
                        "created_at": "2025-01-01T10:00:00Z",
                        "content": "Good prof"
                    }
                ]
            }
        ])

    # ---------------- Course List ----------------
    if "courses" in url and "discussion" not in url:
        return SmartMockResponse([
            {"id": 101, "name": "Software Engineering", "course_code": "CS520"}
        ])

    # ---------------- Course Discussions (Admin path) ----------------
    if "course" in url and "discussion" in url:
        return SmartMockResponse([
            {
                "id": 20,
                "pk": 20,
                "course_subject": "CS",
                "course_id": "520",
                "creator_id": 1,
                "title": "Course Discussion",
                "created_at": "BAD_DATE",    # triggers parse exception
                "comments": [
                    {
                        "creator_id": 999,
                        "created_at": "WRONG",  # triggers parse exception
                        "discussion": 20
                    }
                ]
            }
        ])

    # ---------------- Events (Admin mode) ----------------
    if "events" in url:
        return SmartMockResponse([
            # Valid event (normal path coverage)
            {
                "id": 1,
                "eventID": 1,
                "event_start_date": "2025-01-01T10:00:00Z",
                "event_end_date": "2025-01-01T12:00:00Z"
            },
            # Invalid event
            {
                "id": 2,
                "eventID": 2,
                "event_start_date": "NOT_A_DATE",   
                "event_end_date": "INVALID_DATE"  
            }
        ])



# ============================================================
# Test 1: Not logged in → redirect
# ============================================================
def test_redirect_not_logged_in(client):
    client.session.flush()
    res = client.get(reverse("myworkplace"))
    assert res.status_code == 302
    assert res.url == reverse("login")


# ============================================================
# Test 2: Student view
# ============================================================
def test_student_view(client, monkeypatch):
    setup_session(client, role="STUDENT", user_id=10)
    monkeypatch.setattr("myworkplace.views.requests.get", universal_mock)

    res = client.get(reverse("myworkplace"))
    assert res.status_code == 200

    discussions = res.context["discussions"]
    assert len(discussions) == 1  # only own discussion

    comments = res.context["comments"]
    assert len(comments) == 1     # only own comment


# ============================================================
# Test 3: Admin view (main branch)
# ============================================================
def test_admin_view(client, monkeypatch):
    setup_session(client, role="ADMIN", user_id=1)
    monkeypatch.setattr("myworkplace.views.requests.get", universal_mock)

    res = client.get(reverse("myworkplace"))
    assert res.status_code == 200

    # Admin sees all discussions
    assert len(res.context["discussions"]) == 2

    # Admin sees course discussions and comments
    assert len(res.context["coursesDiscussions"]) == 1
    assert len(res.context["coursesDiscussionComments"]) == 1


# ============================================================
# Test 4: Cover try/except block in course discussions fetch
# ============================================================
def test_course_discussion_api_exception(client, monkeypatch):
    setup_session(client, role="ADMIN", user_id=1)

    # First call (for normal discussions) → safe universal_mock
    # Second call (course discussion) → raise Exception to hit missing lines 161-162
    def mock_exception(url, *args, **kwargs):
        if "course" in url and "discussion" in url:
            raise Exception("API failed")  # ❗ triggers except block
        return universal_mock(url, *args, **kwargs)

    monkeypatch.setattr("myworkplace.views.requests.get", mock_exception)

    res = client.get(reverse("myworkplace"))
    assert res.status_code == 200
    assert res.context["coursesDiscussions"] == []


# ============================================================
# Test 5: format_event_dates success
# ============================================================
def test_format_event_dates_success():
    data = [{"event_start_date": "2025-01-01T10:00:00Z"}]
    out = format_event_dates(data)
    assert isinstance(out[0]["event_start_date"], datetime.datetime)


# ============================================================
# Test 6: format_event_dates early-return (non-list)
# ============================================================
def test_format_event_dates_non_list():
    out = format_event_dates({"not": "list"})  # ❗ triggers line 106
    assert isinstance(out, dict)


# ============================================================
# Test 7: Unknown role → page still loads
# ============================================================
def test_unknown_role(client, monkeypatch):
    setup_session(client, role="WEIRD", user_id=10)
    monkeypatch.setattr("myworkplace.views.requests.get", universal_mock)
    res = client.get(reverse("myworkplace"))
    assert res.status_code == 200

# ============================================================
# Test 8: Event date parsing failure → triggers except blocks
# ------------------------------------------------------------
def test_event_date_parsing_failure(client, monkeypatch):
    # Admin mode ensures /events endpoint is used
    setup_session(client, role="ADMIN", user_id=1)

    # universal_mock already includes invalid event data
    monkeypatch.setattr("myworkplace.views.requests.get", universal_mock)

    response = client.get(reverse("myworkplace"))
    assert response.status_code == 200

    events = response.context["events"]
    
    # Our universal_mock returns TWO events (valid + invalid)
    assert len(events) == 2

    # Check the invalid one — this triggers exception handling in the view
    invalid_event = events[1]
    assert invalid_event["event_start_date"] == "NOT_A_DATE"
    assert invalid_event["event_end_date"] == "INVALID_DATE"
