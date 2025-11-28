
import requests

# NOTE: Ensure this port matches your discussions-service runserver port (DRF UI shows 8000 in your screenshots)
DISCUSSION_API_BASE_URL = "http://127.0.0.1:8000/api/discussions/"
COMMENT_API_BASE_URL = "http://127.0.0.1:8000/api/comments/"

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


