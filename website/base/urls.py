from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', views.events, name='events'),
    path('discussions/', views.discussions, name='discussions'),
    path('courses/', views.courses, name='courses'),
    path('professors/', views.professors, name='professors'),
    path('myplan/', views.myplan, name='myplan'),   
]
