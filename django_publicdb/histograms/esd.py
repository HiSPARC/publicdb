"""Process events from datastore and save Event Summary Data (ESD)"""

import os.path
import tempfile
import logging
from operator import itemgetter

import numpy as np
import tables
from sapphire.analysis import process_events, coincidences
from sapphire.storage import ProcessedHisparcEvent
from sapphire import clusters

from django_publicdb.inforecords.models import Station
import datastore

from django.conf import settings


logger = logging.getLogger('histograms.esd')

# Limit the coincidence window to 1 microsecond,
# to prevent coincidental coincidences to become more dominant.
COINCIDENCE_WINDOW = 2000  # nanoseconds


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

        :return: table object

        """
        if '_events' in self.source_group:
            source = self.source_group._events
        else:
            source = self.source_group.events
        return source

    def _check_destination(self, destination, overwrite):
        """Override method, the destination is empty"""
        pass

    def _replace_table_with_selected_rows(self, table, row_ids):
        """Replace events table with selected rows.

        :param table: original table to be replaced.
        :param row_ids: row ids of the selected rows which should go in
            the destination table.

        """
        new_events = self.dest_file.createTable(self.dest_group, '_events',
            description=table.description)
        selected_rows = table.readCoordinates(row_ids)
        new_events.append(selected_rows)
        new_events.flush()
        return new_events

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

    def _create_progressbar_from_iterable(self, iterable, length=None):
        """Override method, do not show a progressbar"""

        return lambda x: x


def search_coincidences_and_store_in_esd(network_summary):
    """Determine coincidences for events from Event Summary Data

    Events from all non-test stations in the ESD are processed
    for coincidences, the results of which are stored in the
    coincidences group.

    :param network_summary: summary of data source (station and date)
    :type network_summary: histograms.models.NetworkSummary instance

    """
    date = network_summary.date

    # Get non-test stations with events on the specified date
    stations = Station.objects.filter(summary__date=date,
                                      summary__num_events__isnull=False,
                                      pc__is_test=False)

    station_groups = ['/hisparc/cluster_%s/station_%d' %
                      (station.cluster.main_cluster().lower(), station.number)
                      for station in stations]

    cluster = clusters.BaseCluster()
    for station in stations:
        # FIXME: Wrong station position and no detectors..
        cluster._add_station((0, 0), 0, [], station.number)

    filepath = get_esd_data_path(date)
    with tables.openFile(filepath, 'a') as data:
        coinc = coincidences.CoincidencesESD(data, '/coincidences',
                                             station_groups, overwrite=True)
        coinc.search_coincidences(window=COINCIDENCE_WINDOW)
        coinc.store_coincidences(cluster=cluster)
        num_coincidences = len(coinc.coincidences)

    return num_coincidences


def process_events_and_store_temporary_esd(summary):
    """Process events from datastore and save temporary Event Summary Data

    Events from the datastore are processed and stored in a temporary
    file.  The temporary file path and node path are returned.

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    date = summary.date
    station = summary.station

    filepath = datastore.get_data_path(date)
    with tables.openFile(filepath, 'r') as source_file:
        source_node = get_station_node(source_file, station)
        tmp_filename = create_temporary_file()
        with tables.openFile(tmp_filename, 'w') as tmp_file:
            process_events = ProcessEventsFromSource(source_file,
                                                     tmp_file,
                                                     source_node, '/')
            process_events.process_and_store_results()
            node_path = process_events.destination._v_pathname
    return tmp_filename, node_path


def process_weather_and_store_temporary_esd(summary):
    """Process weather events from datastore and save temporary ESD

    Currently, this is basically a no-op.

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    date = summary.date
    station = summary.station

    filepath = datastore.get_data_path(date)
    with tables.openFile(filepath, 'r') as source_file:
        source_node = get_station_node(source_file, station)
        tmp_filename = create_temporary_file()
        with tables.openFile(tmp_filename, 'w') as tmp_file:
            new_node = source_node.weather.copy(tmp_file.root)
            node_path = new_node._v_pathname
    return tmp_filename, node_path


def get_or_create_station_node(datafile, station):
    node_path = get_station_node_path(station)
    head, tail = os.path.split(node_path)

    if node_path in datafile:
        return datafile.getNode(head, tail)
    else:
        return datafile.createGroup(head, tail, createparents=True)


def get_station_node(datafile, station):
    """Return station node in datastore file

    :param data: datastore file
    :param station: inforecords.models.Station object

    """
    node_path = get_station_node_path(station)
    group = datafile.getNode(node_path)
    return group


def get_coincidences_node(datafile):
    """Return coincidences node in datastore file

    :param data: datastore file

    """
    node_path = '/coincidences'
    group = datafile.getNode(node_path)
    return group


def get_station_node_path(station):
    """Return station node path as used in data files

    :param station: inforecords.Station instance

    :return: path to station group as used in datastore / ESD files

    """
    cluster = station.cluster.main_cluster()
    return '/hisparc/cluster_%s/station_%d' % (cluster.lower(),
                                               station.number)


def create_temporary_file():
    """Create a temporary file and return the pathname

    The file is closed as soon as it is created, to allow PyTables to open
    it for writing

    """
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    return f.name


def copy_temporary_esd_node_to_esd(summary, file_path, node_path):
    """Copy temporary ESD node into the Event Summary Data

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param file_path: the path to the file containing the temporary ESD
        node.
    :param node_path: the path to the node to be copied

    """
    with tables.openFile(file_path, 'r') as tmp_file:
        node = tmp_file.getNode(node_path)
        copy_node_to_esd_file_for_summary(summary, node)
    os.remove(file_path)


def copy_node_to_esd_file_for_summary(summary, node):
    """Copy a PyTables node to ESD file

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param node: the node to be copied

    """
    esd_path = get_or_create_esd_data_path(summary.date)

    with tables.openFile(esd_path, 'a') as esd_data:
        esd_group = get_or_create_station_node(esd_data, summary.station)
        node.copy(esd_group, createparents=True, overwrite=True)


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

    :return: path to ESD file

    """
    filepath = get_esd_data_path(date)
    dirpath, filename = os.path.split(filepath)

    if not os.path.exists(dirpath):
        # create dir and parent dirs with mode rwxr-xr-x
        os.makedirs(dirpath, 0755)

    return filepath


def get_event_timestamps(summary):
    """Get event timestamps

    Read data from file and return a list of timestamps for all events on
    date `date' from station `station_number', specified by the summary.

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    return get_event_data(summary, 'timestamp')


def get_coincidence_timestamps(network_summary):
    """Get coincidence timestamps

    Read data from file and return a list of timestamps for all coincidences
    on the date specified by the summary.

    :param network_summary: summary of data source (date)
    :type network_summary: histograms.models.NetworkSummary instance

    """
    return get_coincidence_data(network_summary, 'timestamp')


def get_pulseheights(summary):
    """Get all event pulse heights

    Read data from file and return a list of pulseheights.

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    pulseheights = get_event_data(summary, 'pulseheights')
    if pulseheights is None:
        return None
    else:
        #FIXME: do we need configurations for this?
        pulseheights = np.where(pulseheights >= 0, pulseheights * .57,
                                pulseheights)

        # transpose, so we have '4 arrays of many pulseheights'
        return pulseheights.T


def get_integrals(summary):
    """Get all event integrals

    Read data from file and return a list of integrals.

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    integrals = get_event_data(summary, 'integrals')
    if integrals is None:
        return None
    else:
        # multiply by .57 for ADC -> mV, and by 2.5 for sample -> ns
        #FIXME: do we need configurations for this?
        integrals = np.where(integrals >= 0, integrals * .57 * 2.5,
                             integrals)

        # transpose, so we have '4 arrays of many integrals'
        return integrals.T


def get_temperature(summary):
    """Get temperature data

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    return get_time_series(summary, 'weather', 'temp_outside')


def get_barometer(summary):
    """Get barometer data

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    return get_time_series(summary, 'weather', 'barometer')


def get_event_data(summary, quantity):
    """Get event data of a specific quantity

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param quantity: the specific event data type (e.g., 'pulseheights')

    """
    return get_data(summary, 'events', quantity)


def get_coincidence_data(network_summary, quantity):
    """Get event data of a specific quantity

    :param network_summary: summary of data source (station and date)
    :type network_summary: histograms.models.NetworkSummary instance
    :param quantity: the specific event data type (e.g., 'pulseheights')

    """
    return get_coincidences(network_summary, 'coincidences', quantity)


def get_data(summary, tablename, quantity):
    """Get data from the datastore from a table of a specific quantity

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param tablename: table name (e.g. 'events', 'weather', ...)
    :param quantity: the specific event data type (e.g., 'pulseheights')

    """
    date = summary.date
    station = summary.station

    path = get_esd_data_path(date)
    with tables.openFile(path, 'r') as datafile:
        try:
            station_node = get_station_node(datafile, station)
            table = datafile.getNode(station_node, tablename)
        except tables.NoSuchNodeError:
            logger.error("Cannot find table %s for %s", tablename, summary)
            data = None
        else:
            data = table.col(quantity)

    return data


def get_coincidences(network_summary, tablename, quantity):
    """Get data from the datastore from a table of a specific quantity

    :param network_summary: summary of data source (date)
    :type network_summary: histograms.models.NetworkSummary instance
    :param tablename: table name (e.g. 'coincidences', 'observables', ...)
    :param quantity: the specific event data type (e.g., 'shower_size')

    """
    date = network_summary.date

    path = get_esd_data_path(date)
    with tables.openFile(path, 'r') as datafile:
        try:
            coincidences_node = get_coincidences_node(datafile)
            table = datafile.getNode(coincidences_node, tablename)
        except tables.NoSuchNodeError:
            logger.error("Cannot find table %s for %s", tablename, network_summary)
            data = None
        else:
            data = table.col(quantity)

    return data


def get_time_series(summary, tablename, quantity):
    """Get time series data from a table of a specific quantity

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param tablename: table name (e.g. 'events', 'weather', ...)
    :param quantity: the specific event data type (e.g., 'pulseheights')

    """
    date = summary.date
    station = summary.station

    path = get_esd_data_path(date)
    with tables.openFile(path, 'r') as datafile:
        try:
            station_node = get_station_node(datafile, station)
            table = datafile.getNode(station_node, tablename)
        except tables.NoSuchNodeError:
            logger.error("Cannot find table %s for %s", tablename,
                         summary)
            data = None
        else:
            col1 = table.col('timestamp')
            col2 = table.col(quantity)
            data = zip(col1, col2)
            data.sort(key=itemgetter(0))

    return data
