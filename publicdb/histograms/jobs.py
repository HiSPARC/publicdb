""" Various maintenance jobs that can either be executed by cron or by
    accessing a view.

"""
import calendar
import datetime
import logging
import multiprocessing
import time
import warnings

import numpy as np

import django.db

from django.conf import settings

# from sapphire.analysis.calibration import datetime_range
from sapphire.utils import round_in_base

from . import datastore, esd, fit_pulseheight_peak
from ..inforecords.models import Station
from ..station_layout.models import StationLayout
from .models import (Configuration, DailyDataset, DailyHistogram, DatasetType,
                     DetectorTimingOffset, GeneratorState, HistogramType,
                     MultiDailyDataset, MultiDailyHistogram, NetworkHistogram,
                     NetworkSummary, PulseheightFit, StationTimingOffset,
                     Summary)

logger = logging.getLogger('histograms.jobs')

# Parameters for the histograms
MAX_PH = 2500
BIN_PH_NUM = 250  # bin width = 10 mV
MAX_IN = 62500
BIN_IN_NUM = 250  # bin width = 250 mVns
MAX_SINGLES_LOW = 1000
BIN_SINGLES_LOW_NUM = 100  # bin width = 10
MAX_SINGLES_HIGH = 300
BIN_SINGLES_HIGH_NUM = 100  # bin width = 3

BIN_SINGLES_RATE = 150  # seconds

# Parameters for the datasets, interval in seconds
INTERVAL_TEMP = 150
INTERVAL_BARO = 150

# Tables supported by this code
SUPPORTED_TABLES = ['events', 'config', 'errors', 'weather', 'singles']
# Tables that initiate network updates
NETWORK_TABLES = {'events': 'coincidences'}
# Tables ignored by this code (unsupported tables not listed here will
# generate a warning).
IGNORE_TABLES = ['blobs']
# For some event tables, we can safely update the num_events during the
# check.  For events, for example, the histograms are recreated.  For
# configs, this is not possible.  The previous number of configs is used
# to select only new ones during the update.
RECORD_EARLY_NUM_EVENTS = ['events', 'weather', 'singles']
# Maximum number of configs per station per day. If more configs are found
# for a single day, all (new) configs will be treated as erroneous and skipped.
MAX_NUMBER_OF_CONFIGS = 100


def check_for_updates():
    """Run a check for updates to the event tables"""

    state = GeneratorState.objects.get()

    if state.check_is_running:
        check_has_run = False
    else:
        check_for_new_events_and_update_flags(state)
        check_has_run = True

    return check_has_run


def check_for_new_events_and_update_flags(state):
    """Check the datastore for new events and update flags"""

    # bookkeeping
    last_check_time = time.mktime(state.check_last_run.timetuple())
    check_last_run = datetime.datetime.now()
    state.check_is_running = True
    state.save()

    try:
        # perform a check for updated files
        possibly_new = datastore.check_for_new_events(last_check_time)

        # perform a thorough check for each possible date
        for date, station_list in possibly_new.iteritems():
            process_possible_stations_for_date(date, station_list)
        state.check_last_run = check_last_run
    finally:
        # bookkeeping
        state.check_is_running = False
        state.save()


def process_possible_stations_for_date(date, station_list):
    """Check stations for possible new data

    :param date: The date which needs to be updated as a date object
    :param station_list: A nested dictionary:
                         {'[station_number]': {'[table_name]': [n_rows], }, }

    """
    logger.info('Now processing %s' % date)
    unique_table_list = set([table_name
                             for table_list in station_list.values()
                             for table_name in table_list.keys()])
    for table_name in unique_table_list:
        process_possible_tables_for_network(date, table_name)
    for station, table_list in station_list.iteritems():
        process_possible_tables_for_station(station, table_list, date)


def process_possible_tables_for_network(date, table_name):
    """Check table and store summary for the network

    :param date: The date which needs to be updated as a date object
    :param table_name: The name of the changed table (e.g. 'events')

    """
    try:
        update_flag_attr = 'needs_update_%s' % NETWORK_TABLES[table_name]
        logger.info("New %s data on %s.", table_name,
                    date.strftime("%a %b %d %Y"))
        network_summary, _ = NetworkSummary.objects.get_or_create(date=date)
        setattr(network_summary, update_flag_attr, True)
        network_summary.needs_update = True
        network_summary.save()
    except KeyError:
        logger.debug('Unsupported table type for network: %s', table_name)


def process_possible_tables_for_station(station, table_list, date):
    """Check all tables and store summary for single station"""

    try:
        station = Station.objects.get(number=station)
    except Station.DoesNotExist:
        logger.error('Unknown station: %s' % station)
    else:
        summary, created = Summary.objects.get_or_create(station=station,
                                                         date=date)
        for table, num_events in table_list.iteritems():
            check_table_and_update_flags(table, num_events, summary)


def check_table_and_update_flags(table_name, num_events, summary):
    """Check a single table and update flags if new data"""

    if table_name in SUPPORTED_TABLES:
        number_of_events_attr = 'num_%s' % table_name
        update_flag_attr = 'needs_update_%s' % table_name

        if getattr(summary, number_of_events_attr) != num_events:
            logger.info("New data (%s) on %s for station %d", table_name,
                        summary.date.strftime("%a %b %d %Y"),
                        summary.station.number)
            # only record number of events for *some* tables at this time
            if table_name in RECORD_EARLY_NUM_EVENTS:
                setattr(summary, number_of_events_attr, num_events)
            setattr(summary, update_flag_attr, True)
            summary.needs_update = True
            summary.save()
    elif table_name not in IGNORE_TABLES:
        logger.warning('Unsupported table type: %s', table_name)


def update_all_histograms():
    """Perform the update tasks if no update is currently running."""

    state = GeneratorState.objects.get()

    if state.update_is_running:
        return False
    else:
        update_last_run = datetime.datetime.now()
        state.update_is_running = True
        state.save()

        try:
            perform_update_tasks()
            state.update_last_run = update_last_run
        finally:
            django.db.close_old_connections()
            state.update_is_running = False
            state.save()

    return True


def perform_update_tasks():
    """Perform the update tasks in specific order

    - First update ESD, which processes and stores events, weather and singles
      data.
    - Then update the histograms to determine detector offsets, perform
      event reconstructions, and create the station data histograms.
    - Then search coincidences in the ESD data and determine the time deltas
      (which require the detector offsets).
    - Finally create the histograms for the coincidences.

    """
    update_esd()
    update_histograms()
    update_coincidences()
    update_histograms()


def copy_temporary_and_set_flag(summary, needs_update_item, tmp_locations=[]):
    """Copy temporary data to the ESD and set a flag to False

    :param summary: Summary object for which the flag will be set to False.
        The summary is also used to find the destination file/table for the
        temporary data tables.
    :param needs_update_item: name of the flat which is to be set to False.
    :param tmp_locations: a list of tuples, each tuple containing the path
        to the temporary file and the node to be copied.

    """
    for tmpfile_path, node_path in tmp_locations:
        esd.copy_temporary_esd_node_to_esd(summary, tmpfile_path, node_path)
    setattr(summary, needs_update_item, False)
    django.db.close_old_connections()
    summary.save()


def update_esd():
    """Update the ESD for all Summaries with the needs_update flag

    Depending on the USE_MULTIPROCESSING flag, the manager either does the
    tasks himself or he grabs some workers and let them do it.

    """
    summaries = Summary.objects.filter(needs_update=True).reverse()
    if settings.USE_MULTIPROCESSING:
        worker_pool = multiprocessing.Pool()
        results = worker_pool.imap_unordered(
            process_and_store_temporary_esd_for_summary, summaries)

        for summary, tmp_locations in results:
            copy_temporary_and_set_flag(summary, 'needs_update', tmp_locations)

        worker_pool.close()
        worker_pool.join()
    else:
        for summary in summaries:
            summary, tmp_locations = \
                process_and_store_temporary_esd_for_summary(summary)
            copy_temporary_and_set_flag(summary, 'needs_update', tmp_locations)


def update_coincidences():
    """Update coincidences for all NetworkSummaries with the needs_update flag

    Depending on the USE_MULTIPROCESSING flag, the manager either does the
    tasks himself or he grabs some workers and let them do it.

    """
    network_summaries = (NetworkSummary.objects.filter(needs_update=True)
                                               .reverse())
    if settings.USE_MULTIPROCESSING:
        worker_pool = multiprocessing.Pool()
        results = worker_pool.imap_unordered(
            search_and_store_coincidences,
            network_summaries)

        for network_summary in results:
            network_summary.needs_update = False
            django.db.close_old_connections()
            network_summary.save()

        worker_pool.close()
        worker_pool.join()
    else:
        for network_summary in network_summaries:
            network_summary = search_and_store_coincidences(network_summary)
            network_summary.needs_update = False
            django.db.close_old_connections()
            network_summary.save()


def process_and_store_temporary_esd_for_summary(summary):
    """Process events, weather and singles from raw data and store in
    temporary file

    :param summary: Summary object for data will be processed if the
        corresponding flags are set.

    """
    django.db.close_old_connections()
    tmp_locations = []
    if summary.needs_update_events:
        tmp_locations.append(process_events_and_store_esd(summary))
    if summary.needs_update_weather:
        tmp_locations.append(process_weather_and_store_esd(summary))
    if summary.needs_update_singles:
        tmp_locations.append(process_singles_and_store_esd(summary))
    return summary, tmp_locations


def search_and_store_coincidences(network_summary):
    """Perform the search and storing of coincidences for a network summary

    :param network_summary: a NetworkSummary object.

    """
    django.db.close_old_connections()
    if network_summary.needs_update_coincidences:
        search_coincidences_and_store_esd(network_summary)
        determine_time_delta_and_store_esd(network_summary)
    return network_summary


def update_histograms():
    """Update new configs, histograms and datasets"""

    perform_tasks_manager(NetworkSummary, "needs_update_coincidences",
                          perform_coincidences_tasks)
    perform_tasks_manager(Summary, "needs_update_config",
                          perform_config_tasks)
    perform_tasks_manager(Summary, "needs_update_events",
                          perform_events_tasks)
    perform_tasks_manager(Summary, "needs_update_weather",
                          perform_weather_tasks)
    perform_tasks_manager(Summary, "needs_update_singles",
                          perform_singles_tasks)


def perform_tasks_manager(model, needs_update_item, perform_certain_tasks):
    """ Front office for doing tasks

    Depending on the USE_MULTIPROCESSING flag, the manager either does the
    tasks himself or he grabs some workers and let them do it.

    :param model: the summary model to query
    :param needs_update_item: the flag which has to be true for summaries to
        be processed.
    :param perform_certain_tasks: the function which performs the tasks
        required for the given flag.

    """
    summaries = model.objects.filter(**{needs_update_item: True,
                                        'needs_update': False}).reverse()

    if settings.USE_MULTIPROCESSING:
        worker_pool = multiprocessing.Pool()
        results = worker_pool.imap(perform_certain_tasks, summaries)
        current_date = None
        tmp_results = []
        for summary, tmp_locations in results:
            if current_date is None:
                current_date = summary.date
            if not current_date == summary.date:
                # Finish delayed store jobs.
                for summary_res, tmp_locations_res in tmp_results:
                    copy_temporary_and_set_flag(summary_res, needs_update_item,
                                                tmp_locations_res)
                tmp_results = []
                current_date = summary.date
            if not len(tmp_locations):
                copy_temporary_and_set_flag(summary, needs_update_item)
            else:
                # Delay storing until jobs for day have finished.
                tmp_results.append((summary, tmp_locations))
        if len(tmp_results):
            for summary, tmp_locations in tmp_results:
                copy_temporary_and_set_flag(summary, needs_update_item,
                                            tmp_locations)
        worker_pool.close()
        worker_pool.join()
    else:
        for summary in summaries:
            summary, tmp_locations = perform_certain_tasks(summary)
            copy_temporary_and_set_flag(summary, needs_update_item,
                                        tmp_locations)


def perform_events_tasks(summary):
    django.db.close_old_connections()
    logger.info("Updating event histograms for %s" % summary)
    update_eventtime_histogram(summary)
    update_pulseheight_histogram(summary)
    update_pulseheight_fit(summary)
    update_pulseintegral_histogram(summary)
    update_detector_timing_offsets(summary)
    tmp_locations = []
    try:
        layout = summary.station.stationlayout_set.filter(
            active_date__lte=summary.date).latest()
    except StationLayout.DoesNotExist:
        logger.debug("No station layout available for %s" % summary)
    else:
        if layout.detector_3_radius is not None:
            tmp_locations.append(
                esd.reconstruct_events_and_store_temporary_esd(summary))
            update_zenith_histogram(summary, *tmp_locations[-1])
            update_azimuth_histogram(summary, *tmp_locations[-1])
        else:
            logger.debug("No reconstructions for 2-detector station %s" %
                         summary)
    return summary, tmp_locations


def perform_config_tasks(summary):
    django.db.close_old_connections()
    logger.info("Updating configuration messages for %s" % summary)
    num_config = update_config(summary)
    summary.num_config = num_config
    return summary, []


def perform_weather_tasks(summary):
    django.db.close_old_connections()
    logger.info("Updating weather datasets for %s" % summary)
    update_temperature_dataset(summary)
    update_barometer_dataset(summary)
    return summary, []


def perform_singles_tasks(summary):
    django.db.close_old_connections()
    logger.info("Updating singles datasets for %s" % summary)
    update_singles_histogram(summary)
    update_singles_rate_dataset(summary)
    return summary, []


def perform_coincidences_tasks(network_summary):
    django.db.close_old_connections()
    logger.info("Updating coincidence histograms for %s" % network_summary)
    update_coincidencetime_histogram(network_summary)
    update_coincidencenumber_histogram(network_summary)
    update_station_timing_offsets(network_summary)
    return network_summary, []


def search_coincidences_and_store_esd(network_summary):
    """Search and store coincidences, and store the number of coincidences"""

    logger.info("Processing coincidences and storing ESD for %s" %
                network_summary)
    t0 = time.time()
    num_coincidences = \
        esd.search_coincidences_and_store_in_esd(network_summary)
    t1 = time.time()
    network_summary.num_coincidences = num_coincidences
    logger.debug("Processing took %.1f s." % (t1 - t0))


def determine_time_delta_and_store_esd(network_summary):
    logger.info("Processing time deltas and storing ESD for %s" %
                network_summary)
    t0 = time.time()
    esd.determine_time_delta_and_store_in_esd(network_summary)
    t1 = time.time()
    logger.debug("Processing took %.1f s." % (t1 - t0))


def process_events_and_store_esd(summary):
    logger.info("Processing events and storing ESD for %s" % summary)
    t0 = time.time()
    tmpfile_path, node_path = \
        esd.process_events_and_store_temporary_esd(summary)
    t1 = time.time()
    logger.debug("Processing took %.1f s." % (t1 - t0))
    return tmpfile_path, node_path


def process_weather_and_store_esd(summary):
    logger.info("Processing weather and storing ESD for %s" % summary)
    tmpfile_path, node_path = \
        esd.process_weather_and_store_temporary_esd(summary)
    return tmpfile_path, node_path


def process_singles_and_store_esd(summary):
    logger.info("Processing singles and storing ESD for %s" % summary)
    tmpfile_path, node_path = \
        esd.process_singles_and_store_temporary_esd(summary)
    return tmpfile_path, node_path


def update_eventtime_histogram(summary):
    logger.debug("Updating eventtime histogram for %s" % summary)
    timestamps = esd.get_event_timestamps(summary)

    # creating a histogram with bins consisting of timestamps instead of
    # hours saves us from having to convert all timestamps to hours of day.
    # timestamp at midnight (start of day) of date
    start = calendar.timegm(summary.date.timetuple())
    # create bins, don't forget right-most edge
    bins = [start + hour * 3600 for hour in range(25)]

    hist = np.histogram(timestamps, bins=bins)
    # redefine bins and histogram, don't forget right-most edge
    bins = range(25)
    hist = hist[0].tolist()
    save_histograms(summary, 'eventtime', bins, hist)


def update_coincidencetime_histogram(network_summary):
    """Histograms that show the number of coincidences per hour"""

    logger.debug("Updating coincidencetime histogram for %s" % network_summary)
    timestamps = esd.get_coincidence_timestamps(network_summary)

    # creating a histogram with bins consisting of timestamps instead of
    # hours saves us from having to convert all timestamps to hours of day.
    # timestamp at midnight (start of day) of date
    start = calendar.timegm(network_summary.date.timetuple())
    # create bins, don't forget right-most edge
    bins = [start + hour * 3600 for hour in range(25)]

    hist = np.histogram(timestamps, bins=bins)
    # redefine bins and histogram, don't forget right-most edge
    bins = range(25)
    hist = hist[0].tolist()
    save_network_histograms(network_summary, 'coincidencetime', bins, hist)


def update_coincidencenumber_histogram(network_summary):
    """Histograms of the number of stations participating in coincidences"""

    logger.debug("Updating coincidencenumber histogram for %s" %
                 network_summary)
    n_stations = esd.get_coincidence_data(network_summary, 'N')

    # create bins, don't forget right-most edge
    bins = range(2, 101)

    hist = np.histogram(n_stations, bins=bins)
    hist = hist[0].tolist()
    save_network_histograms(network_summary, 'coincidencenumber', bins, hist)


def update_pulseheight_histogram(summary):
    """Histograms of pulseheights for each detector individually"""

    logger.debug("Updating pulseheight histogram for %s" % summary)
    pulseheights = esd.get_pulseheights(summary)
    bins, histograms = create_histogram(pulseheights, MAX_PH, BIN_PH_NUM)
    save_histograms(summary, 'pulseheight', bins, histograms)


def update_pulseheight_fit(summary):
    logger.debug("Updating pulseheight fit for %s" % summary)
    try:
        fits = fit_pulseheight_peak.get_pulseheight_fits(summary)
    except Configuration.DoesNotExist:
        logger.debug("No Configuration for station: %d." %
                     summary.station.number)
        return
    save_pulseheight_fits(summary, fits)


def update_pulseintegral_histogram(summary):
    """Histograms of pulseintegral for each detector individually"""

    logger.debug("Updating pulseintegral histogram for %s" % summary)
    integrals = esd.get_integrals(summary)
    bins, histograms = create_histogram(integrals, MAX_IN, BIN_IN_NUM)
    save_histograms(summary, 'pulseintegral', bins, histograms)


def update_singles_histogram(summary):
    """Histograms of singles data for each detector individually"""

    logger.debug("Updating singles histograms for %s" % summary)
    _, high, low = esd.get_singles(summary)

    bins, histograms = create_histogram(low, MAX_SINGLES_LOW,
                                        BIN_SINGLES_LOW_NUM)
    save_histograms(summary, 'singleslow', bins, histograms)

    bins, histograms = create_histogram(high, MAX_SINGLES_HIGH,
                                        BIN_SINGLES_HIGH_NUM)
    save_histograms(summary, 'singleshigh', bins, histograms)


def update_singles_rate_dataset(summary):
    """Singles rate for each detector individually"""

    logger.debug("Updating singles rate datasets for %s" % summary)
    ts, high, low = esd.get_singles(summary)

    # timestamp at midnight (start of day) of date
    start = calendar.timegm(summary.date.timetuple())

    # create bins, don't forget right-most edge
    n_bins = 24 * 60 * 60 // BIN_SINGLES_RATE
    bins = [start + step * BIN_SINGLES_RATE for step in range(n_bins + 1)]
    bin_idxs = [np.searchsorted(ts, bin) for bin in bins]

    rates = [shrink(column, bin_idxs, n_bins) for column in low]
    save_dataset(summary, 'singlesratelow', bins, rates)

    rates = [shrink(column, bin_idxs, n_bins) for column in high]
    save_dataset(summary, 'singlesratehigh', bins, rates)


def update_detector_timing_offsets(summary):
    """Determine detector timing offsets"""

    logger.debug("Determining detector timing offsets for %s" % summary)
    offsets = esd.determine_detector_timing_offsets_for_summary(summary)
    save_offsets(summary, offsets)


def update_station_timing_offsets(network_summary):
    """Determine which station timing offsets need updating and update"""

    logger.debug("Determining update of station offsets "
                 "for %s" % network_summary)
    summary_date = network_summary.date

    stations = esd.get_station_numbers_from_esd_coincidences(network_summary)
    network_off = esd.DetermineStationTimingOffsetsESD(stations)

    for ref_sn, sn in network_off.get_station_pairs_within_max_distance():
        off = esd.DetermineStationTimingOffsetsESD([ref_sn, sn])
        cuts = off._get_cuts(sn, ref_sn)
        left, right = off.determine_first_and_last_date(summary_date,
                                                        sn, ref_sn)
        # To update all affected offsets use:
        # for date, _ in datetime_range(left, right):
        # To only update offset for specific date use:
        for date in [summary_date]:
            ref_summary = get_summary_or_none(date, ref_sn)
            if ref_summary is None:
                continue
            summary = get_summary_or_none(date, sn)
            if summary is None:
                continue
            if date in cuts:
                logger.debug("Setting offset for config cut to nan for %s"
                             " ref %s at %s" % (summary, ref_summary, date))
                offset, error = np.nan, np.nan
            else:
                logger.debug("Determining station offset for %s"
                             " ref %s at %s" % (summary, ref_summary, date))
                offset, error = off.determine_station_timing_offset(date, sn,
                                                                    ref_sn)
            save_station_offset(ref_summary, summary, offset, error)


def update_zenith_histogram(summary, tempfile_path, node_path):
    """Histogram of the reconstructed azimuth"""

    logger.debug("Updating zenith histogram for %s" % summary)
    zeniths = esd.get_zeniths(tempfile_path, node_path)

    # create bins, don't forget right-most edge
    bins = range(0, 91, 3)

    hist = np.histogram(zeniths, bins=bins)
    hist = hist[0].tolist()
    save_histograms(summary, 'zenith', bins, hist)


def update_azimuth_histogram(summary, tempfile_path, node_path):
    """Histogram of the reconstructed azimuth"""

    logger.debug("Updating azimuth histogram for %s" % summary)
    azimuths = esd.get_azimuths(tempfile_path, node_path)

    # create bins, don't forget right-most edge
    bins = range(-180, 181, 12)

    hist = np.histogram(azimuths, bins=bins)
    hist = hist[0].tolist()
    save_histograms(summary, 'azimuth', bins, hist)


def update_temperature_dataset(summary):
    """Create dataset of timestamped temperature data"""

    logger.debug("Updating temperature dataset for %s" % summary)
    temperature = esd.get_temperature(summary)
    error_values = [-999, -2 ** 15]
    temperature = [(x, y) for x, y in temperature if y not in error_values]
    if temperature != []:
        temperature = shrink_dataset(temperature, INTERVAL_TEMP)
        save_dataset(summary, 'temperature', *zip(*temperature))


def update_barometer_dataset(summary):
    """Create dataset of timestamped barometer data"""

    logger.debug("Updating barometer dataset for %s" % summary)
    barometer = esd.get_barometer(summary)
    error_values = [-999]
    barometer = [(x, y) for x, y in barometer if y not in error_values]
    if barometer != []:
        barometer = shrink_dataset(barometer, INTERVAL_BARO)
        save_dataset(summary, 'barometer', *zip(*barometer))


def shrink_dataset(dataset, interval):
    """Shrink a dataset by skipping over data.

    :param dataset: list of x, y data to be shrunk.
    :param interval: minimum value between subsequent x values.
    :return: list of tuples with filtered x, y values.

    """
    data = [dataset[0]]
    for x, y in dataset[1:]:
        if x - data[-1][0] >= interval:
            data.append((x, y))
    return data


def shrink(column, bin_idxs, n_bins):
    """Shrink a dataset.

    :param column: a column of data.
    :param bin_idxs: bin edge indexes.
    :param n_bins: number of bins.
    :return: list of shrunken data.

    """
    with warnings.catch_warnings():  # suppress "Mean of empty slice"
        warnings.simplefilter("ignore", category=RuntimeWarning)
        data = np.nan_to_num([np.nanmean(column[bin_idxs[i]:bin_idxs[i + 1]])
                              for i in range(n_bins)])
    return data.tolist()


def update_config(summary):
    cluster, station_number = get_station_cluster_number(summary.station)
    file, configs, blobs = datastore.get_config_messages(cluster,
                                                         station_number,
                                                         summary.date)
    num_config = len(configs)
    if num_config > MAX_NUMBER_OF_CONFIGS:
        logger.error('%s: Too many configs: %d. Skipping.' % (summary,
                                                              num_config))
        return summary.num_config

    for config in configs[summary.num_config:]:
        new_config = Configuration(source=summary)
        for var in vars(new_config):
            if var in ['source', 'id', 'source_id'] or var[0] == '_':
                pass
            elif var in ['mas_version', 'slv_version']:
                vars(new_config)[var] = blobs[config[var]]
            elif var == 'timestamp':
                ts = datetime.datetime.utcfromtimestamp(config[var])
                vars(new_config)[var] = ts
            else:
                vars(new_config)[var] = config[var]
        django.db.close_old_connections()
        new_config.save()

    file.close()
    return num_config


def create_histogram(data, high, samples):
    """Bin the given data, in bins from 0 to [high] in [samples] bins"""
    if data is None:
        return [], []
    else:
        values = []
        for array in data:
            bins = np.linspace(0, high, samples + 1)
            hist, bins = np.histogram(array, bins=bins)
            values.append(hist)

        bins = bins.tolist()
        values = [x.tolist() for x in values]

        return bins, values


def save_histograms(summary, slug, bins, values):
    """Store the binned data in database"""
    logger.debug("Saving histogram %s for %s" % (slug, summary))
    type = HistogramType.objects.get(slug=slug)
    histogram = {'bins': bins, 'values': values}
    if not type.has_multiple_datasets:
        DailyHistogram.objects.update_or_create(source=summary, type=type,
                                                defaults=histogram)
    else:
        MultiDailyHistogram.objects.update_or_create(source=summary, type=type,
                                                     defaults=histogram)
    logger.debug("Saved succesfully")


def save_network_histograms(network_summary, slug, bins, values):
    """Store the binned data in database"""
    logger.debug("Saving histogram %s for %s" % (slug, network_summary))
    type = HistogramType.objects.get(slug=slug)
    histogram = {'bins': bins, 'values': values}
    NetworkHistogram.objects.update_or_create(source=network_summary,
                                              type=type, defaults=histogram)
    logger.debug("Saved succesfully")


def save_dataset(summary, slug, x, y):
    """Store the data in database"""
    logger.debug("Saving dataset %s for %s" % (slug, summary))
    type = DatasetType.objects.get(slug=slug)
    dataset = {'x': x, 'y': y}
    if slug in ['barometer', 'temperature']:
        DailyDataset.objects.update_or_create(source=summary, type=type,
                                              defaults=dataset)
    else:
        MultiDailyDataset.objects.update_or_create(source=summary, type=type,
                                                   defaults=dataset)
    logger.debug("Saved succesfully")


def save_pulseheight_fits(summary, fits):
    if len(fits) == 0:
        logger.debug("Empty pulseheight fit results. Nothing to save.")
        return
    logger.debug("Saving pulseheight fits for %s" % summary)
    for fit in fits:
        try:
            fit.save()
        except django.db.IntegrityError:
            existing_fit = PulseheightFit.objects.get(source=summary,
                                                      plate=fit.plate)
            fit.id = existing_fit.id
            fit.save()

    logger.debug("Saved successfully")


def save_offsets(summary, offsets):
    """Store the detector timing offset data in database

    :param summary: summary of data source (station and date)
    :type summary: histograms.models.Summary instance
    :param offsets: list of 4 timing offsets

    """
    logger.debug("Saving detector timing offsets for %s" % summary)
    off = {'offset_%d' % i: round_in_base(o, 0.25) if not np.isnan(o) else None
           for i, o in enumerate(offsets, 1)}
    DetectorTimingOffset.objects.update_or_create(source=summary, defaults=off)
    logger.debug("Saved succesfully")


def save_station_offset(ref_summary, summary, offset, error):
    """Store the station timing offset in database

    :param summary: summary of station (station and date)
    :param ref_summary: summary of reference station (station and date)
    :param offset: station timing offset
    :param error: error of the offset

    """
    logger.debug("Saving station offset for %s ref %s" % (summary,
                                                          ref_summary))
    field = {}
    if not np.isnan(offset):
        field['offset'] = round(offset, 1)
        field['error'] = round(error, 2)
    else:
        field['offset'] = None
        field['error'] = None

    StationTimingOffset.objects.update_or_create(source=summary,
                                                 ref_source=ref_summary,
                                                 defaults=field)
    logger.debug("Saved succesfully")


def get_station_cluster_number(station):
    return station.cluster.main_cluster(), station.number


def get_summary_or_none(date, station_number):
    """Get summary for date and station_number"""

    try:
        return Summary.objects.get(station__number=station_number, date=date)
    except Summary.DoesNotExist:
        return None
