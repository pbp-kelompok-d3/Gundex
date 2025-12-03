from django.urls import path
from . import views

app_name = 'userprofile'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('flutter/login/', views.flutter_login, name='flutter_login'),
    path('flutter/register/', views.flutter_register, name='flutter_register'),
    path('flutter/logout/', views.flutter_logout, name='flutter_logout'),
    path('flutter/profile/', views.get_user_profile_flutter, name='flutter_profile'),
    path('flutter/update-profile/', views.update_profile_flutter, name='flutter_update_profile'),
]