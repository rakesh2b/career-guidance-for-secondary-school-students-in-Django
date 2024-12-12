# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('aptitude-test/', views.aptitude_test, name='aptitude_test'),
    path('result/', views.result, name='result'),
    path('careers/', views.careers, name='careers'),  # Add this line
]
