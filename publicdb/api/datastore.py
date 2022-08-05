import os
import zlib

import tables

from django.conf import settings

from sapphire import gps_to_datetime


def get_event_traces(station, ext_timestamp, raw=False):
    """Get the traces belonging to a station and a certain timestamp

    :param station: a :class:`publicdb.inforecords.models.Station`
                    instance
    :param ext_timestamp: extended timestamp (nanoseconds since UNIX epoch).
    :param raw: (optional, GET) if present get the raw trace, i.e. without
                subtracted baseline.

    """
    timestamp, nanoseconds = split_ext_timestamp(ext_timestamp)
    dt = gps_to_datetime(timestamp)
    path = get_data_path(dt)
    with tables.open_file(path, 'r') as file:
        node = get_station_node(file, station)
        traces = retrieve_traces(node, timestamp, nanoseconds, raw)
    return traces


def retrieve_traces(node, timestamp, nanoseconds, raw=False):
    """Get the traces

    :param node: handler for the node of a station
    :param timestamp, nanoseconds: time of the event

    """
    event = node.events.read_where(f'(timestamp == {timestamp}) & (nanoseconds == {nanoseconds})')[0]
    traces_idx = event['traces']
    baselines = event['baseline']
    traces_str = [zlib.decompress(node.blobs[trace_idx]).split(',')
                  for trace_idx in traces_idx if trace_idx != -1]

    traces = [[int(value) if baseline == -999 or raw else int(value) - baseline
               for value in trace_str if value != '']
              for baseline, trace_str in zip(baselines, traces_str)]

    return traces


def get_station_node(file, station):
    cluster_name = station.cluster.main_cluster().lower()
    node = file.get_node(f'/hisparc/cluster_{cluster_name}/station_{station.number}')
    return node


def get_data_path(date):
    """Return path to data file

    Return path to the data file of a particular date

    :param date: the date
    :return: path to the data file

    """
    rootdir = settings.DATASTORE_PATH
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')
    return os.path.join(rootdir, filepath)


def split_ext_timestamp(ext_timestamp):
    """Separate timestamp and nanoseconds from ext_timestamp"""
    ext_timestamp = int(ext_timestamp)  # cast numpy.uint64 (if read from datastore hdf5) to int
    timestamp = int(ext_timestamp / 1e9)
    nanoseconds = ext_timestamp % 1_000_000_000
    return timestamp, nanoseconds
