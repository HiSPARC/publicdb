import datetime


def daterange(start, stop):
    """Generator for date ranges

    This is a generator for date ranges. Based on a start and stop value,
    it generates one day intervals.

    :param start: a date instance
    :param stop: a date instance

    :yield date: one day intervals between start and stop
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
