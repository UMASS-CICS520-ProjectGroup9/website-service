from django.shortcuts import render, redirect
import requests
from django.views.decorators.http import require_http_methods
from discussions.models import discussionAPI
from events.models import eventsSortedByStartDate_model
from courses.models import courseAPI
from dateutil import parser
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import math

USERAUTH_API_BASE_URL = settings.USERAUTH_API_BASE_URL # Replace with actual API URL

# Create your views here.

def getAuthen(request):
    return  {
        "is_login" : "access_token" in request.session,
        "user_email" : request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }

def index(request):
    token = request.session.get('access_token')
    discussion_data = discussionAPI(token=token)
    if discussion_data:
        discussion_data = sorted(discussion_data, key=lambda x: x['updated_at'], reverse=True)
    
    token = request.session.get("access_token")
    print(f"DEBUG: Index view - Token present: {bool(token)}")
    if token:
        print(f"DEBUG: Token: {token[:10]}...")

    course_data = courseAPI(token=token)
    if course_data:
        course_data = course_data[:3]

    authen = getAuthen(request)

    context = {
        'discussions': discussion_data,
        'authen': authen,
        'courses': course_data
    }
    
    return render(request, 'index.html', context)

def events_page(request, page):
    today = timezone.localdate()

    events_data = eventsSortedByStartDate_model()
    events_today = [
        e for e in events_data
        if parser.parse(e["event_start_date"]).date() == today
    ]
    
    for e in events_today:
        if isinstance(e["created_at"], str):
            e["created_at"] = parser.parse(e["created_at"])
        if isinstance(e.get("event_start_date"), str):
            e["event_start_date"] = parser.parse(e["event_start_date"])
        if isinstance(e.get("event_end_date"), str):
            e["event_end_date"] = parser.parse(e["event_end_date"])

    # For change pages
    per_page = 5
    total_pages = math.ceil(len(events_today) / per_page)

    # slice page data
    start = (page - 1) * per_page
    end = start + per_page
    page_events = events_today[start:end]

    # render partial fragment
    html = render_to_string("components/event_list_fragment.html", {
        "events": page_events,
        "current_page": page,
        "total_pages": total_pages,
    })

    return HttpResponse(html)

def register(request):
    return render(request, 'pages/authentication/register.html')

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
        res = requests.post(f"{USERAUTH_API_BASE_URL}/api/register/", json=data)
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
        res = requests.post(f"{USERAUTH_API_BASE_URL}/api/token/", json=data)
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