
import requests

posts = [{"topic": "Discussion about CSCI 520", "author": "Alice", "date": "2024-01-15"},
         {"topic": "Study Group for Algorithms", "author": "Bob", "date": "2024-01-16"},
         {"topic": "Exam Preparation Tips", "author": "Charlie", "date": "2024-01-17"}]

EXTERNAL_API_BASE_URL = "http://127.0.0.1:9004/api/courses/"  # Replace with actual API URL

# Create your models here.
def courseAPI(courseSubject='', courseID='', title='', instructor=''):
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