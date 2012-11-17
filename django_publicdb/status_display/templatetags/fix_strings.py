from django import template

register = template.Library()


@register.filter
def remove_hyphens(value):
    """Remove hyphens from string"""

    return value.replace("-", "")
