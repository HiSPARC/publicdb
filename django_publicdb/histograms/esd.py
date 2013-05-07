""" Functions that do the processing of events
    from the datastore to the ESD

"""
import tempfile

import tables
from sapphire import process_events

import datastore
import esd_storage


def process_events_and_store_esd(summary):

    date = summary.date
    cluster = summary.station.cluster.main_cluster()
    station_id = summary.station.number

    source_node = get_node_from_datastore(date, cluster, station_id)
    #copy to tmp?
    ... process_events(date, cluster, station_id)
    #copy from tmp to esd
    copy_node_from_tmp_to_esd(date, cluster, station_id)

    pass


def get_node_from_datastore(date, cluster, station_id):
    # get events and blobs from datastore
    datapath = get_data_path(date)
    with tables.openFile(datapath, 'r') as file:
        table = file.getNode('/hisparc/cluster_%s/station_%d/' %
                             (cluster.lower(), station_id))

def get_tmp_file(date, station_id):
    # create tmp file
    filename = 's%d_' % station_id + date.strftime('%Y_%-m_%-d.h5')
    filepath = os.path.join(settings.TMP_PATH, filename)
    file = tables.openFile(filepath, 'w')

    return file


def copy_node_from_tmp_to_esd(tmp_node, esd_file):
    # copy node from tmp to esd

#     station_node = ...(tmp_node, station_id)
#     target_node = esd_storage.get_or_create_station_group(esd_file, cluster, station_id)
#     datafile.copyNode(station_node, esd_file.root, recursive=False)
#     target_node = target.getNode('/', station_node._v_name)
#     datafile.copyNode(node, target_node)
