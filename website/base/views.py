from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

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