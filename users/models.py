"""
Модели для приложения пользователей.

Содержит модель UserProfile для хранения дополнительной информации о пользователях.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Профиль пользователя с дополнительной информацией.

    Расширяет стандартную модель User Django дополнительными полями.

    Attributes:
        user (User): Связь с моделью пользователя Django
        display_name (CharField): Отображаемое имя пользователя
        avatar (ImageField): Аватар пользователя
        bio (TextField): Информация о пользователе
        role (CharField): Роль (студент/преподаватель)
        department (CharField): Факультет или кафедра
        created_at (DateTimeField): Дата создания профиля
    """

    # Выбор ролей для пользователя
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('other', 'Другое'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='userprofile'
    )

    # НОВОЕ ПОЛЕ: Отображаемое имя
    display_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Отображаемое имя',
        help_text='Имя которое будут видеть другие пользователи (можно оставить пустым)'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Загрузите изображение для аватара'
    )

    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='О себе',
        help_text='Расскажите немного о себе'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='Роль',
        help_text='Выберите вашу роль в системе'
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Факультет/кафедра',
        help_text='Укажите ваш факультет или кафедру'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )

    def __str__(self):
        """Строковое представление профиля."""
        display = self.display_name if self.display_name else self.user.username
        return f'{display} ({self.get_role_display()})'

    def get_display_name(self):
        """
        Возвращает отображаемое имя.

        Returns:
            str: Отображаемое имя если задано, иначе username
        """
        return self.display_name if self.display_name else self.user.username

    def get_avatar_url(self):
        """Возвращает URL аватара или URL заглушки если аватара нет."""
        if self.avatar:
            return self.avatar.url
        return '/static/materials/images/default_avatar.png'

    class Meta:
        """Метаданные модели."""
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['-created_at']


# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Создает профиль пользователя при создании нового пользователя.

    Args:
        sender: Модель отправителя (User)
        instance: Созданный экземпляр пользователя
        created (bool): Флаг создания нового объекта
        **kwargs: Дополнительные аргументы
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сохраняет профиль пользователя при сохранении пользователя.

    Args:
        sender: Модель отправителя (User)
        instance: Экземпляр пользователя
        **kwargs: Дополнительные аргументы
    """
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Если профиль не существует, создаем его
        UserProfile.objects.create(user=instance)