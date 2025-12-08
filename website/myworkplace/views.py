from django.shortcuts import render, redirect
import requests
from django.conf import settings
from dateutil import parser

PROFESSORS_API_BASE_URL = settings.PROFESSORS_API_BASE_URL
COURSES_API_BASE_URL = settings.COURSES_API_BASE_URL
DISCUSSIONS_API_BASE_URL = settings.DISCUSSIONS_API_BASE_URL
COMMENTS_API_BASE_URL = settings.COMMENTS_API_BASE_URL
COURSE_DISCUSSION_API_BASE_URL = settings.COURSE_DISCUSSION_API_BASE_URL
COURSE_COMMENTS_API_BASE_URL = settings.COURSE_COMMENTS_API_BASE_URL
EVENTS_API_BASE_URL = settings.EVENTS_API_BASE_URL

def getAuthen(request):
    return  {
        "is_login" : "access_token" in request.session,
        "user_email" : request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }

def getProfessorsReviews(professors_data, authen):
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

def filter_user_discussions(discussion_data, authen):
    user_id = authen.get('user_id')
    role = authen.get('role')
    my_discussions = []
    my_comments = []

    for discussion in discussion_data:
        if role == 'ADMIN' or discussion.get('creator_id') == user_id:
            my_discussions.append(discussion)

        comments = discussion.get('comments', [])
        for comment in comments:
            if role == 'ADMIN' or comment.get('creator_id') == user_id:
                my_comments.append(comment)

    return my_discussions, my_comments

def filter_course_discussions_and_comments(discussion_data, authen):
    """
    Filter course discussions and comments for the current user
    """
    user_id = authen.get('user_id')
    role = authen.get('role')
    my_discussions = []
    my_comments = []

    for discussion in discussion_data:
        if role == 'ADMIN':
            # Convert created_at to datetime object for template formatting
            if isinstance(discussion.get("created_at"), str):
                try:
                    discussion["created_at"] = parser.parse(discussion["created_at"])
                except:
                    pass
            my_discussions.append(discussion)

        comments = discussion.get('comments', [])
        for comment in comments:
            if role == 'ADMIN' or comment.get('creator_id') == user_id:
                # Convert created_at to datetime object for template formatting
                if isinstance(comment.get("created_at"), str):
                    try:
                        comment["created_at"] = parser.parse(comment["created_at"])
                    except:
                        pass
                my_comments.append(comment)

    return my_discussions, my_comments

def myworkplace(request):
    is_login = "access_token" in request.session
    if not is_login:
        return redirect("login")
    authen = getAuthen(request)
    event_data = []
    discussion_data = []
    comments_data = []
    courses_data = []
    courses_discussion_data = []
    courses_discussion_comments_data = []
    professors_data = []
    professors_reviews_data = []

    headers = {
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"
            }
    
    res_discussions = requests.get(DISCUSSIONS_API_BASE_URL)
    discussion_data, comments_data = filter_user_discussions(res_discussions.json(), authen)
    
    res_professors = requests.get(f"{PROFESSORS_API_BASE_URL}", headers=headers)
    professors_data = res_professors.json()
    professors_reviews_data = getProfessorsReviews(professors_data, authen)
    
    res_courses = requests.get(f"{COURSES_API_BASE_URL}", headers=headers)
    courses_data = res_courses.json()

    # Fetch all course discussions at once
    try:
        res_course_discussions = requests.get(COURSE_DISCUSSION_API_BASE_URL, headers=headers)
        if res_course_discussions.status_code == 200:
            all_course_discussions = res_course_discussions.json()
            if isinstance(all_course_discussions, list):
                # Filter by user ownership
                courses_discussion_data, courses_discussion_comments_data = filter_course_discussions_and_comments(all_course_discussions, authen)
    except Exception as e:
        print(f"Error fetching course discussions: {e}")

    if authen.get('role') != "ADMIN":    
        res_student_events = requests.get(f"{EVENTS_API_BASE_URL}/api/events/{authen.get('user_id')}/creator_id/", headers=headers)
        event_data = res_student_events.json()
        courses_data = []
        professors_data = []
        
    else:
        res_admin_events = requests.get(f"{EVENTS_API_BASE_URL}/api/events/")
        event_data = res_admin_events.json()

    context = {
        'events': event_data,
        'authen': authen,
        'discussions':discussion_data,
        'comments':comments_data,
        'courses':courses_data,
        'professors':professors_data,
        'professorsReviews':professors_reviews_data,
        'coursesDiscussions':courses_discussion_data,
        'coursesDiscussionComments':courses_discussion_comments_data
    }    

    return render(request, 'pages/myworkplace/myworkplace.html', context)
