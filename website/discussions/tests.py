import pytest
import requests
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_discussion_list_renders_and_paginates(client, monkeypatch):
    # Create 15 fake discussions so pagination is exercised (10 per page)
    fake = [{"id": i, "title": f"D{i}", "updated_at": "2025-01-01T00:00:00Z"} for i in range(15)]

    # views import discussionAPI into the views namespace, patch there
    monkeypatch.setattr("discussions.views.discussionAPI", lambda token=None: fake)

    url = reverse("discussions")
    response = client.get(url)

    assert response.status_code == 200
    # view places paginated object_list into 'discussions'
    assert len(response.context["discussions"]) == 10
    assert response.context["page_obj"].paginator.num_pages == 2


def test_discussion_detail_renders_with_comments(client, monkeypatch):
    fake_discussion = {"id": 1, "title": "Thread", "body": "content"}
    fake_comments = [{"id": 101, "body": "ok"}]

    # patch functions imported into views module
    monkeypatch.setattr("discussions.views.getDiscussionByID_model", lambda pk, token=None: fake_discussion)
    monkeypatch.setattr("discussions.views.getCommentsByDiscussion_model", lambda pk, token=None: fake_comments)

    url = reverse("discussion_detail", kwargs={"pk": 1})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["discussion"] == fake_discussion
    assert response.context["comments"] == fake_comments
    assert "authen" in response.context


def test_discussion_create_post_redirects_and_calls_model(client, monkeypatch):
    called = {}

    def fake_create(payload, token=None):
        called['payload'] = payload
        return {"id": 9}

    # views imported createDiscussion_model at module level; patch there
    monkeypatch.setattr("discussions.views.createDiscussion_model", fake_create)

    url = reverse("discussion_create")
    data = {"author": "a", "title": "T", "body": "B"}
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse("discussions")
    assert called['payload']["author"] == "a"
    assert called['payload']["title"] == "T"
    assert called['payload']["body"] == "B"


def test_discussion_create_ajax_returns_201(client, monkeypatch):
    def fake_create(payload, token=None):
        return {"id": 10}

    monkeypatch.setattr("discussions.views.createDiscussion_model", fake_create)

    url = reverse("discussion_create")
    data = {"author": "a", "title": "T", "body": "B"}
    response = client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert response.status_code == 201
    assert response.json().get("ok") is True


def test_discussion_create_ajax_validation_error(client):
    url = reverse("discussion_create")
    # missing title/body
    response = client.post(url, {"author": "a"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert response.status_code == 400
    assert response.json().get("ok") is False


def test_comment_create_posts_and_redirects(client, monkeypatch):
    called = {}

    def fake_create(payload, token=None):
        called['payload'] = payload
        return {"id": 55}

    # comment_create imports createComment_model inside the view; patch models name
    monkeypatch.setattr("discussions.models.createComment_model", fake_create)

    url = reverse("discussion_comment_create", kwargs={"pk": 3})
    data = {"author": "me", "body": "hello"}
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse("discussion_detail", kwargs={"pk": 3})
    assert called['payload']["author"] == "me"
    assert called['payload']["body"] == "hello"


def test_removeDiscussion_get_and_post(client, monkeypatch):
    fake_discussion = {"id": 7, "title": "t"}

    monkeypatch.setattr("discussions.views.getDiscussionByID_model", lambda id, token=None: fake_discussion)

    url = reverse("removeDiscussion", kwargs={"id": 7})
    # GET shows confirmation
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.context["discussion"] == fake_discussion

    captured = {}

    def fake_remove(id, headers=None):
        captured['id'] = id
        captured['headers'] = headers
        return {"status": "ok"}

    monkeypatch.setattr("discussions.views.removeDiscussion_model", fake_remove)

    # set session token so header is built
    session = client.session
    session["access_token"] = "tok"
    session["user_id"] = 42
    session.save()

    resp2 = client.post(url)
    assert resp2.status_code == 302
    assert resp2.url == reverse("discussions")
    assert captured['id'] == 7
    assert "Authorization" in captured['headers']


def test_removeComment_get_and_post(client, monkeypatch):
    # GET confirmation
    url = reverse("removeComment", kwargs={"id": 99})
    resp = client.get(url)
    assert resp.status_code == 200

    captured = {}

    def fake_remove(id, headers=None):
        captured['id'] = id
        captured['headers'] = headers
        return {"status": "ok"}

    monkeypatch.setattr("discussions.models.removeComment_model", fake_remove)

    # POST with discussion_id should redirect back to discussion_detail
    resp2 = client.post(url, {"discussion_id": "77"})
    assert resp2.status_code == 302
    assert resp2.url == reverse("discussion_detail", kwargs={"pk": "77"})
    assert captured['id'] == 99


def test_discussion_create_handles_api_error_ajax_and_non_ajax(client, monkeypatch):
    # createDiscussion_model raising should result in redirect for non-AJAX
    def raise_exc(payload, token=None):
        raise Exception("upstream")

    monkeypatch.setattr("discussions.views.createDiscussion_model", raise_exc)

    url = reverse("discussion_create")
    resp = client.post(url, {"author": "a", "title": "T", "body": "B"})
    assert resp.status_code == 302
    assert resp.url == reverse("discussions")

    # AJAX should return 502 with error message
    resp2 = client.post(url, {"author": "a", "title": "T", "body": "B"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert resp2.status_code == 502
    assert resp2.json().get("ok") is False
    assert resp2.json().get("error") == "Upstream service error."


def test_comment_create_handles_exception(client, monkeypatch):
    # If createComment_model raises, the view should swallow and still redirect back
    def raise_exc(payload, token=None):
        raise Exception("boom")

    monkeypatch.setattr("discussions.models.createComment_model", raise_exc)

    url = reverse("discussion_comment_create", kwargs={"pk": 5})
    resp = client.post(url, {"author": "u", "body": "b"})

    assert resp.status_code == 302
    assert resp.url == reverse("discussion_detail", kwargs={"pk": 5})


def test_removeDiscussion_post_failure_returns_500(client, monkeypatch):
    # Make the removeDiscussion_model raise a requests.RequestException
    def raise_req(id, headers=None):
        raise requests.RequestException("fail")

    monkeypatch.setattr("discussions.views.removeDiscussion_model", raise_req)

    # Set session values used to build headers
    session = client.session
    session["access_token"] = "tok"
    session["user_id"] = 42
    session.save()

    url = reverse("removeDiscussion", kwargs={"id": 7})
    resp = client.post(url)
    assert resp.status_code == 500
    assert resp.json().get("error")


def test_removeComment_post_failure_returns_500(client, monkeypatch):
    # Make the removeComment_model raise a requests.RequestException
    def raise_req(id, headers=None):
        raise requests.RequestException("fail")

    monkeypatch.setattr("discussions.models.removeComment_model", raise_req)

    url = reverse("removeComment", kwargs={"id": 99})
    resp = client.post(url)
    assert resp.status_code == 500
    assert resp.json().get("error")
