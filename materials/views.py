from django.shortcuts import render
from .models import Subject, Material


def home(request):
    subjects = Subject.objects.all()
    recent_materials = Material.objects.all().order_by('-upload_date')[:6]

    return render(request, 'materials/home.html', {
        'subjects': subjects,
        'recent_materials': recent_materials,
    })