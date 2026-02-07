from django import template

register = template.Library()

@register.filter
def test_filter(value):
    return str(value) + " - ????"
