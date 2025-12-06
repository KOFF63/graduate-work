from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'created_at']
    search_fields = ['user__username', 'role', 'department']
    list_filter = ['role', 'created_at']