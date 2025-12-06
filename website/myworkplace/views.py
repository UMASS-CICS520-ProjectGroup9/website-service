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
    event_data = []
    discussion_data = []
    comments_data = []
    courses_data = []
    professors_data = []
    if authen.get('role') != "ADMIN":
        headers = {
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"
            }
        res_student_events = requests.get(f"http://127.0.0.1:9002/api/events/{authen.get('user_id')}/creator_id/", headers=headers)
        event_data = res_student_events.json()
        #res_student_discussions = requests.get(f"http://127.0.0.1:8000/api/discussions/{authen.get('user_id')}/creator_id/", headers=headers)
        #discussion_data = res_student_discussions.json()
        discussion_data = []
        comments_data = []
        courses_data = []
        professors_data = []
        
    else:
        res_admin_events = requests.get("http://127.0.0.1:9002/api/events/")
        event_data = res_admin_events.json()
        res_admin_discussions = requests.get("http://127.0.0.1:8000/api/discussions/")
        discussion_data = res_admin_discussions.json()
        res_admin_comments = requests.get("http://127.0.0.1:8000/api/comments/")
        comments_data = res_admin_comments.json()
        res_admin_courses = requests.get("http://127.0.0.1:9005/api/courses/")
        courses_data = res_admin_courses.json()
        #res_admin_professors = requests.get("http://127.0.0.1:8000/api/professors/")
        #professors_data = res_admin_professors.json()

    context = {
        'events': event_data,
        'authen': authen,
        'discussions':discussion_data,
        'comments':comments_data,
        'courses':courses_data,
        'professors':professors_data
    }    

    return render(request, 'pages/myworkplace/myworkplace.html', context)
