from django import template

register = template.Library()


@register.filter
def fix_histogram_data(value):
    """Append one value to end of data, to fix step histogram"""

    return value + [[value[-1][0] + (value[-1][0] - value[-2][0]),
                     value[-1][1]]]
