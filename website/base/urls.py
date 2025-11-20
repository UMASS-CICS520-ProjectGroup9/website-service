from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('login/process/', views.loginProcess, name='loginProcess'),
    path('register/create/', views.registerCreate, name='registerCreate'),
    path('logout/', views.logout, name='logout'),
    
    
    ]
