from django.db import models
import requests

posts = [{"topic": "Discussion about CSCI 520", "author": "Alice", "date": "2024-01-15"},
         {"topic": "Study Group for Algorithms", "author": "Bob", "date": "2024-01-16"},
         {"topic": "Exam Preparation Tips", "author": "Charlie", "date": "2024-01-17"}]

# Create your models here.
def eventAPI():
    response = requests.get("http://127.0.0.1:9002/api/events/")
    data = response.json()
    return data  
    
def getEventByID_model(id):
    response = requests.get(f"http://127.0.0.1:9002/api/events/{id}")
    data = response.json()
    return data
