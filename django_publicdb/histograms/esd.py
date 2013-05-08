"""Process events from datastore and save Event Summary Data (ESD)"""

import os.path
import tempfile

import tables
from sapphire.analysis import process_events
from sapphire.storage import ProcessedHisparcEvent

import datastore
import esd_storage


class ProcessEventsFromSource(process_events.ProcessEvents):

    """Process HiSPARC events from a different source.

    This class is a subclass of ProcessEvents.  The difference is that in
    this class, the source and destination are assumed to be different
    files.  This also means that the source is untouched (no renaming of
    original event tables) and the destination is assumed to be empty.
    """

    def __init__(self, source_file, dest_file, source_group, dest_group):
        """Initialize the class.

        :param source_file: the PyTables source file
        :param dest_file: the PyTables dest file
        :param group_path: the pathname of the source (and destination)
            group

        """
        self.source_file = source_file
        self.dest_file = dest_file

        self.source_group = self.source_file.getNode(source_group)
        self.dest_group = self.dest_file.getNode(dest_group)

        self.source = self._get_source()

    def _get_source(self):
        """Return the table containing the events.

        :returns: table object

        """
        if '_events' in self.source_group:
            source = self.source_group._events
        else:
            source = self.source_group.events
        return source

    def _check_destination(self, destination, overwrite):
        """Override method, the destination is empty"""
        pass

    def _create_empty_results_table(self):
        """Create empty results table with correct length."""

        if self.limit:
            length = self.limit
        else:
            length = len(self.source)

        table = self.dest_file.createTable(self.dest_group, 'events',
                                           ProcessedHisparcEvent,
                                           expectedrows=length)

        for x in xrange(length):
            table.row.append()
        table.flush()

        return table

    def _move_results_table_into_destination(self):
        """Override, destination is temporary table"""
        self.destination = self._tmp_events

    def _get_blobs(self):
        """Return blobs node"""

        return self.source_group.blobs


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
        tmp_filename = create_temporary_file()
        with tables.openFile(tmp_filename, 'w') as f:
            process_events = ProcessEventsFromSource(data, f, source_node,
                                                     '/')
            process_events.process_and_store_results(limit=100)
            copy_node_to_esd_file_for_summary(summary,
                                              process_events.destination)
    os.remove(tmp_filename)


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


def create_temporary_file():
    """Create a temporary file and return the pathname

    The file is closed as soon as it is created, to allow PyTables to open
    it for writing

    """
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    return f.name


def copy_node_to_esd_file_for_summary(summary, source_node):
    esd_path = esd_storage.get_or_create_esd_data_path(summary.date)

    with tables.openFile(esd_path, 'a') as esd_data:
        esd_group = get_or_create_station_node(esd_data, summary.station)
        source_node.copy(esd_group, createparents=True, overwrite=True)
