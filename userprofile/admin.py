from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    # Add custom fields to the admin interface
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'is_admin')}),
    )
    
    list_display = UserAdmin.list_display + ('is_admin', 'bio')
    list_filter = UserAdmin.list_filter + ('is_admin',)