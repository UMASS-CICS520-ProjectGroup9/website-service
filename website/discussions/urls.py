from django.urls import path
from . import views

urlpatterns = [
    path('', views.discussion_list, name='discussions'),
    path('<int:pk>/', views.discussion_detail, name='discussion_detail'),
]