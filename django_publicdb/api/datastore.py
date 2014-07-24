import os
import re
import datetime
from operator import itemgetter
import zlib

import tables

from django.conf import settings


def get_event_traces(station, ext_timestamp, raw=False):
    """Get the traces belonging to a station and a certain timestamp

    :param station: :class:`django_publicdb.inforecords.models.Station` instance
    :param ext_timestamp: extended timestamp (nanoseconds since UNIX epoch).
    :param raw: (optional, GET) if present get the raw trace, i.e. without
                subtracted baseline.

    """
    date = ext_timestamp_to_datetime(ext_timestamp)
    path = get_data_path(date)
    file = get_datastore_file(path)
    node = get_station_node(file, station)
    ts, ns = split_ext_timestamp(ext_timestamp)
    traces = retrieve_traces(node, ts, ns, raw)
    file.close()
    return traces


def retrieve_traces(node, timestamp, nanoseconds, raw=False):
    """Get the traces

    :param node: handler for the node of a station
    :param timestamp, nanoseconds: time of the event

    """
    event = node.events.read_where('(timestamp == %d) & (nanoseconds == %d)' %
                                  (timestamp, nanoseconds))[0]
    traces_idx = event['traces']
    baselines = event['baseline']
    traces_str = [zlib.decompress(node.blobs[trace_idx]).split(',')
                  for trace_idx in traces_idx if trace_idx != -1]
    traces = [[int(val) if baseline is -999 or raw else int(val) - baseline
               for val in trace_str if val != '']
              for baseline, trace_str in zip(baselines, traces_str)]

    return traces


def get_station_node(file, station):
    node = file.get_node('/hisparc/cluster_%s/station_%d' %
                        (station.cluster.main_cluster().lower(),
                         station.number))
    return node


def get_datastore_file(path):
    """Get the datafile

    :param path: path to the desired datafile

    :return: handler for the data file

    """
    file = tables.open_file(path, 'r')
    return file


def get_data_path(date):
    """Return path to data file

    Return path to the data file of a particular date

    :param date: the date

    :return: path to the data file

    """
    rootdir = settings.DATASTORE_PATH
    file = '%d_%d_%d.h5' % (date.year, date.month, date.day)
    return os.path.join(rootdir, str(date.year), str(date.month), file)


def ext_timestamp_to_datetime(ext_timestamp):
    """Extract timestamp from ext_timestamp to make datetime object"""
    timestamp = int(ext_timestamp / 1e9)
    return datetime.datetime.utcfromtimestamp(timestamp)


def split_ext_timestamp(ext_timestamp):
    """Separate timestamp and nanoseconds from ext_timestamp"""
    timestamp = int(ext_timestamp / 1e9)
    nanoseconds = ext_timestamp % 1000000000
    return timestamp, nanoseconds
