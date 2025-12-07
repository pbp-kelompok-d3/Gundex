from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from artikel.views import artikel_detail, show_artikel, create_artikel, edit_artikel, delete_artikel, get_random_recommendations, edit_artikel_modal

app_name = 'artikel'

urlpatterns = [
    path('', show_artikel, name='show_artikel'),
    path('artikel/<uuid:id>/', artikel_detail, name='artikel_detail'),
    path('create-artikel/', create_artikel, name='create_artikel'),
    path('edit-artikel/<uuid:id>/', edit_artikel, name='edit_artikel'),
    path('delete-artikel/<uuid:id>/', delete_artikel, name='delete_artikel'),
    path("refresh-recommendations/", get_random_recommendations, name="refresh_recommendations"),
    path('edit-artikel-modal/<uuid:id>/', edit_artikel_modal, name='edit_artikel_modal'),
    path('like-artikel/<uuid:id>/', views.like_artikel, name='like_artikel'),
    path("get-random-recommendations/", views.get_random_recommendations, name="get_random_recommendations"),
    path("api/artikel/", views.show_json, name="api_list_artikel"),
    path("api/artikel/<uuid:id>/", views.show_json_by_id, name="api_artikel_detail"),
    path("api/flutter/<uuid:id>/edit/", views.edit_artikel_flutter, name="api_edit_artikel_flutter"),
    path("api/flutter/<uuid:id>/delete/", views.delete_artikel_flutter, name="api_delete_artikel_flutter"),
    path("proxy/", views.proxy_image, name="proxy_image"),
    path('api/flutter/create/', views.create_artikel_flutter, name='create_artikel_flutter'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
