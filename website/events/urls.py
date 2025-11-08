from django.urls import path
from . import views 

urlpatterns = [
    path('', views.events, name='events'),
    path('<int:id>/', views.getEventByID, name='getEventByID'),
    path('create/', views.eventForm, name='eventForm'),
]