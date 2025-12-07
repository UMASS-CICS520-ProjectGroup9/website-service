
import requests
from django.conf import settings

# NOTE: Ensure this port matches your discussions-service runserver port (DRF UI shows 8000 in your screenshots)
DISCUSSIONS_API_BASE_URL = f"{settings.DISCUSSIONS_API_BASE_URL}"
COMMENT_API_BASE_URL = f"{settings.COMMENTS_API_BASE_URL}"
COURSE_DISCUSSION_API_BASE_URL = f"{settings.COURSE_DISCUSSION_API_BASE_URL}"
COURSE_COMMENT_API_BASE_URL = f"{settings.COURSE_COMMENTS_API_BASE_URL}"

# Get all discussions
def discussionAPI():
    response = requests.get(DISCUSSIONS_API_BASE_URL)
    response.raise_for_status()
    return response.json()

# Get a single discussion by ID
def getDiscussionByID_model(id):
    response = requests.get(f"{DISCUSSIONS_API_BASE_URL}{id}/")
    response.raise_for_status()
    return response.json()

# Create a new discussion
def createDiscussion_model(discussion_data):
    response = requests.post(DISCUSSIONS_API_BASE_URL, json=discussion_data)
    response.raise_for_status()
    return response.json()

# Delete a discussion by ID
def removeDiscussion_model(id, headers=None):
    """Delete a discussion by ID.
    Optionally pass headers (e.g., Authorization) for protected endpoints.
    """
    response = requests.delete(f"{DISCUSSIONS_API_BASE_URL}{id}/", headers=headers or {})
    response.raise_for_status()
    return {"status": "success", "message": f"Discussion {id} removed."}


# Get comments for a given discussion ID
def getCommentsByDiscussion_model(discussion_id):
    params = {"discussion": discussion_id}
    response = requests.get(COMMENT_API_BASE_URL, params=params)
    response.raise_for_status()
    return response.json()


# Create a new comment for a given discussion
def createComment_model(comment_data):
    """comment_data should be a dict with keys: discussion (id), author, body"""
    response = requests.post(COMMENT_API_BASE_URL, json=comment_data)
    response.raise_for_status()
    return response.json()

def removeComment_model(id, headers=None):
    """Delete a comment by ID. Headers may include Authorization and X-User-ID."""
    response = requests.delete(f"{COMMENT_API_BASE_URL}{id}/", headers=headers or {})
    response.raise_for_status()
    return {"status": "success", "message": f"Comment {id} removed."}


# Get a course discussion by subject and ID
def get_course_discussion_model(course_subject, course_id, token=None):
    url = f"{COURSE_DISCUSSION_API_BASE_URL}{course_subject}/{course_id}/"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers)
    print(f"[DEBUG] GET {url} -> status {response.status_code}, response: {response.text}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def get_course_comments_model(course_subject, course_id, token=None):
    params = {"course_subject": course_subject, "course_id": course_id}
    headers = {}
    if token:
        print(f"[DEBUG] Sending JWT token: {token}")
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(COURSE_COMMENT_API_BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def create_course_comment_model(comment_data, token=None):
    """comment_data should be a dict with keys: discussion (id), author, body"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.post(COURSE_COMMENT_API_BASE_URL, json=comment_data, headers=headers)
    response.raise_for_status()
    return response.json()

def remove_course_comment_model(id, headers=None):
    """Delete a course comment by ID. Headers may include Authorization and X-User-ID."""
    response = requests.delete(f"{COURSE_COMMENT_API_BASE_URL}{id}/", headers=headers or {})
    response.raise_for_status()
    return {"status": "success", "message": f"CourseComment {id} removed."}