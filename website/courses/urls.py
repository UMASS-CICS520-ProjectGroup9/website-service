from django.urls import path
from . import views 

urlpatterns = [
    path('', views.courses, name='courses'),
    path('search/', views.course_search, name='course_search'),
    path('add/', views.add_course, name='add_course'),
    path('delete/<str:courseSubject>/<int:courseID>/', views.delete_course, name='delete_course'),
]