from django.shortcuts import render
import requests

# posts = [{"topic": "Discussion about CSCI 520", "author": "Alice", "date": "2024-01-15"},
#          {"topic": "Study Group for Algorithms", "author": "Bob", "date": "2024-01-16"},
#          {"topic": "Exam Preparation Tips", "author": "Charlie", "date": "2024-01-17"}]
# Create your views here.
def index(request):
    response = requests.get('https://ea9a53d8-d237-4b92-bb0b-57a0b3beb806.mock.pstmn.io/test')
    context = {
        'posts': response.json()
    }
    return render(request, 'index.html', context)

def events(request):
    return render(request, 'pages/events/events.html')

def discussions(request):
    return render(request, 'pages/discussions/discussions.html')

def courses(request):
    return render(request, 'pages/courses/courses.html')

def professors(request):
    return render(request, 'pages/professors/professors.html')

def myplan(request):
    return render(request, 'pages/myplan/myplan.html')

def myplan(request):
    return render(request, 'pages/myplan/myplan.html')