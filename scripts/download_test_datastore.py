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

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import tables
import datetime

from sapphire.publicdb import download_data

from django.conf import settings
from django_publicdb.inforecords.models import Station


datastore_path = os.path.abspath(settings.DATASTORE_PATH)

START = datetime.date(2013, 1, 5)
END = datetime.date(2013, 1, 7)


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
        date += datetime.timedelta(days=1)


def download_and_store_data_for_date(date):
    f = get_datastore_file_for_date(date)
    for station in Station.objects.all():
        download_and_store_station_data(f, station, date)
    f.close()


def get_datastore_file_for_date(date):
    return open_or_create_file(datastore_path, date)


def download_and_store_station_data(f, station, date, get_blobs=True):
    start = datetime.datetime.combine(date, datetime.time(0, 0, 0))
    end = start + datetime.timedelta(days=1)

    cluster = station.cluster.main_cluster()
    station_group = get_or_create_station_group(f, cluster, station.number)

    download_data(f, station_group, station.number,
                  start, end,
                  get_blobs=get_blobs)


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

    return tables.open_file(file, 'a')


def get_or_create_cluster_group(file, cluster):
    """Get an existing cluster group or create a new one

    :param file: the PyTables data file
    :param cluster: the name of the cluster

    """
    try:
        hisparc = file.get_node('/', 'hisparc')
    except tables.NoSuchNodeError:
        hisparc = file.create_group('/', 'hisparc', 'HiSPARC data')
        file.flush()

    node_name = 'cluster_' + cluster.lower()
    try:
        cluster = file.get_node(hisparc, node_name)
    except tables.NoSuchNodeError:
        cluster = file.create_group(hisparc, node_name,
                                    'HiSPARC cluster %s data' % cluster)
        file.flush()

    return cluster


def get_or_create_station_group(file, cluster, station_number):
    """Get an existing station group or create a new one

    :param file: the PyTables data file
    :param cluster: the name of the cluster
    :param station_number: the station number

    """
    cluster = get_or_create_cluster_group(file, cluster)
    node_name = 'station_%d' % station_number
    try:
        station = file.get_node(cluster, node_name)
    except tables.NoSuchNodeError:
        station = file.create_group(cluster, node_name,
                                    'HiSPARC station %d data' % station_number)
        file.flush()

    return station


if __name__ == '__main__':
    main()
