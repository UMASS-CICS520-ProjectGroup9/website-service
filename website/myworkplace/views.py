from django.shortcuts import render, redirect
import requests
from django.conf import settings
from dateutil import parser

PROFESSORS_API_BASE_URL = settings.PROFESSORS_API_BASE_URL
COURSES_API_BASE_URL = settings.COURSES_API_BASE_URL
DISCUSSIONS_API_BASE_URL = settings.DISCUSSIONS_API_BASE_URL
COMMENTS_API_BASE_URL = settings.COMMENTS_API_BASE_URL
EVENTS_API_BASE_URL = settings.EVENTS_API_BASE_URL

def getAuthen(request):
    return  {
        "is_login" : "access_token" in request.session,
        "user_email" : request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }

def getProfessorsReviews(professors_data, authen):
    print(professors_data)
    all_reviews_list = []

    for professor in professors_data:
        professor_name = professor.get('name', 'Unknown Professor')
        
        reviews = professor.get('reviews', [])
        
        for review in reviews:
            if authen.get('role') != 'ADMIN' and review.get('creator_id') != authen.get('user_id'):
                continue

            review_with_name = review.copy()
            
            if isinstance(review_with_name["created_at"], str):

                review_with_name["created_at"] = parser.parse(review_with_name["created_at"])
            
            review_with_name['professor_name'] = professor_name
            
            all_reviews_list.append(review_with_name)
            
    return all_reviews_list

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
    professors_reviews_data = []

    headers = {
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"
            }
    
    res_admin_professors = requests.get(f"{PROFESSORS_API_BASE_URL}", headers=headers)
    professors_data = res_admin_professors.json()
    professors_reviews_data = getProfessorsReviews(professors_data, authen)

    if authen.get('role') != "ADMIN":    
        res_student_events = requests.get(f"{EVENTS_API_BASE_URL}/api/events/{authen.get('user_id')}/creator_id/", headers=headers)
        event_data = res_student_events.json()
        #res_student_discussions = requests.get(f"DISCUSSIONS_API_BASE_URL/{authen.get('user_id')}/creator_id/", headers=headers)
        #discussion_data = res_student_discussions.json()
        discussion_data = []
        comments_data = []
        courses_data = []
        professors_data = []
        
    else:
        res_admin_events = requests.get(f"{EVENTS_API_BASE_URL}/api/events/")
        event_data = res_admin_events.json()
        #res_admin_discussions = requests.get(DISCUSSIONS_API_BASE_URL)
        #discussion_data = res_admin_discussions.json()
        discussion_data = []
        #res_admin_comments = requests.get(COMMENTS_API_BASE_URL)
        #comments_data = res_admin_comments.json()
        comments_data = []
        res_admin_courses = requests.get(COURSES_API_BASE_URL)
        courses_data = res_admin_courses.json()

    context = {
        'events': event_data,
        'authen': authen,
        'discussions':discussion_data,
        'comments':comments_data,
        'courses':courses_data,
        'professors':professors_data,
        'professorsReviews':professors_reviews_data
    }    

    return render(request, 'pages/myworkplace/myworkplace.html', context)
