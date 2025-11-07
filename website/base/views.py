from django.shortcuts import render
import requests
from .models import posts, getEventByID_model
from .models import eventAPI



# Create your views here.
def index(request):
    context = { 'posts': posts }
    # return render(request, 'index.html', context)
    return render(request, 'index.html', context)


def events(request):
    events = eventAPI()
    return render(request, 'pages/events/events.html', {'eventAPI': events})

def getEventByID(request, id):
    event = getEventByID_model(id)
    return render(request, 'pages/events/singleEvent.html', {'event': event})

def discussions(request):
    return render(request, 'pages/discussions/discussions.html')

def courses(request):
    return render(request, 'pages/courses/courses.html')

def professors(request):
    return render(request, 'pages/professors/professors.html')

def myworkplace(request):
    return render(request, 'pages/myworkplace/myworkplace.html')

