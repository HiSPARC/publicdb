import calendar
import datetime

from django import template

register = template.Library()


@register.filter
def fix_histogram_data(value):
    """Append one value to end of data, to fix step histogram"""

    if len(value) > 1:
        return value + [[value[-1][0] + (value[-1][0] - value[-2][0]), value[-1][1]]]
    else:
        return value


@register.filter
def fix_histogram_time(value):
    """Extend last known value to the current date"""

    if not len(value):
        return value

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

    x, y = list(zip(*values))
    seconds_in_day = [timestamp % 86400 for timestamp in x]
    hours_in_day = [seconds // 3600.0 for seconds in seconds_in_day]
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


@register.filter
def none_to_nan(value):
    """Print nan instead of nothing for None values"""

    if value is None:
        return 'nan'
    else:
        return value


@register.filter
def mv_to_adc(value):
    """Convert mv_to_adc

    Old DAQ HiSPARC II+III => ADC = mV/-0.57 + 200
    New DAQ HiSPARC III => ADC = mV/-0.584 + 30

    Old versions of the DAQ report thresholds in mV. For both
    HiSPARC II and III the baseline is 200 with the old DAQ.

    Newer versions of the DAQ the bundled hisparc-monitor
    converts the threshold to ADC before uploading the configuration
    to the public database using the appropriate transformation.

    If value < 0: Assume mV and convert to ADC assume baseline 200.
    """

    if value > 0:
        if int(value) == value:
            return int(value)
        else:
            return value
    else:
        return int(round(value / -0.57 + 200))
