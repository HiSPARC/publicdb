import datetime


def daterange(start, stop):
    """Generator for date ranges

    This is a generator for date ranges. Based on a start and stop value,
    it generates one day intervals.

    :param start: a date instance, end of range
    :param stop: a date instance, end of range
    :yield date: dates with one day interval between start and stop

    """
    if start == stop:
        yield start
        return
    else:
        yield start
        cur = start
        while cur < stop:
            cur += datetime.timedelta(days=1)
            yield cur
        return


def single_day_ranges(start, end):
    """Generate datetime ranges consisting of a single day.

    Generate datetime ranges, a single day at a time.  The generator keeps
    returning two datetime values, making up a range of a full day.
    However, the first and last days may be shorter, if a specific
    time-of-day was specified.

    :param start: a datetime instance, start of range
    :param end: a datetime instance, end of range
    :yield cur,next: date intervals between start and stop

    """
    cur = start
    next_day = cur.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    while next_day < end:
        yield cur, next_day
        cur = next_day
        next_day = cur + datetime.timedelta(days=1)
    yield cur, end
