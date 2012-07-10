from django import template

register = template.Library()


@register.filter
def fix_histogram_data(value):
    """append one value to end of data, to fix histogram"""

    return value + [[value[-1][0] + (value[-1][0] - value[-2][0]), value[-1][1]]]

@register.filter
def fix_timestamps_in_data(values):
    x, y = zip(*values)
    seconds_in_day = [u % 86400 for u in x]
    hours_in_day = [u / 3600. for u in seconds_in_day]
    values = [list(u) for u in zip(hours_in_day, y)]
    return values

@register.filter
def slice_data(values, arg):
    return values[::arg]
