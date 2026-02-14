"""
Views (контроллеры) для приложения materials.

Обрабатывают HTTP-запросы и возвращают HTML-страницы.
Каждая функция соответствует определенной странице сайта.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import Subject, Material
from .search_engine import SmartSearchEngine
import time

# Глобальный экземпляр поискового движка (создается один раз при запуске)
_search_engine = None


def get_search_engine():
    """
    Получить или создать поисковый движок (синглтон).
    """
    global _search_engine
    if _search_engine is None:
        _search_engine = SmartSearchEngine()
        # Пробуем загрузить сохраненный индекс
        if not _search_engine.load_index():
            print("ℹ Индекс не найден, будет построен при первом поиске")
    return _search_engine


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
        total_materials (int): Общее количество материалов

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
        'total_materials': Material.objects.count(),
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

    # Пагинация
    paginator = Paginator(materials, 12)  # 12 материалов на страницу
    page_number = request.GET.get('page', 1)
    page_materials = paginator.get_page(page_number)

    context = {
        'subject': subject,
        'materials': page_materials,
        'current_filter': material_type,
        'total_materials': materials.count(),
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_materials,
        'paginator': paginator,
    }

    return render(request, 'materials/subject_detail.html', context)


@login_required(login_url='/users/login/')
def search_materials(request):
    """
    Умный поиск материалов с использованием TF-IDF и машинного обучения.

    Args:
        request (HttpRequest): HTTP-запрос с GET-параметром 'q'

    Returns:
        HttpResponse: Страница с результатами поиска

    Context:
        materials (QuerySet): Найденные материалы с пагинацией
        query (str): Поисковый запрос
        total_results (int): Общее количество найденных материалов
        search_time (float): Время выполнения поиска в миллисекундах
        suggestions (list): Рекомендации по похожим запросам
    """
    # Получаем поисковый запрос из GET-параметров
    query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    context = {
        'query': query,
        'materials': [],
        'total_results': 0,
        'search_time': 0,
        'suggestions': []
    }

    if not query:
        return render(request, 'materials/search_results.html', context)

    start_time = time.time()

    try:
        # Получаем поисковый движок
        engine = get_search_engine()

        # Получаем все материалы с предварительной загрузкой связанных объектов
        # Используем select_related для оптимизации запросов к БД
        all_materials = list(Material.objects.select_related('subject').all())

        # Если материалов нет
        if not all_materials:
            messages.info(request, "В базе данных пока нет материалов для поиска.")
            return render(request, 'materials/search_results.html', context)

        # Если индекс не построен, строим его
        if not engine.is_built:
            engine.build_index(all_materials)
            # Сохраняем для будущих запросов
            engine.save_index()

        # Выполняем поиск
        results = engine.search(query, all_materials, top_k=50, min_score=0.05)

        # Извлекаем материалы из результатов
        materials_list = [r['material'] for r in results]

        # Добавляем информацию о релевантности в каждый материал
        for i, result in enumerate(results):
            # Добавляем атрибуты для отображения в шаблоне
            result['material'].relevance_score = result['score']
            result['material'].matched_terms = result['matched_terms']

        # Если результатов мало, генерируем предложения
        suggestions = []
        if len(materials_list) < 5:
            suggestions = generate_suggestions(query, all_materials)

        # Пагинация
        paginator = Paginator(materials_list, 12)  # 12 материалов на страницу
        page_materials = paginator.get_page(page_number)

        search_time = round((time.time() - start_time) * 1000, 2)  # в миллисекундах

        context.update({
            'materials': page_materials,
            'total_results': len(materials_list),
            'search_time': search_time,
            'suggestions': suggestions,
            'is_paginated': paginator.num_pages > 1,
            'page_obj': page_materials,
            'paginator': paginator,
        })

    except Exception as e:
        print(f"❌ Ошибка при поиске: {e}")
        messages.error(request, "Произошла ошибка при поиске. Пожалуйста, попробуйте позже.")

    return render(request, 'materials/search_results.html', context)


def generate_suggestions(query, all_materials, max_suggestions=5):
    """
    Генерирует предложения для похожих запросов на основе существующих материалов.

    Args:
        query (str): Исходный поисковый запрос
        all_materials (list): Список всех материалов
        max_suggestions (int): Максимальное количество предложений

    Returns:
        list: Список предложений для похожих запросов
    """
    suggestions = []
    words = query.lower().split()

    if not words:
        return suggestions

    # Собираем популярные термины из материалов
    term_frequency = {}

    for material in all_materials[:100]:  # Анализируем первые 100 материалов
        # Объединяем все текстовые поля
        text = f"{material.title} {material.description} {material.subject.name}".lower()

        # Ищем слова, похожие на слова из запроса
        for word in words:
            if len(word) > 3:  # Игнорируем короткие слова
                # Находим предложения, содержащие слово из запроса
                if word in text:
                    # Извлекаем контекст (слова вокруг)
                    parts = text.split()
                    for i, part in enumerate(parts):
                        if word in part:
                            # Добавляем биграммы
                            if i > 0:
                                bigram = f"{parts[i - 1]} {part}"
                                term_frequency[bigram] = term_frequency.get(bigram, 0) + 1
                            if i < len(parts) - 1:
                                bigram = f"{part} {parts[i + 1]}"
                                term_frequency[bigram] = term_frequency.get(bigram, 0) + 1

    # Сортируем по частоте и выбираем топ
    sorted_terms = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)
    suggestions = [term for term, freq in sorted_terms[:max_suggestions]]

    # Если нет предложений, добавляем общие варианты
    if not suggestions:
        common_suggestions = [
            f"{query} лекции",
            f"{query} практика",
            f"{query} учебник",
            "методические материалы",
            "лабораторные работы"
        ]
        suggestions = common_suggestions[:max_suggestions]

    return suggestions


def is_admin(user):
    """Проверка что пользователь администратор."""
    return user.is_superuser or user.is_staff


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
        6. Перестраиваем поисковый индекс
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

            # Перестраиваем поисковый индекс в фоне
            try:
                # Получаем движок и обновляем индекс
                engine = get_search_engine()
                all_materials = list(Material.objects.select_related('subject').all())
                engine.build_index(all_materials)
                engine.save_index()
                print(f"✅ Поисковый индекс обновлен после добавления материала")
            except Exception as e:
                print(f"⚠️ Ошибка при обновлении индекса: {e}")

            messages.success(request, f'✅ Материал "{title}" успешно добавлен в предмет "{subject.name}"!')
            return redirect('subject_materials', subject_id=subject.id)

        except Exception as e:
            messages.error(request, f'❌ Ошибка при добавлении материала: {str(e)}')
            return redirect('add_material')

    return render(request, 'materials/add_material.html', {
        'subjects': subjects,
        'material_types': Material.MATERIAL_TYPES,
        'title': 'Добавить материал',
    })


# Дополнительная функция для перестроения индекса (можно вызвать из management command)
def rebuild_search_index():
    """
    Принудительное перестроение поискового индекса.
    """
    engine = get_search_engine()
    all_materials = list(Material.objects.select_related('subject').all())

    if all_materials:
        success = engine.build_index(all_materials)
        if success:
            engine.save_index()
            print(f"✅ Индекс перестроен: {len(all_materials)} материалов")
            return True
        else:
            print("❌ Ошибка при перестроении индекса")
            return False
    else:
        print("ℹ Нет материалов для индексации")
        return False