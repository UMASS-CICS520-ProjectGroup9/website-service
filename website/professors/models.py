import requests
from django.conf import settings

PROFESSORS_API_BASE_URL = settings.PROFESSORS_API_BASE_URL

def get_professors_api(query='', token=None):
    params = {}
    if query:
        params['query'] = query
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    try:
        response = requests.get(PROFESSORS_API_BASE_URL, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def get_professor_api(pk, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    try:
        url = f"{PROFESSORS_API_BASE_URL}{pk}/"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def create_review_api(pk, data, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    try:
        url = f"{PROFESSORS_API_BASE_URL}{pk}/review/"
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 201
    except requests.exceptions.RequestException:
        return False

def create_professor_api(data, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    try:
        url = f"{PROFESSORS_API_BASE_URL}create/"
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 201
    except requests.exceptions.RequestException:
        return False

def delete_professor_api(pk, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    try:
        url = f"{PROFESSORS_API_BASE_URL}{pk}/delete/"
        response = requests.delete(url, headers=headers)
        return response.status_code == 204
    except requests.exceptions.RequestException:
        return False

def delete_review_api(pk, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    try:
        url = f"{PROFESSORS_API_BASE_URL}review/{pk}/delete/"
        response = requests.delete(url, headers=headers)
        return response.status_code == 204
    except requests.exceptions.RequestException:
        return False
