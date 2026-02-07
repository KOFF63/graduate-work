"""
Views (контроллеры) для приложения materials.

Обрабатывают HTTP-запросы и возвращают HTML-страницы.
Каждая функция соответствует определенной странице сайта.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Subject, Material


def home(request):
    """
    Обработчик главной страницы сайта.

    Args:
        request (HttpRequest): HTTP-запрос от пользователя

    Returns:
        HttpResponse: HTML страница с данными

    Context:
        subjects (QuerySet): Все предметы из базы данных
        recent_materials (QuerySet): Последние 6 материалов
        material_stats (dict): Статистика по типам материалов

    Template:
        materials/home.html
    """
    # Если пользователь не авторизован - показываем приветственную страницу
    if not request.user.is_authenticated:
        # Считаем общую статистику для показа на приветственной странице
        subject_count = Subject.objects.count()
        material_count = Material.objects.count()

        return render(request, 'materials/welcome.html', {
            'subject_count': subject_count,
            'material_count': material_count,
        })

    # Для авторизованных пользователей - обычная главная страница
    # Получаем все предметы для отображения на главной
    subjects = Subject.objects.all()

    # Получаем последние материалы для блока "Новое"
    recent_materials = Material.objects.all().order_by('-upload_date')[:6]

    # Собираем статистику по типам материалов
    material_stats = {}
    for material_type, _ in Material.MATERIAL_TYPES:
        material_stats[material_type] = Material.objects.filter(
            material_type=material_type
        ).count()

    # Подготавливаем данные для шаблона
    context = {
        'subjects': subjects,
        'recent_materials': recent_materials,
        'material_stats': material_stats,
    }

    return render(request, 'materials/home.html', context)


@login_required(login_url='/users/login/')
def subject_materials(request, subject_id):
    """
    Страница материалов по конкретному предмету.

    Args:
        request (HttpRequest): HTTP-запрос
        subject_id (int): ID предмета из URL

    Returns:
        HttpResponse: Страница с материалами выбранного предмета

    Raises:
        404: Если предмет с указанным ID не существует

    Context:
        subject (Subject): Объект выбранного предмета
        materials (QuerySet): Материалы по предмету
        current_filter (str): Текущий фильтр по типу материала

    Template:
        materials/subject_detail.html
    """
    # Получаем предмет или возвращаем 404 если не найден
    subject = get_object_or_404(Subject, id=subject_id)

    # Базовый запрос - все материалы по предмету
    materials = Material.objects.filter(subject=subject).order_by('-upload_date')

    # Фильтрация по типу материала если указан
    material_type = request.GET.get('type', '')
    if material_type:
        materials = materials.filter(material_type=material_type)

    context = {
        'subject': subject,
        'materials': materials,
        'current_filter': material_type,
    }

    return render(request, 'materials/subject_detail.html', context)


@login_required(login_url='/users/login/')
def search_materials(request):
    """
    Страница результатов поиска материалов.

    Args:
        request (HttpRequest): HTTP-запрос с GET-параметром 'q'

    Returns:
        HttpResponse: Страница с результатами поиска

    Context:
        materials (QuerySet): Найденные материалы
        query (str): Поисковый запрос

    Template:
        materials/search_results.html
    """
    # Получаем поисковый запрос из GET-параметров
    query = request.GET.get('q', '')
    materials = []

    # Выполняем поиск только если запрос не пустой
    if query:
        materials = Material.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(subject__name__icontains=query)
        ).order_by('-upload_date')

    context = {
        'materials': materials,
        'query': query,
    }

    return render(request, 'materials/search_results.html', context)


def is_admin(user):
    """Проверка что пользователь администратор."""
    return user.is_superuser


@user_passes_test(is_admin, login_url='/users/login/')
def add_material(request):
    """
    Страница добавления нового материала.
    Доступна только для администраторов.

    Args:
        request (HttpRequest): HTTP-запрос

    Returns:
        HttpResponse: Страница добавления материала или перенаправление

    Process:
        1. Проверяем что пользователь администратор
        2. Показываем форму с выбором предмета
        3. Принимаем данные формы
        4. Создаем материал
        5. Перенаправляем на страницу предмета
    """
    # Получаем все предметы для отображения в форме
    subjects = Subject.objects.all()

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            subject_id = request.POST.get('subject')
            material_type = request.POST.get('material_type')
            tags = request.POST.get('tags', '').strip()
            external_link = request.POST.get('external_link', '').strip()

            # Валидация обязательных полей
            if not title:
                messages.error(request, 'Название материала обязательно.')
                return redirect('add_material')

            if not description:
                messages.error(request, 'Описание материала обязательно.')
                return redirect('add_material')

            if not subject_id:
                messages.error(request, 'Выберите предмет.')
                return redirect('add_material')

            if not material_type:
                messages.error(request, 'Выберите тип материала.')
                return redirect('add_material')

            # Получаем предмет
            subject = get_object_or_404(Subject, id=subject_id)

            # Создаем материал
            material = Material(
                title=title,
                description=description,
                subject=subject,
                material_type=material_type,
                uploaded_by=request.user,
                tags=tags,
                external_link=external_link if external_link else ''
            )

            # Обработка загруженного файла
            if 'file' in request.FILES:
                file = request.FILES['file']
                material.file = file

            material.save()

            messages.success(request, f'✓ Материал "{title}" успешно добавлен в предмет "{subject.name}"!')
            return redirect('subject_materials', subject_id=subject.id)

        except Exception as e:
            messages.error(request, f'✗ Ошибка при добавлении материала: {str(e)}')
            return redirect('add_material')

    return render(request, 'materials/add_material.html', {
        'subjects': subjects,
        'material_types': Material.MATERIAL_TYPES,
        'title': 'Добавить материал',
    })