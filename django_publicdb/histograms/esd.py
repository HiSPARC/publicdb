"""Process events from datastore and save Event Summary Data (ESD)"""

import os.path
import tempfile

import tables
from sapphire.analysis import process_events

import datastore
import esd_storage


def process_events_and_store_esd(summary):
    """Process events from datastore and save Event Summary Data

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    date = summary.date
    station = summary.station

    filepath = datastore.get_data_path(date)
    with tables.openFile(filepath, 'r') as data:
        source_node = get_station_node(data, station)
        copy_node_to_esd_file_for_summary(summary, source_node)

    #copy to tmp?
    #... process_events(date, cluster, station_id)
    #copy from tmp to esd
    #copy_node_from_tmp_to_esd(date, cluster, station_id)


def get_or_create_station_node(data, station):
    node_path = get_station_node_path(station)
    head, tail = os.path.split(node_path)

    if node_path in data:
        return data.getNode(head, tail)
    else:
        return data.createGroup(head, tail, createparents=True)


def get_station_node(data, station):
    """Return station node in datastore file

    :param data: datastore file
    :param station: inforecords.models.Station object

    """
    node_path = get_station_node_path(station)
    group = data.getNode(node_path)
    return group


def get_station_node_path(station):
    """Return station node path as used in data files

    :param station: inforecords.Station instance

    :returns: path to station group as used in datastore / ESD files

    """
    cluster = station.cluster.main_cluster()
    station_id = station.number
    return '/hisparc/cluster_%s/station_%d' % (cluster.lower(),
                                               station_id)


def copy_node_to_esd_file_for_summary(summary, source_node):
    esd_path = esd_storage.get_or_create_esd_data_path(summary.date)

    with tables.openFile(esd_path, 'a') as esd_data:
        esd_group = get_or_create_station_node(esd_data, summary.station)
        source_node.events.copy(esd_group, createparents=True)


def get_tmp_file(date, station_id):
    # create tmp file
    filename = 's%d_' % station_id + date.strftime('%Y_%-m_%-d.h5')
    filepath = os.path.join(settings.TMP_PATH, filename)
    file = tables.openFile(filepath, 'w')

    return file


def copy_node_from_tmp_to_esd(tmp_node, esd_file):
    pass
    # copy node from tmp to esd

#     station_node = ...(tmp_node, station_id)
#     target_node = esd_storage.get_or_create_station_group(esd_file, cluster, station_id)
#     datafile.copyNode(station_node, esd_file.root, recursive=False)
#     target_node = target.getNode('/', station_node._v_name)
#     datafile.copyNode(node, target_node)
