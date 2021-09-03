
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='Index'),
    path('search/', views.search, name='Search'),
    path('login/', views.login_attempt, name='Login'),
    path('logout/', views.logout_attempt, name='Logout'),
    path('resister/', views.register_attempt, name='Register'),
]
