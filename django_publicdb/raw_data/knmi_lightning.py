import os
from datetime import date, timedelta

# import tables
import numpy as np

from knmi_timestamps import get_gps_timestamp

from django.conf import settings

# functie van deze gebruiken voor download formulier


def discharges(datafile, start, end, type=4):
    """Get discharge information for discharges of certain type

    :param file: the date as a datetime.date object
    :param start: start of timestamp range
    :param end: end of timestamp range
    :param type: the type of detected event (default: 4, cloud-ground)
        o = single-point,
        1 = start of CC,
        2 = CC discharge,
        3 = end of CC,
        4 = CG stroke,
        5 = CG return stroke.
    :return: arrays time_offset, latitude, longitude for events of chosen type

    """
    discharge_table = datafile.get_node('/discharge1')
    cg_idx = np.where(discharge_table.event_type[:] == type)

    discharges = ({'timestamp': get_gps_timestamp(datafile, discharge_table.time_offset[idx])[0],
                   'nanoseconds': get_gps_timestamp(datafile, discharge_table.time_offset[idx])[1],
                   'latitude': discharge_table.latitude[idx],
                   'longitude': discharge_table.longitude[idx],
                   'current': discharge_table.current[idx]}
                  for idx in cg_idx[0]
                  if start <= get_gps_timestamp(datafile, discharge_table.time_offset[idx])[0] < end)

    return discharges


# def data_file(date):
#     """Return PyTables data file
#
#     :param date: the date as a datetime.date object
#
#     :return: PyTables instance of the data file
#
#     """
#     filepath = data_path(date)
#     try:
#         datafile = tables.open_file(filepath, 'r')
#         return datafile
#     except IOError:
#         print "No datefile for %s." % date.strftime('%Y_%-m_%-d')
#         raise
#

def data_path(date):
    """Return path to KNMI LGT file

    Return path to the KNMI LGT file of a particular date
    Note that 1 day is added to the file name, because KNMI names the files
    for the end date of the data.

    :param date: the date as a datetime.date object

    :return: path to the KNMI LGT file

    """
    rootdir = settings.LGT_PATH
    date += timedelta(days=1)
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')

    return os.path.join(rootdir, filepath)
