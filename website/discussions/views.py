from django.shortcuts import render
from .models import posts

def discussions(request):
    return render(request, 'pages/discussions/discussions.html')