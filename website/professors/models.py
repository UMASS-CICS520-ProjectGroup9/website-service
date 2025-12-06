
import requests
from django.conf import settings

PROFESSORS_API_BASE_URL = settings.PROFESSORS_API_BASE_URL

def get_professors_api(query=''):
    params = {}
    if query:
        params['query'] = query
    try:
        response = requests.get(PROFESSORS_API_BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def get_professor_api(pk):
    try:
        url = f"{PROFESSORS_API_BASE_URL}{pk}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def create_review_api(pk, data):
    try:
        url = f"{PROFESSORS_API_BASE_URL}{pk}/review/"
        response = requests.post(url, json=data)
        return response.status_code == 201
    except requests.exceptions.RequestException:
        return False
