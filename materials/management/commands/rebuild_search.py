from django.core.management.base import BaseCommand
from materials.models import Material
from materials.search_engine import SmartSearchEngine


class Command(BaseCommand):
    help = 'Перестраивает поисковый TF-IDF индекс'

    def add_arguments(self, parser):
        parser.add_argument(
            '--save',
            action='store_true',
            help='Сохранить индекс на диск',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Перестроение поискового индекса...")

        # Получаем все материалы
        materials = list(Material.objects.select_related('subject').all())
        self.stdout.write(f"Найдено материалов: {len(materials)}")

        if not materials:
            self.stdout.write(self.style.WARNING("Нет материалов для индексации"))
            return

        # Создаем и строим индекс
        engine = SmartSearchEngine()
        success = engine.build_index(materials)

        if success:
            self.stdout.write(self.style.SUCCESS(f"✓ Индекс успешно построен"))
            self.stdout.write(f"  - Документов: {len(engine.document_ids)}")
            self.stdout.write(f"  - Признаков: {engine.tfidf_matrix.shape[1]}")

            if options['save']:
                if engine.save_index():
                    self.stdout.write(self.style.SUCCESS("✓ Индекс сохранен на диск"))
                else:
                    self.stdout.write(self.style.ERROR("✗ Ошибка при сохранении индекса"))
        else:
            self.stdout.write(self.style.ERROR("✗ Ошибка при построении индекса"))