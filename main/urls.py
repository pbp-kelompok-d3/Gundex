from django.urls import path
from . import views  # Import views module

app_name = 'main'

urlpatterns = [
    path('', views.redirect_to_login, name='redirect_to_login'),
    path('home/', views.show_main, name='show_main'), 
]