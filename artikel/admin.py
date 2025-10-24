from django.contrib import admin
from .models import Artikel

@admin.register(Artikel)
class ArtikelAdmin(admin.ModelAdmin):
    list_display  = ("title", "created_at", "updated_at", "views", "total_likes")
    search_fields = ("title", "description")
    list_filter   = ("created_at",)
    ordering      = ("-created_at",)
