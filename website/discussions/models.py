import requests
from django.conf import settings

# NOTE: Ensure this port matches your discussions-service runserver port (DRF UI shows 8000 in your screenshots)
DISCUSSION_API_BASE_URL = f"{settings.DISCUSSIONS_API_BASE_URL}discussions/"
COMMENT_API_BASE_URL = f"{settings.DISCUSSIONS_API_BASE_URL}comments/"
COURSE_DISCUSSION_API_BASE_URL = f"{settings.DISCUSSIONS_API_BASE_URL}course-discussions/"
COURSE_COMMENT_API_BASE_URL = f"{settings.DISCUSSIONS_API_BASE_URL}course-comments/"

# Get all discussions
def discussionAPI():
    response = requests.get(DISCUSSION_API_BASE_URL)
    response.raise_for_status()
    return response.json()

# Get a single discussion by ID
def getDiscussionByID_model(id):
    response = requests.get(f"{DISCUSSION_API_BASE_URL}{id}/")
    response.raise_for_status()
    return response.json()

# Create a new discussion
def createDiscussion_model(discussion_data):
    response = requests.post(DISCUSSION_API_BASE_URL, json=discussion_data)
    response.raise_for_status()
    return response.json()

# Delete a discussion by ID
def removeDiscussion_model(id):
    response = requests.delete(f"{DISCUSSION_API_BASE_URL}{id}/")
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


# Get a course discussion by subject and ID
def get_course_discussion_model(course_subject, course_id):
    response = requests.get(f"{COURSE_DISCUSSION_API_BASE_URL}{course_subject}/{course_id}/")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def get_course_comments_model(course_subject, course_id):
    params = {"course_subject": course_subject, "course_id": course_id}
    response = requests.get(COURSE_COMMENT_API_BASE_URL, params=params)
    response.raise_for_status()
    return response.json()


def create_course_comment_model(comment_data):
    """comment_data should be a dict with keys: discussion (id), author, body"""
    response = requests.post(COURSE_COMMENT_API_BASE_URL, json=comment_data)
    response.raise_for_status()
    return response.json()