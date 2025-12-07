from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.show_wishlist, name='show_wishlist'),
    path('json/', views.get_wishlist_json, name='get_wishlist_json'),
    path('add/', views.add_to_wishlist_ajax, name='add_to_wishlist_ajax'),
    path('remove/<int:item_id>/', views.remove_from_wishlist_ajax, name='remove_from_wishlist_ajax'),
    path('flutter/json/', views.flutter_get_wishlist, name='flutter_get_wishlist'),
    path('flutter/add/', views.flutter_add_to_wishlist, name='flutter_add_to_wishlist'),
    path('flutter/remove/<int:item_id>/', views.flutter_remove_from_wishlist, name='flutter_remove_from_wishlist'),
    path('flutter/check/<str:gunung_id>/', views.flutter_check_wishlist_status, name='flutter_check_wishlist_status'),
]