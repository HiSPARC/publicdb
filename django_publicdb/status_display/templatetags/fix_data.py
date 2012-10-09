from django import template

register = template.Library()


@register.filter
def fix_histogram_data(values):
    """Append one value to end of data, to fix step histogram"""

    return values + [[values[-1][0] + (values[-1][0] - values[-2][0]),
                      values[-1][1]]]


@register.filter
def fix_timestamps_in_data(values):
    """Convert timestamps to hour of day"""

    return [[x % 86400 / 3600., y] for x, y in values]


@register.filter
def slice_data(values, arg):
    """Get every nth value from the list"""

    return values[::arg]


@register.filter
def round_data(values, arg):
    """Round every value to nth decimal place"""

    return [[round(x, arg), round(y, arg)] for x, y in values]


@register.filter
def real_temperature(values):
    """Only allow physically possible temperatures"""

    return [[x, y] for x, y in values if -273 < y]


@register.filter
def fix_hour(values):
    """Offset hours by half an hour"""

    return [[x - 0.5, y] for x, y in values]


@register.filter
def divide_data(values, arg):
    """Offset hours by half an hour"""

    return [[x, y / arg] for x, y in values]


@register.filter
def real_pressure(values):
    """Only allow physically possible pressures"""

    return [[x, y] for x, y in values if y > 0]
