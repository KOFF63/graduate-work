from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_material, name='add_material'),  # <-- эта строка
    path('search/', views.search_materials, name='search_materials'),
    path('subject/<int:subject_id>/', views.subject_materials, name='subject_materials'),
]