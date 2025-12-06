from django.shortcuts import render, redirect
from .models import courseAPI, posts, delete_course_api, create_course_api


def courses(request):
    """
    Render the courses page with all available courses.
    Calls courseAPI() with no filters to fetch all courses.
    """
    courses = courseAPI()
    return render(request, 'pages/courses/courses.html', {'courseAPI': courses, 'searched': False})


def get_courses_from_api(courseSubject='', courseID='', title='', instructor=''):
    """
    Helper to fetch courses from the API with optional filters.
    Passes all arguments to courseAPI().
    """
    return courseAPI(courseSubject, courseID, title, instructor)


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
    courses = get_courses_from_api(courseSubject, courseID, title, instructor)
    return render(request, 'pages/courses/courses.html', {'courseAPI': courses, 'searched': True})

def delete_course(request, courseSubject, courseID):
    """
    Handle course deletion.
    """
    if request.method == 'POST':
        delete_course_api(courseSubject, courseID)
    return redirect('courses')

def add_course(request):
    """
    Handle adding a new course.
    """
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
        if create_course_api(data):
            return redirect('courses')
        else:
            # Handle error (maybe pass an error message to the template)
            pass
            
    return render(request, 'pages/courses/add_course.html')
