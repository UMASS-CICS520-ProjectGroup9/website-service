from django.shortcuts import render
import requests
from .models import posts

def myworkplace(request):
    is_login = "access_token" in request.session
    return render(request, 'pages/myworkplace/myworkplace.html', {"is_login": is_login})
