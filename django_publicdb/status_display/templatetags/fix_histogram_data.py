from django import template

register = template.Library()


@register.filter
def fix_histogram_data(value):
    """append one value to end of data, to fix histogram"""

    return value + [value[-1]]
