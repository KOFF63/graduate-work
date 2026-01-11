"""
Views (контроллеры) для приложения пользователей.

Обрабатывают регистрацию, вход, выход и управление профилями пользователей.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from materials.models import Material


def register_view(request):
    """
    Обработчик страницы регистрации нового пользователя.

    Args:
        request (HttpRequest): HTTP-запрос от пользователя

    Returns:
        HttpResponse: Страница регистрации или перенаправление на профиль
    """
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        display_name = request.POST.get('display_name', '').strip()
        role = request.POST.get('role', 'student')
        department = request.POST.get('department', '').strip()

        # Валидация данных
        if not username:
            messages.error(request, 'Имя пользователя обязательно.')
            return redirect('register')

        if not password1:
            messages.error(request, 'Пароль обязателен.')
            return redirect('register')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return redirect('register')

        # Проверяем не существует ли уже пользователь
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return redirect('register')

        try:
            # Создаем пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            # Получаем профиль пользователя
            profile = user.userprofile

            # Обновляем поля профиля
            profile.display_name = display_name
            profile.role = role
            profile.department = department
            profile.save()

            # Авторизуем пользователя
            login(request, user)

            messages.success(request, f'Добро пожаловать, {display_name or username}! Регистрация прошла успешно.')
            return redirect('profile')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return redirect('register')

    # GET запрос - отображаем форму регистрации
    return render(request, 'users/register.html')


def login_view(request):
    """
    Обработчик страницы входа в систему.

    Args:
        request (HttpRequest): HTTP-запрос

    Returns:
        HttpResponse: Страница входа или перенаправление на главную
    """
    if request.method == 'POST':
        # Получаем данные для входа
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Успешный вход
            login(request, user)

            # Используем отображаемое имя если есть
            display_name = user.userprofile.get_display_name()
            messages.success(request, f'Добро пожаловать, {display_name}!')

            # Перенаправляем на главную страницу
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # Неудачный вход
            messages.error(request, 'Неверное имя пользователя или пароль.')

    # Отображаем страницу входа
    return render(request, 'users/login.html')


def logout_view(request):
    """
    Обработчик выхода из системы.

    Args:
        request (HttpRequest): HTTP-запрос

    Returns:
        HttpResponseRedirect: Перенаправление на главную страницу
    """
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')


@login_required
def profile_view(request):
    """
    Обработчик страницы профиля пользователя.

    Доступна только для авторизованных пользователей.

    Args:
        request (HttpRequest): HTTP-запрос от авторизованного пользователя

    Returns:
        HttpResponse: Страница профиля пользователя
    """
    user = request.user

    # Получаем материалы загруженные пользователем
    user_materials = Material.objects.filter(
        uploaded_by=user
    ).order_by('-upload_date')

    # Обработка формы редактирования профиля
    if request.method == 'POST':
        try:
            # Получаем профиль пользователя
            profile = user.userprofile

            # Получаем данные из формы
            display_name = request.POST.get('display_name', '').strip()
            bio = request.POST.get('bio', '').strip()
            role = request.POST.get('role', 'student')
            department = request.POST.get('department', '').strip()
            email = request.POST.get('email', '').strip()

            # Обрабатываем загруженный аватар
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']

                # Проверяем тип файла (только изображения)
                if avatar_file.content_type.startswith('image/'):
                    profile.avatar = avatar_file
                else:
                    messages.warning(request, 'Можно загружать только изображения.')

            # Обрабатываем удаление аватара
            if request.POST.get('remove_avatar') == 'on':
                if profile.avatar:
                    profile.avatar.delete(save=False)
                    profile.avatar = None

            # Обновляем email пользователя
            if email and email != user.email:
                user.email = email
                user.save()

            # Обновляем поля профиля
            profile.display_name = display_name
            profile.bio = bio
            profile.role = role
            profile.department = department
            profile.save()

            messages.success(request, 'Профиль успешно обновлен!')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

        # Перенаправляем на ту же страницу
        return redirect('profile')

    # Подготавливаем контекст для шаблона
    context = {
        'user_materials': user_materials,
        'materials_count': user_materials.count(),
    }

    return render(request, 'users/profile.html', context)