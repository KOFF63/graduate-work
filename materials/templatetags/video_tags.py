import re
from django import template

register = template.Library()

@register.filter
def is_rutube_video(url):
    # Check if URL is RuTube video
    if not url:
        return False
    
    # Simple check for rutube
    return 'rutube.ru' in url.lower()

@register.filter
def get_rutube_embed_url(url):
    # Get embed URL for RuTube
    if not url:
        return ''
    
    if 'rutube.ru' in url.lower():
        # Try to extract video ID
        patterns = [
            r'/video/([a-f0-9]{32})',
            r'/play/embed/([a-f0-9]{32})',
            r'/video/embed/([a-f0-9]{32})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return f'https://rutube.ru/play/embed/{video_id}'
        
        # If no ID found, return original URL
        return url
    
    return url

@register.filter
def is_video_file(url):
    # Check if URL is video file
    if not url:
        return False
    
    video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.wmv', '.flv', '.mkv']
    url_lower = url.lower()
    return any(url_lower.endswith(ext) for ext in video_extensions)

@register.filter
def get_video_type(url):
    # Determine video type
    if not url:
        return 'other'
    
    if 'rutube.ru' in url.lower():
        return 'rutube'
    elif is_video_file(url):
        return 'file'
    else:
        return 'other'
