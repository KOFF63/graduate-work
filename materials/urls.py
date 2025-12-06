from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('subject/<int:subject_id>/', views.subject_materials, name='subject_materials'),
    path('search/', views.search_materials, name='search_materials'),
]