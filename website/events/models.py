from django.db import models
import requests

posts = [{"topic": "Discussion about CSCI 520", "author": "Alice", "date": "2024-01-15"},
         {"topic": "Study Group for Algorithms", "author": "Bob", "date": "2024-01-16"},
         {"topic": "Exam Preparation Tips", "author": "Charlie", "date": "2024-01-17"}]

EXTERNAL_API_BASE_URL = "http://127.0.0.1:9002/api/events/"  # Replace with actual API URL

# Create your models here.
def eventAPI():
    response = requests.get("http://127.0.0.1:9002/api/events/")
    data = response.json()
    return data  
    
def getEventByID_model(id):
    response = requests.get(f"http://127.0.0.1:9002/api/events/{id}")
    print(response.status_code)
    response.raise_for_status()
    data = response.json()
    return data

def createEvent_model(event_data, headers):
    response = requests.post("http://127.0.0.1:9002/api/events/create/", json=event_data, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

def removeEvent_model(id, headers):
    
    response = requests.delete(f"http://127.0.0.1:9002/api/events/{id}/delete/", headers=headers)
    response.raise_for_status()
    return {"status": "success", "message": f"Event {id} removed."}

def updateEvent_model(id, event_data, headers):
    response = requests.put(f"http://127.0.0.1:9002/api/events/{id}/update/", json=event_data, headers=headers)
    response.raise_for_status()
    return {"status": "success", "message": f"Event {id} updated."}
    
def eventSearchByKeywords_model(query):
    params = {
        "q": query,
        "page": 1,
        "limit": 10
    }
    respone = requests.get("http://127.0.0.1:9002/api/events/search/", params=params)
    respone.raise_for_status
    return respone.json()

def eventsSortedByCreationDate_model():
    respone = requests.get("http://127.0.0.1:9002/api/events/sorted_by_creation_date/")
    respone.raise_for_status
    return respone.json()

def eventsSortedByStartDate_model():
    respone = requests.get("http://127.0.0.1:9002/api/events/sorted_by_start_date/")
    respone.raise_for_status
    return respone.json()

def eventsSortedByEndDate_model():
    respone = requests.get("http://127.0.0.1:9002/api/events/sorted_by_end_date/")
    respone.raise_for_status
    return respone.json()

def eventsSortedByUpdateDate_model():
    respone = requests.get("http://127.0.0.1:9002/api/events/sorted_by_update_date/")
    respone.raise_for_status
    return respone.json()

def eventsMultipleFiltersAndInput_model(params):
    respone = requests.get("http://127.0.0.1:9002/api/events/filters/", params=params)
    respone.raise_for_status
    return respone.json()