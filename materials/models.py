from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название предмета')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, default='📚', verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Material(models.Model):
    MATERIAL_TYPES = [
        ('pdf', 'PDF документ'),
        ('video', 'Видео урок'),
        ('text', 'Текстовый материал'),
        ('presentation', 'Презентация'),
        ('link', 'Ссылка'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, verbose_name='Тип материала')
    file = models.FileField(upload_to='materials/', blank=True, null=True, verbose_name='Файл')
    external_link = models.URLField(blank=True, verbose_name='Ссылка на внешний ресурс')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    tags = models.CharField(max_length=200, blank=True, verbose_name='Теги (через запятую)')

    def __str__(self):
        return self.title

    # ДОБАВЛЯЕМ МЕТОД ДЛЯ ПОИСКА - ВСТАВЬ ЭТОТ КОД В КЛАСС Material
    @classmethod
    def search(cls, query):
        """Поиск материалов по названию, описанию и тегам"""
        from django.db.models import Q
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(subject__name__icontains=query)
        )

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['-upload_date']