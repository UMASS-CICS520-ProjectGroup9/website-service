from django.urls import path
from . import views 

urlpatterns = [
    path('', views.professors, name='professors'),
    path('<int:pk>/', views.professor_detail, name='professor_detail'),
]