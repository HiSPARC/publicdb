import calendar
import os

from datetime import datetime, timedelta

import numpy

from django.conf import settings

from sapphire.transformations import clock


def discharges(datafile, start, end, type=4):
    """Get discharge information for discharges of certain type

    :param file: the date as a datetime.date object
    :param start: start of timestamp range
    :param end: end of timestamp range
    :param type: the type of detected event (default: 4, cloud-ground)
        0 = single-point,
        1 = start of CC,
        2 = CC discharge,
        3 = end of CC,
        4 = CG stroke,
        5 = CG return stroke.
    :return: iterator giving a dictionary with the GPS time, location,
             and current of the discharges of the chosen type.

    """
    discharge_table = datafile.get_node('/discharge1')
    reference_date = get_reference_datetime(datafile)

    cg_idx = numpy.where(discharge_table.event_type[:] == type)

    for idx in cg_idx[0]:
        ts, ns = get_gps_timestamp(reference_date, discharge_table.time_offset[idx])
        if start <= ts < end:
            yield {'timestamp': ts,
                   'nanoseconds': ns,
                   'latitude': discharge_table.latitude[idx],
                   'longitude': discharge_table.longitude[idx],
                   'current': discharge_table.current[idx]}


def data_path(date):
    """Return path to KNMI LGT file

    Return path to the KNMI LGT file of a particular date. Note that 1
    day is added to the file name, because KNMI names the files for the
    end date of the data.

    :param date: the date as a datetime.date object

    :return: path to the KNMI LGT file

    """
    rootdir = settings.LGT_PATH
    date += timedelta(days=1)
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')

    return os.path.join(rootdir, filepath)


def get_gps_timestamp(reference_date, time_offset):
    """Convert time_offsets to gps timestamps and nanoseconds

    :param reference_date: datetime object of the reference datetime
    :param time_offset: time offset of the discharge in fractional seconds

    :return: timestamp and nanosecond in GPS time

    """
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


def get_absolute_datetime(reference_date, time_offset):
    """Get the absolute time of the discharges

    :param reference_date: datetime object of the reference datetime
    :param time_offset: time offset of the discharge in fractional seconds

    :return: datetime object for the offset time in absolute datetime

    """
    absolute_datetime = reference_date + timedelta(seconds=time_offset)

    return absolute_datetime


def get_reference_datetime(datafile):
    """Get the reference datetime from the KNMI LGT file as datetime

    :param datafile: KNMI LGT file object

    :return: datetime object of the reference datetime

    """
    date_string = datafile.root.discharge1._f_getattr('reference_datetime')[0]
    ref_date = datetime.strptime(date_string, '%d-%b-%Y;%H:%M:%S.%f')

    return ref_date
