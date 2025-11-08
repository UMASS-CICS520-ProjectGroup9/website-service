from django.shortcuts import render
import requests
from .models import posts

def myworkplace(request):
    return render(request, 'pages/myworkplace/myworkplace.html')
