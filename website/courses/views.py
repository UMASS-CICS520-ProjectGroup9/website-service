from django.shortcuts import render
from .models import courseAPI, posts


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
