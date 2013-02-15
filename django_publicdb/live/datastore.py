import os
import re
import datetime
from operator import itemgetter
import zlib

import tables

from django.conf import settings


def get_trace(cluster, station_id, iterator=2):
    """

    :param cluster: string containing the cluster name (slugged)
    :param station_id: station number
    :param iterator: row number (from the bottom) to get

    """

    path = get_data_path_today()
    file = get_datastore_file(path)
    node = get_station_node(file, cluster, station_id)
    event, trace = retrieve_event(node, iterator)
    file.close()
    return event, trace


def retrieve_event(node, iterator):
    """Get the event and trace

    :param node: handler for the node of a station
    :param iterator: row number (from the bottom) to get

    """
    event = node.events[-iterator];
    trace_idx = event['traces'];
    trace_str = [zlib.decompress(node.blobs[idx]).split(',') for idx in trace_idx]
    traces = [[int(val) for val in plate if val != ''] for plate in trace_str]
    return event, traces


def get_station_node(file, cluster, station_id):
    node = file.getNode('/hisparc/cluster_%s/station_%d' %
                        (cluster.lower(), station_id))
    return node


def get_datastore_file(path):
    """Get the datafile

    :param path: path to the desired datafile

    :return: handler for the data file

    """
    file = tables.openFile(path, 'r', NODE_CACHE_SLOTS=0)
    return file


def get_data_path_latest(station_id):
    """Get path to latest date with data for the given station

    :param station_id: station number

    """
    summary = (Summary.objects.filter(station__number=station_id,
                                      num_events__isnull=False,
                                      date__gte=datetime.date(2002, 1, 1),
                                      date__lte=datetime.date.today())
                              .latest('date'))
    date = summary.date
    return get_data_path(date)


def get_data_path_today():
    """Get path to todays datafile"""
    return get_data_path(datetime.date(2012, 12, 3))

    #return get_data_path(datetime.date.today())


def get_data_path(date):
    """Return path to data file

    Return path to the data file of a particular date

    :param date: the date

    :return: path to the data file

    """
    rootdir = settings.DATASTORE_PATH
    file = '%d_%d_%d.h5' % (date.year, date.month, date.day)
    return os.path.join(rootdir, str(date.year), str(date.month), file)
