from django.shortcuts import render
from .models import posts

def professors(request):
    return render(request, 'pages/professors/professors.html')
