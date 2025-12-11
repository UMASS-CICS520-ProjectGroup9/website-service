from django.urls import path
from . import views 

urlpatterns = [
    path('', views.professors, name='professors'),
    path('add/', views.add_professor, name='add_professor'),
    path('<int:pk>/', views.professor_detail, name='professor_detail'),
    path('<int:pk>/delete/', views.delete_professor, name='delete_professor'),
    path('<int:prof_pk>/review/<int:review_pk>/delete/', views.delete_review, name='delete_review'),
]