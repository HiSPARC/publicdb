""" Download and build a datastore for testing

    Load a few days worth of raw station data to build a tiny datastore.
    This is useful to get a test public database up and running.

    It is important that the script is run from inside the Django
    application folder (the one containing the settings.py).  You'll get a
    warning if the datastore directory cannot be found.

    (Actually, it can be run from any directory at the same level as the
    one containing the settings.py.  Don't worry about it.)

"""

import os
import sys

sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import tables
from datetime import date, datetime, time, timedelta

from sapphire.publicdb import download_data

from django.conf import settings
from django_publicdb.inforecords.models import *


datastore_path = os.path.abspath(settings.DATASTORE_PATH)

START = date(2013, 1, 5)
END = date(2013, 1, 6)


def main():
    test_for_datastore_directory()
    fill_datastore()


def test_for_datastore_directory():
    print "Checking for datastore path at %s ..." % datastore_path,
    if not os.path.exists(datastore_path):
        raise RuntimeError("Datastore path cannot be found!")
    else:
        print "Found."


def fill_datastore():
    for date in generate_date_range(START, END):
        download_and_store_data_for_date(date)


def generate_date_range(start, end):
    date = start
    while date <= end:
        yield date
        date += timedelta(days=1)


def download_and_store_data_for_date(date):
    f = get_datastore_file_for_date(date)
    for station in Station.objects.all():
        download_and_store_station_data(f, station, date)
    f.close()


def get_datastore_file_for_date(date):
    return open_or_create_file(datastore_path, date)


def download_and_store_station_data(f, station, date):
    start = datetime.combine(date, time(0, 0, 0))
    end = start + timedelta(days=1)

    cluster = station.cluster.main_cluster()
    station_group = get_or_create_station_group(f, cluster, station.number)

    download_data(f, station_group, station.number, start, end, get_blobs=True)


def open_or_create_file(data_dir, date):
    """Open an existing file or create a new one

    This function opens an existing PyTables file according to the event
    date.  If the file does not yet exist, a new one is created.

    :param data_dir: the directory containing all data files
    :param date: the event date

    """
    dir = os.path.join(data_dir, date.strftime('%Y/%-m'))
    file = os.path.join(dir, date.strftime('%Y_%-m_%-d.h5'))

    if not os.path.exists(dir):
        # create dir and parent dirs with mode rwxr-xr-x
        os.makedirs(dir, 0755)

    return tables.openFile(file, 'a')


def get_or_create_cluster_group(file, cluster):
    """Get an existing cluster group or create a new one

    :param file: the PyTables data file
    :param cluster: the name of the cluster

    """
    try:
        hisparc = file.getNode('/', 'hisparc')
    except tables.NoSuchNodeError:
        hisparc = file.createGroup('/', 'hisparc', 'HiSPARC data')
        file.flush()

    node_name = 'cluster_' + cluster.lower()
    try:
        cluster = file.getNode(hisparc, node_name)
    except tables.NoSuchNodeError:
        cluster = file.createGroup(hisparc, node_name,
                                   'HiSPARC cluster %s data' % cluster)
        file.flush()

    return cluster


def get_or_create_station_group(file, cluster, station_id):
    """Get an existing station group or create a new one

    :param file: the PyTables data file
    :param cluster: the name of the cluster
    :param station_id: the station number

    """
    cluster = get_or_create_cluster_group(file, cluster)
    node_name = 'station_%d' % station_id
    try:
        station = file.getNode(cluster, node_name)
    except tables.NoSuchNodeError:
        station = file.createGroup(cluster, node_name,
                                   'HiSPARC station %d data' % station_id)
        file.flush()

    return station


if __name__ == '__main__':
    main()
