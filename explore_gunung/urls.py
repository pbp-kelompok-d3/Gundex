from django.urls import path
from explore_gunung.views import show_json

app_name = 'explore_gunung'

urlpatterns = [
    path('json/', show_json, name='show_json'),
]