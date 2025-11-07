from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', views.events, name='events'),
    path('events/<int:id>/', views.getEventByID, name='getEventByID'),
    path('discussions/', views.discussions, name='discussions'),
    path('courses/', views.courses, name='courses'),
    path('professors/', views.professors, name='professors'),
    path('myworkplace/', views.myworkplace, name='myworkplace'),  
]
