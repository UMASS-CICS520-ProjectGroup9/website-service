from django.shortcuts import render, redirect
import requests
from django.conf import settings
from dateutil import parser
from django.views.decorators.http import require_http_methods

# Load API base URLs from Django settings
PROFESSORS_API_BASE_URL = settings.PROFESSORS_API_BASE_URL
COURSES_API_BASE_URL = settings.COURSES_API_BASE_URL
DISCUSSIONS_API_BASE_URL = settings.DISCUSSIONS_API_BASE_URL
COMMENTS_API_BASE_URL = settings.COMMENTS_API_BASE_URL
COURSE_DISCUSSION_API_BASE_URL = settings.COURSE_DISCUSSION_API_BASE_URL
COURSE_COMMENTS_API_BASE_URL = settings.COURSE_COMMENTS_API_BASE_URL
EVENTS_API_BASE_URL = settings.EVENTS_API_BASE_URL

def getAuthen(request):
    # Helper to retrieve user authentication info from session
    return  {
        "is_login" : "access_token" in request.session,
        "user_email" : request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }

def getProfessorsReviews(professors_data, authen):
    """Processes and filters professor reviews based on user role.

    Flattens the nested review structure within professor data. Admins can see
    all reviews, while regular users are filtered to see only reviews they created.
    Also parses date strings and attaches professor metadata to each review.

    Args:
        professors_data (list): A list of professor dictionaries containing nested reviews.
        authen (dict): Authentication details including 'role' and 'user_id'.

    Returns:
        list: A flattened list of processed review dictionaries.
    """

    all_reviews_list = []

    for professor in professors_data:
        professor_name = professor.get('name', 'Unknown Professor')
        professor_id = professor.get('id') 
        
        reviews = professor.get('reviews', [])
        
        for review in reviews:
            # Filter: Admins see all, regular users only see their own reviews
            if authen.get('role') != 'ADMIN' and review.get('creator_id') != authen.get('user_id'):
                continue

            review_with_name = review.copy()
            
            # Parse date string to datetime object
            if isinstance(review_with_name["created_at"], str):
                review_with_name["created_at"] = parser.parse(review_with_name["created_at"])
            
            # Attach professor info to the review for display
            review_with_name['professor_name'] = professor_name
            review_with_name['professor_id'] = professor_id
            
            all_reviews_list.append(review_with_name)
            
    return all_reviews_list

def filter_user_discussions(discussion_data, authen):
    """Filters general discussions and comments based on ownership and role.

    Admins have access to all content. Non-admin users are restricted to seeing
    only the discussions and comments they created.

    Args:
        discussion_data (list): A list of discussion dictionaries.
        authen (dict): Authentication details including 'role' and 'user_id'.

    Returns:
        tuple: A tuple containing two lists:
            - my_discussions (list): Filtered discussions.
            - my_comments (list): Filtered comments.
    """

    user_id = authen.get('user_id')
    role = authen.get('role')
    my_discussions = []
    my_comments = []

    for discussion in discussion_data:
        # Add discussion if user is Admin or the creator
        if role == 'ADMIN' or discussion.get('creator_id') == user_id:
            my_discussions.append(discussion)

        # Process comments within the discussion
        comments = discussion.get('comments', [])
        for comment in comments:
            if role == 'ADMIN' or comment.get('creator_id') == user_id:
                my_comments.append(comment)

    return my_discussions, my_comments

def filter_course_discussions_and_comments(discussion_data, authen):
    """Filters course-specific discussions and comments, including date parsing.

    Similar to general discussion filtering, but specifically for course threads.
    It parses 'created_at' timestamps into datetime objects and appends course
    metadata (subject, ID) to comments for context.

    Args:
        discussion_data (list): A list of course discussion dictionaries.
        authen (dict): Authentication details including 'role' and 'user_id'.

    Returns:
        tuple: A tuple containing two lists:
            - my_discussions (list): Filtered and date-parsed discussions.
            - my_comments (list): Filtered and date-parsed comments.
    """
    user_id = authen.get('user_id')
    role = authen.get('role')
    my_discussions = []
    my_comments = []

    for discussion in discussion_data:
        # Admin check: Parse date and add to list
        if role == 'ADMIN':
            # Convert created_at to datetime object for template formatting
            if isinstance(discussion.get("created_at"), str):
                try:
                    discussion["created_at"] = parser.parse(discussion["created_at"])
                except:
                    pass
            my_discussions.append(discussion)

        # Process comments inside course discussions
        comments = discussion.get('comments', [])
        for comment in comments:
            # Filter: Admin or comment owner
            if role == 'ADMIN' or comment.get('creator_id') == user_id:
                # Convert created_at to datetime object for template formatting
                if isinstance(comment.get("created_at"), str):
                    try:
                        comment["created_at"] = parser.parse(comment["created_at"])
                    except:
                        pass
                # Add course information to comment for context
                comment['course_subject'] = discussion.get('course_subject')
                comment['course_id'] = discussion.get('course_id')
                my_comments.append(comment)

    return my_discussions, my_comments

def format_event_dates(event_data):
    """Parses ISO 8601 date strings in event data into datetime objects.

    Iterates through the event list and converts 'event_start_date' and
    'event_end_date' from strings to Python datetime objects for correct
    template rendering.

    Args:
        event_data (list): A list of event dictionaries.

    Returns:
        list: The modified list of events with parsed datetime objects.
    """
    if not isinstance(event_data, list):
        return event_data
    
    for event in event_data:
        if isinstance(event, dict):
            # Parse start date
            if isinstance(event.get("event_start_date"), str):
                try:
                    event["event_start_date"] = parser.parse(event["event_start_date"])
                except:
                    pass
            
            # Parse end date
            if isinstance(event.get("event_end_date"), str):
                try:
                    event["event_end_date"] = parser.parse(event["event_end_date"])
                except:
                    pass
    
    return event_data

def myworkplace(request):
    """Renders the 'My Workplace' dashboard with aggregated user data.

    Aggregates data from multiple backend services (Discussions, Professors,
    Courses, Events). It applies role-based logic to determine what data the
    user can see (e.g., Students see their own events; Admins see all events).

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'myworkplace.html' template with aggregated context,
                      or a redirect to the login page if unauthorized.
    """
    # Check if user is logged in
    is_login = "access_token" in request.session
    if not is_login:
        return redirect("login")
    
    authen = getAuthen(request)
    
    # Initialize data containers
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
    
    # 1. Fetch and filter General Discussions
    res_discussions = requests.get(DISCUSSIONS_API_BASE_URL)
    discussion_data, comments_data = filter_user_discussions(res_discussions.json(), authen)
    
    # 2. Fetch Professors and filter Reviews
    res_professors = requests.get(f"{PROFESSORS_API_BASE_URL}", headers=headers)
    professors_data = res_professors.json()
    professors_reviews_data = getProfessorsReviews(professors_data, authen)
    
    # 3. Fetch Courses
    res_courses = requests.get(f"{COURSES_API_BASE_URL}", headers=headers)
    courses_data = res_courses.json()

    # 4. Fetch and filter Course Discussions
    try:
        res_course_discussions = requests.get(COURSE_DISCUSSION_API_BASE_URL, headers=headers)
        if res_course_discussions.status_code == 200:
            all_course_discussions = res_course_discussions.json()
            if isinstance(all_course_discussions, list):
                # Filter by user ownership
                courses_discussion_data, courses_discussion_comments_data = filter_course_discussions_and_comments(all_course_discussions, authen)
    except Exception as e:
        print(f"Error fetching course discussions: {e}")

    # 5. Handle Role-specific Logic (Student vs Admin)
    if authen.get('role') != "ADMIN":    
        # Student: Fetch their specific events
        res_student_events = requests.get(f"{EVENTS_API_BASE_URL}/api/events/{authen.get('user_id')}/creator_id/", headers=headers)
        event_data = res_student_events.json()
        event_data = format_event_dates(event_data)
        
        # Hide raw lists for students (they don't manage these directly here)
        courses_data = []
        professors_data = []
        
    else:
        # Admin: Fetch all events
        res_admin_events = requests.get(f"{EVENTS_API_BASE_URL}/api/events/")
        event_data = res_admin_events.json()
        event_data = format_event_dates(event_data)

    # 6. Prepare context and render template
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