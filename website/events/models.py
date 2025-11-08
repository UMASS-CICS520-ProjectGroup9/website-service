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

def createEvent_model(event_data):
    response = requests.post("http://127.0.0.1:9002/api/events/create/", json=event_data)
    response.raise_for_status()
    data = response.json()
    return data

def removeEvent_model(id):
    
    response = requests.delete(f"http://127.0.0.1:9002/api/events/{id}/delete/")
    response.raise_for_status()
    return {"status": "success", "message": f"Event {id} removed."}
