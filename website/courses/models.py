
import requests
from django.conf import settings

posts = [{"topic": "Discussion about CSCI 520", "author": "Alice", "date": "2024-01-15"},
         {"topic": "Study Group for Algorithms", "author": "Bob", "date": "2024-01-16"},
         {"topic": "Exam Preparation Tips", "author": "Charlie", "date": "2024-01-17"}]

EXTERNAL_API_BASE_URL = settings.EXTERNAL_API_BASE_URL

# Create your models here.
def courseAPI(courseSubject='', courseID='', title='', instructor=''):
    """
    Fetch course data from the external API, optionally filtered by parameters.

    Args:
        courseSubject (str): Filter by course subject code (e.g., 'COMPSCI').
        courseID (str): Filter by course ID.
        title (str): Filter by course title.
        instructor (str): Filter by instructor name.

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
    response = requests.get(EXTERNAL_API_BASE_URL, params=params)
    data = response.json()
    return data

def delete_course_api(courseSubject, courseID):
    """
    Delete a course via the API.
    """
    url = f"{EXTERNAL_API_BASE_URL}{courseSubject}/{courseID}/delete/"
    response = requests.delete(url)
    return response.status_code == 204

def create_course_api(data):
    """
    Create a course via the API.
    """
    url = f"{EXTERNAL_API_BASE_URL}create/"
    response = requests.post(url, data=data)
    return response.status_code == 201