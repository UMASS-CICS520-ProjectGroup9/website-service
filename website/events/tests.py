import pytest
from django.urls import reverse
import requests


pytestmark = pytest.mark.django_db


@pytest.fixture
def auth_client(client):
    session = client.session
    session["access_token"] = "token-123"
    session["user_id"] = 42
    session["email"] = "user@example.com"
    session["role"] = "STUDENT"
    session.save()
    return client


@pytest.fixture
def sample_event():
    return {
        "eventID": 1,
        "title": "Sample",
        "description": "Details",
        "creator": "Owner",
    }


def test_events_lists_events(client, monkeypatch, sample_event):
    calls = {}

    def fake_event_api():
        calls["called"] = True
        return [sample_event]

    monkeypatch.setattr("events.views.eventAPI", fake_event_api)

    response = client.get(reverse("events"))

    assert response.status_code == 200
    assert response.context["eventAPI"] == [sample_event]
    assert calls["called"] is True


def test_get_event_by_id_renders_detail(client, monkeypatch, sample_event):
    monkeypatch.setattr("events.views.getEventByID_model", lambda event_id: {**sample_event, "eventID": event_id})

    response = client.get(reverse("getEventByID", args=[5]))

    assert response.status_code == 200
    assert response.context["event"]["eventID"] == 5


def test_event_form_requires_login(client):
    response = client.get(reverse("eventForm"))

    assert response.status_code == 302
    assert response.url == reverse("login")


def test_event_form_returns_template_for_authenticated_user(auth_client):
    response = auth_client.get(reverse("eventForm"))

    assert response.status_code == 200
    assert response.context["creator_id"] == 42


def test_event_form_creation_redirects_on_get(client):
    response = client.get(reverse("eventFormCreation"))

    assert response.status_code == 302
    assert response.url == reverse("eventForm")


def test_event_form_creation_requires_login(client):
    response = client.post(reverse("eventFormCreation"), {"title": "New"})

    assert response.status_code == 302
    assert response.url == reverse("login")


def test_event_form_creation_submits_payload(auth_client, monkeypatch):
    captured = {}

    def fake_create_event(data, headers):
        captured["data"] = data
        captured["headers"] = headers
        return {"eventID": 123}

    monkeypatch.setattr("events.views.createEvent_model", fake_create_event)

    payload = {
        "title": "New Event",
        "description": "Nice one",
        "creator": "Tester",
        "creator_id": "77",
        "eventType": "ONLINE",
        "location": "Zoom",
        "capacity": "50",
        "link": "",
        "zoom_link": "https://zoom.example",
        "hosted_by": "CS Dept",
        "event_start_date": "2024-01-02T03:04",
        "event_end_date": "2024-01-03T03:04",
        "registered_students": "1, 2, abc",
    }

    response = auth_client.post(reverse("eventFormCreation"), payload)

    assert response.status_code == 302
    assert response.url == reverse("getEventByID", args=[123])
    assert captured["data"]["capacity"] == 50
    assert captured["data"]["registered_students"] == [1, 2, "abc"]
    assert captured["headers"]["Authorization"] == "Bearer token-123"


def test_event_form_creation_returns_error_without_event_id(auth_client, monkeypatch):
    monkeypatch.setattr("events.views.createEvent_model", lambda *_args, **_kwargs: {})

    response = auth_client.post(reverse("eventFormCreation"), {"title": "Missing id"})

    assert response.status_code == 400
    assert "error" in response.json()


def test_event_form_creation_handles_request_exception(auth_client, monkeypatch):
    def raise_error(*_args, **_kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr("events.views.createEvent_model", raise_error)

    response = auth_client.post(reverse("eventFormCreation"), {"title": "Err"})

    assert response.status_code == 400
    assert response.json()["error"].startswith("API Error: boom")


def test_remove_event_get_shows_confirmation(client, monkeypatch, sample_event):
    monkeypatch.setattr("events.views.getEventByID_model", lambda _id: sample_event)

    response = client.get(reverse("removeEvent", args=[sample_event["eventID"]]))

    assert response.status_code == 200
    assert response.context["event"] == sample_event


def test_remove_event_post_calls_api(auth_client, monkeypatch):
    called = {}

    def fake_remove(event_id, headers):
        called["event_id"] = event_id
        called["headers"] = headers
        return {"status": "success"}

    monkeypatch.setattr("events.views.removeEvent_model", fake_remove)

    response = auth_client.post(reverse("removeEvent", args=[9]))

    assert response.status_code == 302
    assert response.url == "/events/"
    assert called["event_id"] == 9
    assert called["headers"]["Authorization"] == "Bearer token-123"


def test_event_form_update_requires_login(client):
    response = client.get(reverse("eventFormUpdate", args=[1]))

    assert response.status_code == 302
    assert response.url == reverse("login")


def test_event_form_update_get_formats_event(auth_client, monkeypatch):
    raw_event = {
        "eventID": 5,
        "event_start_date": "2024-01-02T03:04:00Z",
        "event_end_date": "2024-01-04 05:06:00",
        "registered_students": [1, "abc"],
    }
    monkeypatch.setattr("events.views.getEventByID_model", lambda _id: raw_event.copy())

    response = auth_client.get(reverse("eventFormUpdate", args=[5]))

    assert response.status_code == 200
    formatted = response.context["event"]
    assert formatted["event_start_date"] == "2024-01-02T03:04"
    assert formatted["event_end_date"] == "2024-01-04T05:06"
    assert formatted["registered_students"] == "1, abc"


def test_event_form_update_post_calls_api(auth_client, monkeypatch):
    called = {}
    monkeypatch.setattr("events.views.getEventByID_model", lambda _id: {})

    def fake_update(event_id, data, headers):
        called["event_id"] = event_id
        called["data"] = data
        called["headers"] = headers
        return {"status": "success"}

    monkeypatch.setattr("events.views.updateEvent_model", fake_update)

    payload = {
        "title": "Updated",
        "description": "New",
        "creator": "Owner",
        "creator_id": "11",
        "eventType": "OFFLINE",
        "location": "Campus",
        "capacity": "15",
        "link": "",
        "zoom_link": "",
        "hosted_by": "Dept",
        "event_start_date": "2024-02-03T04:05",
        "event_end_date": "2024-02-04T05:06",
        "registered_students": "1, 7, bob",
    }

    response = auth_client.post(reverse("eventFormUpdate", args=[3]), payload)

    assert response.status_code == 302
    assert response.url == reverse("getEventByID", args=[3])
    assert called["event_id"] == 3
    assert called["data"]["capacity"] == 15
    assert called["data"]["registered_students"] == [1, 7, "bob"]
    assert called["data"]["creator_id"] == 11
    assert called["headers"]["Authorization"] == "Bearer token-123"


def test_event_form_update_handles_request_exception(auth_client, monkeypatch):
    def fake_update(*_args, **_kwargs):
        raise requests.RequestException("fail")

    monkeypatch.setattr("events.views.updateEvent_model", fake_update)

    response = auth_client.post(reverse("eventFormUpdate", args=[2]), {"title": "Err"})

    assert response.status_code == 400
    assert response.json()["error"].startswith("API Error: fail")


def test_event_search_redirects_when_missing_query(client):
    response = client.get(reverse("eventSearchByKeywords"), {"q": "   "})

    assert response.status_code == 302
    assert response.url == reverse("events")


def test_event_search_renders_results(client, monkeypatch, sample_event):
    monkeypatch.setattr("events.views.eventSearchByKeywords_model", lambda query: [sample_event])

    response = client.get(reverse("eventSearchByKeywords"), {"q": "sample"})

    assert response.status_code == 200
    assert response.context["eventAPI"] == [sample_event]
    assert response.context["query"] == "sample"


@pytest.mark.parametrize(
    ("url_name", "patch_target"),
    [
        ("eventsSortedByCreationDate", "eventsSortedByCreationDate_model"),
        ("eventsSortedByStartDate", "eventsSortedByStartDate_model"),
        ("eventsSortedByEndDate", "eventsSortedByEndDate_model"),
        ("eventsSortedByUpdateDate", "eventsSortedByUpdateDate_model"),
    ],
)
def test_event_sorting_endpoints(client, monkeypatch, sample_event, url_name, patch_target):
    monkeypatch.setattr(f"events.views.{patch_target}", lambda: [sample_event])

    response = client.get(reverse(url_name))

    assert response.status_code == 200
    assert response.context["eventAPI"] == [sample_event]


def test_events_multiple_filters_and_input(client, monkeypatch, sample_event):
    captured = {}

    def fake_multiple_filters(params):
        captured["params"] = params
        return [sample_event]

    monkeypatch.setattr("events.views.eventsMultipleFiltersAndInput_model", fake_multiple_filters)

    response = client.get(reverse("eventsMultipleFiltersAndInput"), {"filter": "creator_id", "value": "7"})

    assert response.status_code == 200
    assert response.context["eventAPI"] == [sample_event]
    assert captured["params"] == {"creator_id": "7", "limit": 10, "page": 1}
