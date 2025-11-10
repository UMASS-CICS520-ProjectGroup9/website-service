from django.shortcuts import render
from .models import courseAPI, posts

def courses(request):
    courses = courseAPI()
    return render(request, 'pages/courses/courses.html', {'courseAPI': courses, 'searched': False})

def get_courses_from_api(courseSubject='', courseID='', title='', instructor=''):
    return courseAPI(courseSubject, courseID, title, instructor)

def course_search(request):
    courseSubject = request.GET.get('courseSubject', '')
    courseID = request.GET.get('courseID', '')
    title = request.GET.get('title', '')
    instructor = request.GET.get('instructor', '')
    courses = get_courses_from_api(courseSubject, courseID, title, instructor)
    return render(request, 'pages/courses/courses.html', {'courseAPI': courses, 'searched': True})
