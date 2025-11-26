from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'artikel'

urlpatterns = [
    # =======================
    # 🔹 Web (GunDex site)
    # =======================
    path('', views.show_artikel, name='show_artikel'),
    path('artikel/<uuid:id>/', views.artikel_detail, name='artikel_detail'),
    path('create-artikel/', views.create_artikel, name='create_artikel'),
    path('edit-artikel/<uuid:id>/', views.edit_artikel, name='edit_artikel'),
    path('delete-artikel/<uuid:id>/', views.delete_artikel, name='delete_artikel'),
    path('like-artikel/<uuid:id>/', views.like_artikel, name='like_artikel'),
    path('get-random-recommendations/', views.get_random_recommendations, name='get_random_recommendations'),

    # =======================
    # 🔹 Flutter API (JSON endpoints)
    # =======================
    path('api/artikel/create/', views.create_artikel_flutter, name='create_artikel_flutter'),
    path('api/artikel/edit/<uuid:artikel_id>/', views.edit_artikel_flutter, name='edit_artikel_flutter'),
    path('api/artikel/json/', views.show_json_all, name='show_json_all'),
    path('api/artikel/json/<uuid:id>/', views.show_json_by_id, name='show_json_by_id'),
    path('api/artikel/xml/', views.show_xml_all, name='show_xml_all'),
    path('api/artikel/xml/<uuid:id>/', views.show_xml_by_id, name='show_xml_by_id'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
