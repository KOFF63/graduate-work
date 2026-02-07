import os
import codecs


# Исправление всех HTML и Python файлов в проекте
def fix_encoding_in_project():
    # Директории для исключения
    exclude_dirs = ['venv', '__pycache__', '.git', '.idea']

    # Расширения файлов для обработки
    extensions = ['.html', '.py', '.txt', '.md', '.css', '.js']

    # Проходим по всем файлам
    for root, dirs, files in os.walk('.'):
        # Пропускаем исключенные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            filepath = os.path.join(root, file)

            # Проверяем расширение
            if any(file.endswith(ext) for ext in extensions):
                try:
                    # Пробуем прочитать с разными кодировками
                    for encoding in ['utf-8-sig', 'utf-8', 'cp1251', 'windows-1251', 'latin-1']:
                        try:
                            with open(filepath, 'r', encoding=encoding) as f:
                                content = f.read()

                            # Сохраняем в UTF-8 без BOM
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)

                            print(f"✓ Исправлен: {filepath} (была {encoding})")
                            break

                        except UnicodeDecodeError:
                            continue
                        except Exception as e:
                            print(f"✗ Ошибка при чтении {filepath} с {encoding}: {e}")
                            continue

                except Exception as e:
                    print(f"✗ Ошибка с файлом {filepath}: {e}")


if __name__ == "__main__":
    print("Исправление кодировки файлов...")
    fix_encoding_in_project()
    print("\nГотово! Все файлы пересохранены в UTF-8 без BOM.")