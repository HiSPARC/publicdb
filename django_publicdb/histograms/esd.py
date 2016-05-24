"""Process events from datastore and save Event Summary Data (ESD)"""

import os.path
import tempfile
import logging
import re
from operator import itemgetter

import numpy as np
import tables

from sapphire import (determine_detector_timing_offsets,
                      DetermineStationTimingOffsets,
                      ProcessEventsFromSourceWithTriggerOffset,
                      ProcessWeatherFromSource, CoincidencesESD,
                      ReconstructESDEventsFromSource, ProcessTimeDeltas)
from sapphire.analysis.calibration import datetime_range

from ..inforecords.models import Station
from .models import DetectorTimingOffset
from . import datastore

from django.conf import settings


logger = logging.getLogger('histograms.esd')

# Limit the coincidence window to 10 microseconds,
COINCIDENCE_WINDOW = 10000  # nanoseconds


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
                                      summary__needs_update=False,
                                      pc__is_test=False)

    station_numbers = [station.number for station in stations]
    station_groups = ['/hisparc/cluster_%s/station_%d' %
                      (station.cluster.main_cluster().lower(), station.number)
                      for station in stations]

    filepath = get_esd_data_path(date)
    with tables.open_file(filepath, 'a') as data:
        coinc = CoincidencesESD(data, '/coincidences', station_groups,
                                overwrite=True, progress=False)
        coinc.search_coincidences(window=COINCIDENCE_WINDOW)
        coinc.store_coincidences(station_numbers=station_numbers)
        num_coincidences = len(coinc.coincidences)

    return num_coincidences


def determine_time_delta_and_store_in_esd(network_summary):
    """Determine arrival time difference for station pairs in coincidences

    For all station pairs in coincidences determine the arrival time
    difference.

    :param network_summary: summary of data source (station and date)
    :type network_summary: histograms.models.NetworkSummary instance

    """
    date = network_summary.date
    filepath = get_esd_data_path(date)
    with tables.open_file(filepath, 'a') as data:
        td = ProcessTimeDeltas(data, progress=False)
        td.find_station_pairs()
        station_numbers = {station for pair in td.pairs for station in pair}
        td.detector_timing_offsets = {sn: get_offset_function(sn, date)
                                      for sn in station_numbers}
        td.determine_and_store_time_deltas_for_pairs()


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
    with tables.open_file(filepath, 'r') as source_file:
        source_node = get_station_node(source_file, station)
        tmp_filename = create_temporary_file()
        with tables.open_file(tmp_filename, 'w') as tmp_file:
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, source_node, '/', station.number)
            process.process_and_store_results()
            node_path = process.destination._v_pathname
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
    with tables.open_file(filepath, 'r') as source_file:
        source_node = get_station_node(source_file, station)
        tmp_filename = create_temporary_file()
        with tables.open_file(tmp_filename, 'w') as tmp_file:
            process = ProcessWeatherFromSource(source_file, tmp_file,
                                               source_node, '/')
            process.process_and_store_results()
            node_path = process.source._v_pathname
    return tmp_filename, node_path


def reconstruct_events_and_store_temporary_esd(summary):
    """Reconstruct events from datastore and save temporary Event Summary Data

    Events from the ESD are reconstructed and stored in a temporary
    file.  The temporary file path and node path are returned.

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    date = summary.date
    station = summary.station

    filepath = get_esd_data_path(date)
    source_path = get_station_node_path(station)
    with tables.open_file(filepath, 'r') as source_file:
        tmp_filename = create_temporary_file()
        with tables.open_file(tmp_filename, 'w') as tmp_file:
            reconstruct = ReconstructESDEventsFromSource(
                source_file, tmp_file, source_path, '/', station.number,
                progress=False)
            reconstruct.reconstruct_and_store()
            node_path = reconstruct.reconstructions._v_pathname
    return tmp_filename, node_path


def get_or_create_station_node(datafile, station):
    node_path = get_station_node_path(station)
    head, tail = os.path.split(node_path)

    if node_path in datafile:
        return datafile.get_node(head, tail)
    else:
        return datafile.create_group(head, tail, createparents=True)


def get_station_node(datafile, station):
    """Return station node in datastore file

    :param data: datastore file
    :param station: inforecords.models.Station object

    """
    node_path = get_station_node_path(station)
    group = datafile.get_node(node_path)
    return group


def get_coincidences_node(datafile):
    """Return coincidences node in datastore file

    :param data: datastore file

    """
    node_path = '/coincidences'
    group = datafile.get_node(node_path)
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
    with tables.open_file(file_path, 'r') as tmp_file:
        node = tmp_file.get_node(node_path)
        copy_node_to_esd_file_for_summary(summary, node)
    os.remove(file_path)


def copy_node_to_esd_file_for_summary(summary, node):
    """Copy a PyTables node to ESD file

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param node: the node to be copied

    """
    esd_path = get_or_create_esd_data_path(summary.date)

    with tables.open_file(esd_path, 'a') as esd_data:
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
        # FIXME: do we need configurations for this?
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
        # FIXME: do we need configurations for this?
        integrals = np.where(integrals >= 0, integrals * .57 * 2.5,
                             integrals)

        # transpose, so we have '4 arrays of many integrals'
        return integrals.T


def determine_detector_timing_offsets_for_summary(summary):
    """Get all detector timing offsets

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance

    """
    date = summary.date
    station = summary.station

    path = get_esd_data_path(date)
    with tables.open_file(path, 'r') as datafile:
        try:
            station_node = get_station_node(datafile, station)
            table = datafile.get_node(station_node, 'events')
        except tables.NoSuchNodeError:
            logger.error("Cannot find table events for %s", summary)
            offsets = [np.nan, np.nan, np.nan, np.nan]
        else:
            offsets = determine_detector_timing_offsets(table)

    return offsets


def get_zeniths(tmpfile_path, node_path):
    """Get all reconstructed zeniths

    Read data from file and return a list of zeniths.

    """
    return np.degrees(get_data_from_path(tmpfile_path, node_path, 'zenith'))


def get_azimuths(tmpfile_path, node_path):
    """Get all reconstructed azimuths

    Read data from file and return a list of azimuths.

    """
    return np.degrees(get_data_from_path(tmpfile_path, node_path, 'azimuth'))


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
    with tables.open_file(path, 'r') as datafile:
        try:
            station_node = get_station_node(datafile, station)
            table = datafile.get_node(station_node, tablename)
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
    with tables.open_file(path, 'r') as datafile:
        try:
            coincidences_node = get_coincidences_node(datafile)
            table = datafile.get_node(coincidences_node, tablename)
        except tables.NoSuchNodeError:
            logger.error("Cannot find table %s for %s", tablename,
                         network_summary)
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
    with tables.open_file(path, 'r') as datafile:
        try:
            station_node = get_station_node(datafile, station)
            table = datafile.get_node(station_node, tablename)
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


def get_timedeltas(date, ref_station, station):
    """Get timedeltas for a specific date

    Read timedelta's from ESD file, if data exists.
    :param date: date for which to get timedelta's
    :return: numpy.array of timedeltas

    """
    path = get_esd_data_path(date)
    try:
        with tables.open_file(path, 'r') as datafile:
            try:
                table_path = '/time_deltas/station_%d/station_%d' % \
                    (ref_station, station)
                tablename = 'time_deltas'
                table = datafile.get_node(table_path, tablename)
            except tables.NoSuchNodeError:
                logger.debug("Cannot find table %s %s for %s", table_path,
                             tablename, date)
                data = None
            else:
                data = table.col('delta')
    except IOError:
        logger.debug("ESD file %s does not exists", path)
        return None
    return data


def get_data_from_path(file_path, node_path, quantity):
    """Get reconstructed data

    Read data from file and return a list of values.
    Only return not-nan values.

    """
    with tables.open_file(file_path, 'r') as data:
        node = data.get_node(node_path)
        data = node.col(quantity)
    data = data[~np.isnan(data)]
    return data


def get_offset_function(station, date):
    """Get detector offsets for a station on a specific date as a function"""

    offsets = get_detector_offsets(station, date)

    def detector_timing_offset(ts):
        return offsets

    return detector_timing_offset


def get_detector_offsets(station, date):
    """Get detector offsets for a station on a specific date"""

    do = DetectorTimingOffset.objects.get(source__station__number=station,
                                          source__date=date)
    offsets = [do.offset_1, do.offset_2, do.offset_3, do.offset_4]
    return [o if o is not None else np.nan for o in offsets]


def get_station_numbers_from_esd_coincidences(network_summary):
    """Get the station numbers in a coincidence file"""

    date = network_summary.date
    filepath = get_esd_data_path(date)
    with tables.open_file(filepath, 'r') as data:
        s_index = data.root.coincidences.s_index
        re_number = re.compile('[0-9]+$')
        s_numbers = [int(re_number.search(s_path).group())
                     for s_path in s_index]
    return s_numbers


class DetermineStationTimingOffsetsESD(DetermineStationTimingOffsets):

    """Modified to work for the public database

    In the ESD the data is separated by date. To collect enough data to
    determine the offset multiple files may need to be opened. In order to
    facilitate this the method to collect the deltas is overwritten.

    """

    def read_dt(self, station, ref_station, start, end):
        """Overwrite how time deltas are read"""

        dt = []
        for date, _ in datetime_range(start, end):
            data = get_timedeltas(date, ref_station, station)
            if data is not None:
                dt.extend(data)
        return dt
