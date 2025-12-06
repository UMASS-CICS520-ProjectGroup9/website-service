
import requests
from django.conf import settings

posts = [{"topic": "Discussion about CSCI 520", "author": "Alice", "date": "2024-01-15"},
         {"topic": "Study Group for Algorithms", "author": "Bob", "date": "2024-01-16"},
         {"topic": "Exam Preparation Tips", "author": "Charlie", "date": "2024-01-17"}]

COURSES_API_BASE_URL = settings.COURSES_API_BASE_URL

# Create your models here.
def courseAPI(courseSubject='', courseID='', title='', instructor='', token=None):
    """
    Fetch course data from the external API, optionally filtered by parameters.

    Args:
        courseSubject (str): Filter by course subject code (e.g., 'COMPSCI').
        courseID (str): Filter by course ID.
        title (str): Filter by course title.
        instructor (str): Filter by instructor name.
        token (str): JWT access token for authentication.

    Returns:
        list: List of course dictionaries returned by the API.
    """
    params = {}
    if courseSubject:
        params['courseSubject'] = courseSubject
    if courseID:
        params['courseID'] = courseID
    if title:
        params['title'] = title
    if instructor:
        params['instructor'] = instructor
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    try:
        response = requests.get(COURSES_API_BASE_URL, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            # If 403/401, it might be because we are not logged in, return empty list or handle gracefully
            return []
    except requests.exceptions.RequestException:
        return []

def delete_course_api(courseSubject, courseID, token=None):
    """
    Delete a course via the API.
    """
    url = f"{COURSES_API_BASE_URL}{courseSubject}/{courseID}/delete/"
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    try:
        response = requests.delete(url, headers=headers)
        return response.status_code == 204
    except requests.exceptions.RequestException:
        return False

def create_course_api(data, token=None):
    """
    Create a course via the API.
    """
    url = f"{COURSES_API_BASE_URL}create/"
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    try:
        response = requests.post(url, data=data, headers=headers)
        return response.status_code == 201
    except requests.exceptions.RequestException:
        return False