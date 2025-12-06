from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Subject, Material


def home(request):
    subjects = Subject.objects.all()
    recent_materials = Material.objects.all().order_by('-upload_date')[:6]

    # Статистика по типам материалов
    material_stats = {}
    for material_type, _ in Material.MATERIAL_TYPES:
        material_stats[material_type] = Material.objects.filter(material_type=material_type).count()

    return render(request, 'materials/home.html', {
        'subjects': subjects,
        'recent_materials': recent_materials,
        'material_stats': material_stats,
    })


def subject_materials(request, subject_id):
    """Страница материалов по предмету"""
    subject = get_object_or_404(Subject, id=subject_id)
    materials = Material.objects.filter(subject=subject).order_by('-upload_date')

    # Фильтрация по типу материала
    material_type = request.GET.get('type', '')
    if material_type:
        materials = materials.filter(material_type=material_type)

    return render(request, 'materials/subject_detail.html', {
        'subject': subject,
        'materials': materials,
        'current_filter': material_type,
    })


def search_materials(request):
    """Страница поиска материалов"""
    query = request.GET.get('q', '')
    materials = []

    if query:
        materials = Material.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(subject__name__icontains=query)
        ).order_by('-upload_date')

    return render(request, 'materials/search_results.html', {
        'materials': materials,
        'query': query,
    })