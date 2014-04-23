from django import template

import datetime
import calendar

register = template.Library()


@register.filter
def fix_histogram_data(value):
    """Append one value to end of data, to fix step histogram"""

    return value + [[value[-1][0] + (value[-1][0] - value[-2][0]), value[-1][1]]]


@register.filter
def fix_histogram_time(value):
    """Extend last known value to the current date"""

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    timestamp = calendar.timegm(tomorrow.timetuple())

    return value + [[timestamp, value[-1][1]]]


@register.filter
def fix_timestamps(values):
    """Convert timestamps to milliseconds"""

    return [[x * 1000, y] for x, y in values]


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
    """Get every nth value from the list

    Note: This only slices data if the data has at least 1000 elements.
    This to prevent the new shrunken datasets (~576 long) to be sliced.

    """
    if len(values) > 1000:
        return values[::arg]
    else:
        return values


@register.filter
def round_data(values, arg):
    """Round every value to nth decimal place"""

    return [[round(x, arg), round(y, arg)] for x, y in values]


@register.filter
def shift_bins(values, arg):
    """Shift bins edges by arg"""

    values = [[x + arg, y] for x, y in values]

    return values
