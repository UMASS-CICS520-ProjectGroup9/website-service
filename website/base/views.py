from django.shortcuts import render, redirect
import requests
from django.views.decorators.http import require_http_methods

from .models import posts

def getAuthen(request):
    return  {
        "is_login" : "access_token" in request.session,
        "user_email" : request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }

# Create your views here.
def index(request):
    authen = getAuthen(request)
    return render(request, 'index.html', { 'posts': posts, 'authen': authen })

def register(request):
    return render(request, 'pages/authentication/register.html')

USERAUTH_URL = "http://127.0.0.1:9111"   # your user auth service

@require_http_methods(["GET", "POST"])
def registerCreate(request): 
    """
    Handle register form submission to external API, user authen service.
    GET: Display the form
    POST: Submit to external API, user authen service
    """
    
    
    if request.method == "POST":
        
        password = request.POST.get("password"),
        password = password[0]
        confirm_password = request.POST.get("confirm_password")
        if password != confirm_password:
            # print("31-password:", password==confirm_password)
            return render(request, 'pages/authentication/register.html', {"error": "Confirm Password must be same!"})
        
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": password,  
            "role": "STUDENT"  
        }
        print("37-data:", data)
        # # Send to UserAuth API
        res = requests.post(f"{USERAUTH_URL}/api/register/", json=data)
        print("44-data:", res.json())
        if res.status_code == 201 or res.status_code == 200:
            return redirect("login")
        else:
            return render(request, 'pages/authentication/register.html', {"error": res.json()})

    return render(request, 'pages/authentication/register.html') 

def login(request):
    return render(request, 'pages/authentication/login.html')

@require_http_methods(["POST"])
def loginProcess(request): 
    """
    Handle login submission to external API, user authen service.
    POST: Submit to external API, user authen service
    """
    
    
    if request.method == "POST":
        data = {
            "email": request.POST.get("Email"),
            "password": request.POST.get("password"),
        }
        print("68-data: ", data)
        # Call login API
        res = requests.post(f"{USERAUTH_URL}/api/token/", json=data)
        print("71-res.json(): ", res.json())
        if res.status_code == 200:
            tokens = res.json()

            # # Store access token in Django session
            request.session["access_token"] = tokens["access"]
            request.session["refresh_token"] = tokens["refresh"]
            request.session["email"] = tokens.get("email")
            request.session["user_id"] = tokens.get("user_id")
            request.session["role"] = tokens.get("role")
            print("81-request.session.get('access_token'): ", request.session.get("access_token"))
            return redirect("index")   # go to protected page
        else:
            return render(request, 'pages/authentication/login.html', {"error": "Invalid login credentials"})

    return render(request, "login.html")

def logout(request):
    request.session.flush()
    return redirect("login")