from django import template

register = template.Library()


@register.filter
def fix_histogram_data(value):
    """Append one value to end of data, to fix step histogram"""

    return value + [[value[-1][0] + (value[-1][0] - value[-2][0]), value[-1][1]]]


@register.filter
def fix_timestamps_in_data(values):
    """Convert timestamps to hour of day"""

    x, y = zip(*values)
    seconds_in_day = [u % 86400 for u in x]
    hours_in_day = [u / 3600. for u in seconds_in_day]
    values = [list(u) for u in zip(hours_in_day, y)]
    return values


@register.filter
def slice_data(values, arg):
    """Get every nth value from the list"""

    return values[::arg]


@register.filter
def round_data(values, arg):
    """Round every value to nth decimal place"""

    return [[round(x, arg), round(y, arg)] for x, y, in values]


@register.filter
def real_temperature(values):
    """Only allow physically possible temperatures"""

    return [[x, y] for x, y in values if -273 < y]
