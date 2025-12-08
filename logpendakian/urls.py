from django.urls import path
from . import views

app_name = "logpendakian"
urlpatterns = [
    path("", views.log_list, name="list"),
    path("new/", views.log_create, name="create"),
    path("<uuid:pk>/edit/", views.log_update, name="update"),
    path("<uuid:pk>/delete/", views.log_delete, name="delete"),
    path("json/", views.log_list_json, name="list_json"),
    path("<uuid:pk>/json/", views.log_detail_json, name="detail_json"),
    path("api/create/", views.log_create_api, name="log_create_api"),
    path("api/update/<uuid:pk>/", views.log_update_api, name="log_update_api"),
    path("api/delete/<uuid:pk>/", views.log_delete_api, name="log_delete_api"),
]
