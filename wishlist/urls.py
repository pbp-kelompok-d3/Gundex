from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.show_wishlist, name='show_wishlist'),
    path('json/', views.get_wishlist_json, name='get_wishlist_json'),  # Endpoint JSON baru
    path('add/', views.add_to_wishlist_ajax, name='add_to_wishlist_ajax'),
    path('remove/<int:item_id>/', views.remove_from_wishlist_ajax, name='remove_from_wishlist_ajax'),
]