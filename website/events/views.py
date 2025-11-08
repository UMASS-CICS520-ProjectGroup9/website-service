from django.shortcuts import render
import requests
from .models import posts, getEventByID_model
from .models import eventAPI

def events(request):
    events = eventAPI()
    return render(request, 'pages/events/events.html', {'eventAPI': events})

def getEventByID(request, id):
    event = getEventByID_model(id)
    return render(request, 'pages/events/singleEvent.html', {'event': event})

def eventForm(request):
    return render(request, 'pages/events/event_form.html')
