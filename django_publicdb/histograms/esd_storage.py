""" Functions to get the locations of files in the ESD

"""
import os
import logging

import tables

from django.conf import settings


logger = logging.getLogger('histograms.esd_storage')


class ProcessedHisparcEvent(tables.IsDescription):
    timestamp = tables.Time32Col()
    nanoseconds = tables.UInt32Col()
    ext_timestamp = tables.UInt64Col()
    data_reduction = tables.BoolCol()
    baseline = tables.Int16Col(shape=4, dflt=-1)
    std_dev = tables.Int16Col(shape=4, dflt=-1)
    n_peaks = tables.Int16Col(shape=4, dflt=-1)
    pulseheights = tables.Int16Col(shape=4, dflt=-1)
    integrals = tables.Int32Col(shape=4, dflt=-1)
    t1 = tables.Float32Col(dflt=-1)
    t2 = tables.Float32Col(dflt=-1)
    t3 = tables.Float32Col(dflt=-1)
    t4 = tables.Float32Col(dflt=-1)
    n1 = tables.Float32Col(dflt=-1)
    n2 = tables.Float32Col(dflt=-1)
    n3 = tables.Float32Col(dflt=-1)
    n4 = tables.Float32Col(dflt=-1)


def get_esd_data_path(date):
    """Return path to ESD file

    Return path to the ESD file of a particular date

    :param date: the date as a datetime.date object

    :return: path to the ESD file

    """
    rootdir = settings.ESD_PATH
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')
    return os.path.join(rootdir, filepath)


def get_or_create_esd_data_path(date):
    """Return path to ESD file, creating directories if necessary

    :param date: datetime.date object

    :returns: path to ESD file

    """
    filepath = get_esd_data_path(date)
    dirpath, filename = os.path.split(filepath)

    if not os.path.exists(dirpath):
        # create dir and parent dirs with mode rwxr-xr-x
        os.makedirs(dirpath, 0755)

    return filepath


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
