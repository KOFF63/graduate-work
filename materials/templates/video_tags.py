import re
from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()


@register.filter
def is_rutube_video(url):
    """Определяет, является ли ссылка RuTube видео"""
    if not url:
        return False

    rutube_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?rutube\.ru\/video\/([a-f0-9]{32})\/?',
        r'(?:https?:\/\/)?(?:www\.)?rutube\.ru\/play\/embed\/([a-f0-9]{32})',
        r'(?:https?:\/\/)?(?:www\.)?rutube\.ru\/video\/embed\/([a-f0-9]{32})',
    ]

    for pattern in rutube_patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)

    return False


@register.filter
def get_rutube_embed_url(url):
    """Получает embed-ссылку для RuTube"""
    video_id = is_rutube_video(url)
    if video_id:
        return f"https://rutube.ru/play/embed/{video_id}"
    return url


@register.filter
def is_video_file(url):
    """Определяет, является ли ссылка видео файлом"""
    if not url:
        return False

    video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.wmv', '.flv', '.mkv']
    return any(url.lower().endswith(ext) for ext in video_extensions)


@register.filter
def get_video_type(url):
    """Определяет тип видео"""
    if is_rutube_video(url):
        return 'rutube'
    elif is_video_file(url):
        return 'file'
    else:
        return 'other'