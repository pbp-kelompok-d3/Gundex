from django.urls import path
from explore_gunung.views import show_json, show_gunung, edit_gunung, get_gunung_json, delete_gunung

app_name = 'explore_gunung'

urlpatterns = [
    path('json/', show_json, name='show_json'),
    path('gunung/<str:id>/', show_gunung, name='show_gunung'),
    path('gunung/<str:id>/edit', edit_gunung, name='edit_gunung'),
    path('gunung/<str:id>/json/', get_gunung_json, name='get_gunung_json'),
    path('gunung/<str:id>/delete', delete_gunung, name='delete_gunung'),
]