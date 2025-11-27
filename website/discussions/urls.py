from django.urls import path
from . import views

urlpatterns = [
    path('', views.discussion_list, name='discussions'),
    path('create/', views.discussion_create, name='discussion_create'),
    path('<int:pk>/comment/', views.comment_create, name='discussion_comment_create'),
    path('<int:pk>/', views.discussion_detail, name='discussion_detail'),
]