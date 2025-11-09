
import requests

DISCUSSION_API_BASE_URL = "http://127.0.0.1:9003/api/discussions/"

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


