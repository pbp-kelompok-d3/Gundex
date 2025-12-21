from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "artikel"

urlpatterns = [
    # =========================
    # WEB (HTML)
    # =========================
    path("", views.show_artikel, name="show_artikel"),
    path("artikel/<uuid:id>/", views.artikel_detail, name="artikel_detail"),
    path("create-artikel/", views.create_artikel, name="create_artikel"),
    path("edit-artikel/<uuid:id>/", views.edit_artikel, name="edit_artikel"),
    path("delete-artikel/<uuid:id>/", views.delete_artikel, name="delete_artikel"),
    path("edit-artikel-modal/<uuid:id>/", views.edit_artikel_modal, name="edit_artikel_modal"),
    path("refresh-recommendations/", views.get_random_recommendations, name="refresh_recommendations"),

    # =========================
    # INTERAKSI USER
    # =========================
    path("api/flutter/like-artikel/<uuid:id>/", views.like_artikel_flutter, name="like_artikel_flutter"),
    path("artikel/<uuid:id>/view/", views.increment_views, name="increment_views"),

    # =========================
    # API PUBLIK (READ ONLY)
    # =========================
    path("api/artikel/", views.show_json, name="api_list_artikel"),
    path("api/artikel/<uuid:id>/", views.show_json_by_id, name="api_artikel_detail"),
    path("api/latest/", views.api_latest_artikels),
    path("api/recommended/", views.api_recommended_artikels),
    path("api/popular/", views.api_popular_artikels),
    path("api/hottest/", views.api_hottest_artikels),

    # =========================
    # API FLUTTER (ADMIN)
    # =========================
    path("api/flutter/create/", views.create_artikel_flutter, name="api_create_artikel_flutter"),
    path("api/flutter/<uuid:id>/edit/", views.edit_artikel_flutter, name="api_edit_artikel_flutter"),
    path("api/flutter/<uuid:id>/delete/", views.delete_artikel_flutter, name="api_delete_artikel_flutter"),

    # =========================
    # UTIL
    # =========================
    path("proxy/", views.proxy_image, name="proxy_image"),
    path("api/whoami/", views.whoami),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
