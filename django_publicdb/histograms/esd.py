"""Process events from datastore and save Event Summary Data (ESD)"""
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
        source_node = get_station_node_from_datastore_file(data, station)
        copy_node_to_esd_file_for_summary(summary, source_node)

    #copy to tmp?
    #... process_events(date, cluster, station_id)
    #copy from tmp to esd
    #copy_node_from_tmp_to_esd(date, cluster, station_id)


def get_station_node_from_datastore_file(data, station):
    """Return station node in datastore file

    :param data: datastore file
    :param station: inforecords.models.Station object

    """
    cluster = station.cluster.main_cluster()
    station_id = station.number

    group = data.getNode('/hisparc/cluster_%s/station_%d/' %
                         (cluster.lower(), station_id))
    return group


def copy_node_to_esd_file_for_summary(summary, source_node):
    esd_path = esd_storage.get_or_create_esd_data_path(summary.date)
    print esd_path


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
