from django.urls import path
from explore_gunung.views import show_json, show_gunung

app_name = 'explore_gunung'

urlpatterns = [
    path('json/', show_json, name='show_json'),
    path('gunung/<str:id>/', show_gunung, name='show_gunung'),
]