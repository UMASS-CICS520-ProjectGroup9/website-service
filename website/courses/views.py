from django.shortcuts import render
from .models import posts

def courses(request):
    return render(request, 'pages/courses/courses.html')
