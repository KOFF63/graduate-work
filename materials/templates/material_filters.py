from django import template

register = template.Library()

@register.filter
def sum_values(dictionary):
    """Суммирует значения словаря."""
    return sum(dictionary.values()) if dictionary else 0

@register.filter
def get_item(dictionary, key):
    """Получает значение из словаря по ключу."""
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0