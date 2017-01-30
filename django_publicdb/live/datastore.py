import os
import re
import datetime
from operator import itemgetter
import zlib

import tables

from django.conf import settings


def get_event(cluster, station_id, iterator=1):
    """

    :param cluster: string containing the cluster name (slugged)
    :param station_id: station number
    :param iterator: row number (from the bottom) to get

    """

    path = get_data_path_today()
    file = get_datastore_file(path)
    node = get_station_node(file, cluster, station_id)
    event, trace = retrieve_event(node, iterator)
    event_count = node.events.nrows
    file.close()
    event = event_to_dict(event)
    return event, trace, event_count


def retrieve_event(node, iterator):
    """Get the event and trace

    :param node: handler for the node of a station
    :param iterator: row number (from the bottom) to get

    """
    event = node.events[-iterator];
    trace_idx = event['traces'];
    trace_str = [zlib.decompress(node.blobs[idx]).split(',')
                 for idx in trace_idx if idx != -1]
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
    #FIXME when going live!
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


def event_to_dict(event):
    event_dict = {
        'event_id': long(event['event_id']),
        'timestamp': long(event['timestamp']),
        'nanoseconds': long(event['nanoseconds']),
        'data_reduction': str(event['data_reduction']),
        'trigger_pattern': long(event['trigger_pattern']),
        'baseline': event['baseline'].tolist(),
        'std_dev': event['std_dev'].tolist(),
        'n_peaks': event['n_peaks'].tolist(),
        'pulseheights': event['pulseheights'].tolist(),
        'integrals': event['integrals'].tolist(),
        'traces': event['traces'].tolist(),
        'event_rate': float(event['event_rate'])}
    return event_dict
