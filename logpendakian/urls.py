from django.urls import path
from . import views

app_name = "logpendakian"
urlpatterns = [
    path("", views.log_list, name="list"),
    path("new/", views.log_create, name="create"),
    path("<uuid:pk>/edit/", views.log_update, name="update"),
    path("<uuid:pk>/delete/", views.log_delete, name="delete"),
]
