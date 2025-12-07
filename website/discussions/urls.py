from django.urls import path
from . import views

urlpatterns = [
    path('', views.discussion_list, name='discussions'),
    path('create/', views.discussion_create, name='discussion_create'),
    path('<int:pk>/comment/', views.comment_create, name='discussion_comment_create'),
    path('detail/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    # Place specific routes before generic course routes to avoid conflicts
    path('remove/<int:id>/', views.removeDiscussion, name='removeDiscussion'),
    path('comment/remove/<int:id>/', views.removeComment, name='removeComment'),
    path('<str:course_subject>/<str:course_id>/', views.course_discussion_detail, name='course_discussion_detail'),
    path('<str:course_subject>/<str:course_id>/comment/', views.course_comment_create, name='course_comment_create'),
]