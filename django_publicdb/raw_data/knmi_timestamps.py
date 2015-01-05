import datetime
import calendar

import tables

from sapphire.transformations import clock


def get_gps_timestamp(file, time_offset):
    """Convert time_offsets to gps timestamps and nanoseconds

    """
    reference_date = get_reference_datetime(file)
    absolute_date = get_absolute_datetime(reference_date, time_offset)
    timestamp, nanosecond = datetime_to_gpstimestamp_nanoseconds(absolute_date)

    return timestamp, nanosecond


def datetime_to_gpstimestamp_nanoseconds(date):
    """Convert datetime objects to GPS timestamp and nanoseconds

    :param date: datetime object of the absolute datetime

    :return: GPS time as timestamp in seconds
             microsecond part of the datetime as nanoseconds

    """
    timestamp = clock.utc_to_gps(calendar.timegm(date.utctimetuple()))
    nanosecond = date.microsecond * 1000

    return timestamp, nanosecond


def get_absolute_datetime(reference, offset):
    """Get the absolute time of the discharges

    :param reference: datetime object of the reference datetime
    :param offset: time offset of the discharge in fractional seconds

    :return: list of datetime objects of the absolute datetime

    """
    absolute_datetime = reference + datetime.timedelta(seconds=offset)

    return absolute_datetime


def get_reference_datetime(file):
    """Get the reference datetime from the KNMI LGT file as datetime

    :param file: KNMI LGT file object

    :return: datetime object of the reference datetime

    """
    date_string = file.root.discharge1._f_getAttr('reference_datetime')[0]
    ref_date = datetime.datetime.strptime(date_string, '%d-%b-%Y;%H:%M:%S.%f')

    return ref_date
