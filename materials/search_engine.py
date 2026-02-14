"""
Поисковый движок с использованием машинного обучения.
Использует TF-IDF векторизацию и косинусное сходство для умного поиска.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import os
import pickle
from django.conf import settings

# Загрузка необходимых данных NLTK при первом импорте
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

from nltk.corpus import stopwords

# Стоп-слова для русского и английского
try:
    RUSSIAN_STOP_WORDS = set(stopwords.words('russian'))
except:
    RUSSIAN_STOP_WORDS = set(
        ['и', 'в', 'на', 'с', 'по', 'для', 'а', 'но', 'или', 'из', 'за', 'к', 'у', 'о', 'об', 'от', 'до'])

try:
    ENGLISH_STOP_WORDS = set(stopwords.words('english'))
except:
    ENGLISH_STOP_WORDS = set(['the', 'and', 'for', 'with', 'from', 'this', 'that'])

# Объединяем стоп-слова
STOP_WORDS = list(RUSSIAN_STOP_WORDS | ENGLISH_STOP_WORDS)


class SmartSearchEngine:
    """
    Умный поисковый движок на основе TF-IDF.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words=STOP_WORDS,
            ngram_range=(1, 3),  # Учитываем фразы из 1-3 слов
            analyzer='word',
            lowercase=True,
            min_df=1,  # Минимальная частота документа
            max_df=0.8  # Игнорируем слишком частые слова
        )
        self.tfidf_matrix = None
        self.documents = []
        self.document_ids = []
        self.is_built = False

    def prepare_documents(self, materials):
        """
        Подготовка документов для индексации.
        Объединяет название, описание, теги и название предмета.
        """
        documents = []
        for material in materials:
            # Создаем текст для поиска из всех полей с весами
            # Повторяем важные поля для увеличения их веса
            title_text = f"{material.title} " * 3  # Утроенный вес для названия
            subject_text = f"{material.subject.name} " * 2  # Двойной вес для предмета

            text = f"""
            {title_text}
            {material.description} 
            {material.tags or ''} 
            {subject_text}
            {material.get_material_type_display()}
            """.lower()
            documents.append(text)

        return documents

    def build_index(self, materials):
        """
        Построение TF-IDF индекса.
        """
        if not materials:
            print("Нет материалов для индексации")
            return False

        self.documents = self.prepare_documents(materials)
        self.document_ids = [m.id for m in materials]

        try:
            # Создаем TF-IDF матрицу
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            self.is_built = True
            print(f"✓ Индекс построен: {len(self.document_ids)} документов, {self.tfidf_matrix.shape[1]} признаков")
            return True
        except Exception as e:
            print(f"✗ Ошибка при построении индекса: {e}")
            return False

    def search(self, query, materials, top_k=20, min_score=0.1):
        """
        Поиск по запросу с ранжированием по релевантности.

        Args:
            query (str): Поисковый запрос
            materials (list): Список всех материалов
            top_k (int): Максимальное количество результатов
            min_score (float): Минимальный порог релевантности

        Returns:
            list: Список словарей с материалами и их оценками релевантности
        """
        if not self.is_built:
            if not self.build_index(materials):
                return []

        if not query.strip():
            return []

        try:
            # Преобразуем запрос в вектор
            query_vector = self.vectorizer.transform([query.lower()])

            # Вычисляем косинусное сходство
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

            # Получаем индексы с оценкой выше порога
            relevant_indices = np.where(similarities > min_score)[0]

            # Сортируем по убыванию релевантности
            sorted_indices = relevant_indices[np.argsort(-similarities[relevant_indices])]

            results = []
            for idx in sorted_indices[:top_k]:
                if idx < len(self.document_ids):
                    material_id = self.document_ids[idx]
                    material = next((m for m in materials if m.id == material_id), None)
                    if material:
                        results.append({
                            'material': material,
                            'score': round(float(similarities[idx]) * 100, 2),  # в процентах
                            'matched_terms': self.get_matched_terms(query, self.documents[idx])
                        })

            return results

        except Exception as e:
            print(f"✗ Ошибка при поиске: {e}")
            return []

    def get_matched_terms(self, query, document):
        """
        Находит совпадающие термины в документе.
        """
        query_words = set(query.lower().split())
        doc_words = set(document.split())
        matched = list(query_words & doc_words)
        return matched[:5]  # Возвращаем не больше 5 совпадений

    def save_index(self, path='search_index.pkl'):
        """
        Сохраняет индекс на диск.
        """
        if not self.is_built:
            print("Индекс не построен, сохранять нечего")
            return False

        try:
            with open(path, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'tfidf_matrix': self.tfidf_matrix,
                    'document_ids': self.document_ids,
                    'documents': self.documents,
                    'is_built': self.is_built
                }, f)
            print(f"✓ Индекс сохранен в {path}")
            return True
        except Exception as e:
            print(f"✗ Ошибка при сохранении индекса: {e}")
            return False

    def load_index(self, path='search_index.pkl'):
        """
        Загружает индекс с диска.
        """
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectorizer = data['vectorizer']
                    self.tfidf_matrix = data['tfidf_matrix']
                    self.document_ids = data['document_ids']
                    self.documents = data['documents']
                    self.is_built = data.get('is_built', True)
                print(f"✓ Индекс загружен из {path}")
                return True
            except Exception as e:
                print(f"✗ Ошибка при загрузке индекса: {e}")
        return False