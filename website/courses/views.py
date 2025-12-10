from django.shortcuts import render, redirect
from .models import courseAPI, posts, delete_course_api, create_course_api


def courses(request):
    """
    Render the courses page with all available courses.
    Calls courseAPI() with no filters to fetch all courses.
    """
    token = request.session.get("access_token")
    courses = courseAPI(token=token)
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    return render(request, 'pages/courses/courses.html', {'courseAPI': courses, 'searched': False, 'authen': authen})


def get_courses_from_api(courseSubject='', courseID='', title='', instructor='', token=None):
    """
    Helper to fetch courses from the API with optional filters.
    Passes all arguments to courseAPI().
    """
    return courseAPI(courseSubject, courseID, title, instructor, token=token)


def course_search(request):
    """
    Handle course search requests from the frontend form.
    Extracts filter parameters from GET request and fetches filtered courses.
    Renders the courses page with search results.
    """
    courseSubject = request.GET.get('courseSubject', '')
    courseID = request.GET.get('courseID', '')
    title = request.GET.get('title', '')
    instructor = request.GET.get('instructor', '')
    
    token = request.session.get("access_token")
    error = None
    courses = []
    try:
        courses = get_courses_from_api(courseSubject, courseID, title, instructor, token=token)
    except Exception as e:
        error = str(e) or "An error occurred while searching for courses."
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    context = {'courseAPI': courses, 'searched': True, 'authen': authen}
    if error:
        context['error'] = error
    return render(request, 'pages/courses/courses.html', context)

def delete_course(request, courseSubject, courseID):
    """
    Handle course deletion.
    """
    role = request.session.get("role")
    if role not in ['ADMIN', 'STAFF']:
        return redirect('courses')
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    if request.method == 'POST':
        token = request.session.get("access_token")
        success = False
        error = None
        try:
            success = delete_course_api(courseSubject, courseID, token=token)
        except Exception as e:
            error = str(e) or "An error occurred while deleting the course."
        if not success or error:
            # Render the courses page with error
            courses = courseAPI(token=token)
            context = {
                'courseAPI': courses,
                'searched': False,
                'authen': authen,
                'error': error or "Failed to delete course."
            }
            return render(request, 'pages/courses/courses.html', context)
    return redirect('courses')

def add_course(request):
    """
    Handle adding a new course.
    """
    role = request.session.get("role")
    if role not in ['ADMIN', 'STAFF']:
        return redirect('courses')
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    error = None
    if request.method == 'POST':
        data = {
            'courseSubject': request.POST.get('courseSubject'),
            'courseID': request.POST.get('courseID'),
            'title': request.POST.get('title'),
            'instructor': request.POST.get('instructor'),
            'credits': request.POST.get('credits'),
            'schedule': request.POST.get('schedule'),
            'room': request.POST.get('room'),
            'requirements': request.POST.get('requirements'),
            'description': request.POST.get('description'),
            'instruction_mode': request.POST.get('instruction_mode'),
        }
        token = request.session.get("access_token")
        try:
            success = create_course_api(data, token=token)
        except Exception as e:
            error = str(e) or "An error occurred while adding the course."
            success = False
        if success:
            return redirect('courses')
        else:
            error = error or "Failed to add course. Please check your input."
    return render(request, 'pages/courses/add_course.html', {'authen': authen, 'error': error} if error else {'authen': authen})
