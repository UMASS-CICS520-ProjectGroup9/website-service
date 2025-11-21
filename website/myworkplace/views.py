from django.shortcuts import render, redirect
import requests
from .models import posts

def getAuthen(request):
    return  {
        "is_login" : "access_token" in request.session,
        "user_email" : request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }

def myworkplace(request):
    is_login = "access_token" in request.session
    if not is_login:
        return redirect("login")
    authen = getAuthen(request)
    data = []
    if authen.get('role') != "ADMIN":
        headers = {
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"
            }
        res = requests.get(f"http://127.0.0.1:9002/api/events/{authen.get('user_id')}/creator_id/", headers=headers)
        data = res.json()
        
    else:
        response = requests.get("http://127.0.0.1:9002/api/events/")
        data = response.json()
    return render(request, 'pages/myworkplace/myworkplace.html', {"events": data, "authen": authen})
