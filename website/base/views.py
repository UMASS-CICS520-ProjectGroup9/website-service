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
    """Renders the home page with a preview of courses and user authentication status.

    Retrieves the access token from the session, fetches the list of courses,
    and slices the first 3 items for a dashboard preview. It also retrieves
    current user authentication details.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'index.html' template with 'authen' and 'courses' context.
    """
    token = request.session.get("access_token")
    
    # If course data exists, slice it to keep only the first 3 items (e.g., for a dashboard preview)
    course_data = courseAPI(token=token)
    if course_data:
        course_data = course_data[:3]

    authen = getAuthen(request)

    context = {
        'authen': authen,
        'courses': course_data
    }
    
    return render(request, 'index.html', context)

def discussions_page(request, page):
    """Fetches and renders a paginated list of discussions as an HTML fragment.

    This view is designed for AJAX/HTMX requests to load discussion data dynamically.
    It fetches data from the discussion API, sorts it by 'updated_at' in descending order,
    and returns a specific slice of data based on the requested page number.

    Args:
        request (HttpRequest): The HTTP request object.
        page (int): The page number to retrieve (1-based index).

    Returns:
        HttpResponse: An HTML fragment string containing the list of discussions
                      and pagination metadata. Returns an empty list on API failure.
    """
    token = request.session.get("access_token")

    discussions = []
    if token:
        try:
            discussions = discussionAPI(token=token)
            
            # If discussions exist, sort them by 'updated_at' in descending order (newest first)
            if discussions:
                discussions = sorted(discussions, key=lambda x: x["updated_at"], reverse=True)
        except Exception as e:
            print(f"DEBUG: Failed to fetch discussions: {e}")
            discussions = []

    # Pagination logic: Set items per page to 5
    per_page = 5
    # Calculate total pages (rounding up)
    total_pages = math.ceil(len(discussions) / per_page) if discussions else 1

    # Calculate start and end indices for slicing the data for the current page
    start = (page - 1) * per_page
    end = start + per_page

    # Get the data for the specific page
    page_data = discussions[start:end]

    # Render the HTML fragment (not the full page), likely for AJAX/HTMX loading
    html = render_to_string(
        "pages/dashboard/discussion_list_fragment.html",
        {
            "discussions": page_data,
            "current_page": page,
            "total_pages": total_pages,
        }
    )

    return HttpResponse(html)

def events_page(request, page):
    """Fetches, parses, and renders a paginated list of events as an HTML fragment.

    Retrieves events sorted by start date, parses their date strings (ISO 8601) into
    Python datetime objects, and paginates the results. Handles potential parsing
    or fetching errors by returning an error message within the HTML fragment.

    Args:
        request (HttpRequest): The HTTP request object.
        page (int): The page number to retrieve (1-based index).

    Returns:
        HttpResponse: An HTML fragment string containing the paginated events.
                      If an error occurs, returns a fragment with an error message.
    """

    today = timezone.localdate()
    try:
        events_data = eventsSortedByStartDate_model()
        # Iterate through events to parse date strings into Python datetime objects
        for e in events_data:
            if isinstance(e["created_at"], str):
                e["created_at"] = parser.parse(e["created_at"])
            if isinstance(e.get("event_start_date"), str):
                e["event_start_date"] = parser.parse(e["event_start_date"])
            if isinstance(e.get("event_end_date"), str):
                e["event_end_date"] = parser.parse(e["event_end_date"])

        # Pagination logic: Set items per page to 3
        per_page = 3
        total_pages = math.ceil(len(events_data) / per_page)

        # Slice the data to get events for the current page
        start = (page - 1) * per_page
        end = start + per_page
        page_events = events_data[start:end]

        # Render the partial HTML fragment
        html = render_to_string("pages/dashboard/event_list_fragment.html", {
            "events": page_events,
            "current_page": page,
            "total_pages": total_pages,
        })
    except Exception as e:
        # Render an error fragment or message
        html = render_to_string("pages/dashboard/event_list_fragment.html", {
            "events": [],
            "current_page": page,
            "total_pages": 1,
            "error_message": f"Could not load events: {str(e)}"
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

def logout(request):
    request.session.flush()
    return redirect("login")