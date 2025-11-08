from django.urls import path
from . import views 

urlpatterns = [
    path('', views.events, name='events'),
    path('<int:id>/', views.getEventByID, name='getEventByID'),
    path('create/', views.eventForm, name='eventForm'),
    path('create/form', views.eventFormCreation, name='eventFormCreation'),
    path('remove/<int:id>/', views.removeEvent, name='removeEvent'),
]