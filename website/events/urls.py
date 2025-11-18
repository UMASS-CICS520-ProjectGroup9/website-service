from django.urls import path
from . import views 

urlpatterns = [
    path('', views.events, name='events'),
    path('<int:id>/', views.getEventByID, name='getEventByID'),
    path('create/', views.eventForm, name='eventForm'),
    path('create/form', views.eventFormCreation, name='eventFormCreation'),
    path('update/form/<int:id>/', views.eventFormUpdate, name='eventFormUpdate'),
    path('remove/<int:id>/', views.removeEvent, name='removeEvent'),
    path('search/', views.eventSearchByKeywords, name="eventSearchByKeywords"),
    path('sorted_by_creation_date/', views.eventsSortedByCreationDate, name="eventsSortedByCreationDate"),
    path('sorted_by_start_date/', views.eventsSortedByStartDate, name="eventsSortedByStartDate"),
    path('sorted_by_end_date/', views.eventsSortedByEndDate, name="eventsSortedByEndDate"),
    path('sorted_by_update_date/', views.eventsSortedByUpdateDate, name="eventsSortedByUpdateDate"),
    path('filters/', views.eventsMultipleFiltersAndInput, name="eventsMultipleFiltersAndInput")
    
]