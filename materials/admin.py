from django.contrib import admin
from .models import Subject, Material

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_per_page = 20

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'material_type', 'uploaded_by', 'upload_date']
    list_filter = ['subject', 'material_type', 'upload_date']
    search_fields = ['title', 'description', 'tags']
    date_hierarchy = 'upload_date'
    list_per_page = 25