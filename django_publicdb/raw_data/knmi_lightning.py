import csv
import os
from datetime import date, timedelta

import tables
import numpy as np

from date_generator import daterange
from knmi_timestamps import get_gps_timestamp


# functie van deze gebruiken voor download formulier

LGT_PATH = "/Users/arne/Datastore/Lightning/"


def discharges(datafile, type=4):
    """Get discharge information for discharges of certain type

    :param file: the date as a datetime.date object
    :param type: the type of detected event (default: 4, cloud-ground)

    :return: arrays time_offset, latitude, longitude for events of chosen type

    """
    # FIXME: Might be a discharge2, check this.
    discharge_table = datafile.get_node('/discharge1')
    cg_idx = np.where(discharge_table.event_type[:] == type)

    discharges = ((get_gps_timestamp(datafile, discharge_table.time_offset[idx])[0],
                   get_gps_timestamp(datafile, discharge_table.time_offset[idx])[1],
                   discharge_table.latitude[idx],
                   discharge_table.longitude[idx],
                   discharge_table.current[idx])
                  for idx in cg_idx[0])

    return discharges


def data_file(date):
    """Return PyTables data file

    :param date: the date as a datetime.date object

    :return: PyTables instance of the data file

    """
    filepath = data_path(date)
    try:
        datafile = tables.open_file(filepath, 'r')
        return datafile
    except IOError:
        print "No datefile for %s." % date.strftime('%Y_%-m_%-d')
        raise


def data_path(date):
    """Return path to KNMI LGT file

    Return path to the KNMI LGT file of a particular date
    Note that 1 day is added to the file name, because KNMI names the files
    for the end date of the data.

    :param date: the date as a datetime.date object

    :return: path to the KNMI LGT file

    """
    rootdir = LGT_PATH
    date += timedelta(days=1)
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')

    return os.path.join(rootdir, filepath)


def data_to_csv():
    with open(LGT_PATH + 'robert_2006.csv','w') as output:
        csvwriter = csv.writer(output, delimiter='\t')
        csvwriter.writerow(['timestamp', 'nanoseconds', 'latitude',
                            'longitude', 'current'])

        for d in daterange(date(2005, 12, 31), date(2006, 12, 31)):
            try:
                data = data_file(d)
                for discharge in discharges(data):
                    csvwriter.writerow(discharge)
            except:
                continue
            else:
                data.close()

if __name__ == '__main__':
    data_to_csv()
