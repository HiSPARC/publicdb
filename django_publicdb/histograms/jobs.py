""" Various maintenance jobs that can either be executed by cron or by
    accessing a view.

"""
import datetime
import time
import calendar
import logging
import multiprocessing

from sapphire.utils import round_in_base
import numpy as np

import django.db
from models import *
from django_publicdb.inforecords.models import Station, DetectorHisparc
import datastore
import esd

from django.conf import settings

import fit_pulseheight_peak

logger = logging.getLogger('histograms.jobs')

# Parameters for the histograms
MAX_PH = 2500
BIN_PH_NUM = 250  # bin width = 10 mV
MAX_IN = 62500
BIN_IN_NUM = 250  # bin width = 250 mVns

# Parameters for the datasets, interval in seconds
INTERVAL_TEMP = 150
INTERVAL_BARO = 150

# Tables supported by this code
SUPPORTED_TABLES = ['events', 'config', 'errors', 'weather']
# Tables that initiate network updates
NETWORK_TABLES = {'events': 'coincidences'}
# Tables ignored by this code (unsupported tables not listed here will
# generate a warning).
IGNORE_TABLES = ['blobs']
# For some event tables, we can safely update the num_events during the
# check.  For events, for example, the histograms are recreated.  For
# configs, this is not possible.  The previous number of configs is used
# to select only new ones during the update.
RECORD_EARLY_NUM_EVENTS = ['events', 'weather']


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
    unique_table_list = set([table_name for table_list in station_list.values()
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
            django.db.close_connection()
            state.update_is_running = False
            state.save()

    return True


def perform_update_tasks():
    update_esd()
    update_histograms()
    update_coincidences()
    update_histograms()


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
            for tmpfile_path, node_path in tmp_locations:
                esd.copy_temporary_esd_node_to_esd(summary, tmpfile_path,
                                                   node_path)
            summary.needs_update = False
            django.db.close_connection()
            summary.save()

        worker_pool.close()
        worker_pool.join()
    else:
        for summary in summaries:
            summary, tmp_locations = \
                process_and_store_temporary_esd_for_summary(summary)
            for tmpfile_path, node_path in tmp_locations:
                esd.copy_temporary_esd_node_to_esd(summary, tmpfile_path,
                                                   node_path)
            summary.needs_update = False
            django.db.close_connection()
            summary.save()


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
            search_and_store_coincidences_for_network_summary,
            network_summaries)

        for network_summary in results:
            network_summary.needs_update = False
            django.db.close_connection()
            network_summary.save()

        worker_pool.close()
        worker_pool.join()
    else:
        for network_summary in network_summaries:
            network_summary = search_and_store_coincidences_for_network_summary(network_summary)
            network_summary.needs_update = False
            django.db.close_connection()
            network_summary.save()


def process_and_store_temporary_esd_for_summary(summary):
    django.db.close_connection()
    tmp_locations = []
    if summary.needs_update_events:
        tmp_locations.append(process_events_and_store_esd(summary))
    if summary.needs_update_weather:
        tmp_locations.append(process_weather_and_store_esd(summary))
    return summary, tmp_locations


def search_and_store_coincidences_for_network_summary(network_summary):
    django.db.close_connection()
    if network_summary.needs_update_coincidences:
        search_coincidences_and_store_esd(network_summary)
    return network_summary


def update_histograms():
    """Update new configs, histograms and datasets"""

    perform_tasks_manager("Summary", "needs_update_config",
                          perform_config_tasks)
    perform_tasks_manager("Summary", "needs_update_events",
                          perform_events_tasks)
    perform_tasks_manager("Summary", "needs_update_weather",
                          perform_weather_tasks)
    perform_tasks_manager("NetworkSummary", "needs_update_coincidences",
                          perform_coincidences_tasks)


def perform_tasks_manager(model, needs_update_item, perform_certain_tasks):
    """ Front office for doing tasks

    Depending on the USE_MULTIPROCESSING flag, the manager either does the
    tasks himself or he grabs some workers and let them do it.

    """
    summaries = eval("%s.objects.filter(%s=True, needs_update=False).reverse()"
                     % (model, needs_update_item))

    if settings.USE_MULTIPROCESSING:
        worker_pool = multiprocessing.Pool()
        results = worker_pool.imap_unordered(perform_certain_tasks, summaries)
        for summary in results:
            exec "summary.%s=False" % needs_update_item
            django.db.close_connection()
            summary.save()
        worker_pool.close()
        worker_pool.join()
    else:
        for summary in summaries:
            perform_certain_tasks(summary)
            exec "summary.%s=False" % needs_update_item
            django.db.close_connection()
            summary.save()


def perform_events_tasks(summary):
    django.db.close_connection()
    logger.info("Updating event histograms for %s" % summary)
    update_eventtime_histogram(summary)
    update_pulseheight_histogram(summary)
    update_pulseheight_fit(summary)
    update_pulseintegral_histogram(summary)
    update_detector_timing_offsets(summary)
    return summary


def perform_config_tasks(summary):
    django.db.close_connection()
    logger.info("Updating configuration messages for %s" % summary)
    num_config = update_config(summary)
    summary.num_config = num_config
    return summary


def perform_weather_tasks(summary):
    django.db.close_connection()
    logger.info("Updating weather datasets for %s" % summary)
    update_temperature_dataset(summary)
    update_barometer_dataset(summary)
    return summary


def perform_coincidences_tasks(network_summary):
    django.db.close_connection()
    logger.info("Updating coincidence histograms for %s" % network_summary)
    update_coincidencetime_histogram(network_summary)
    update_coincidencenumber_histogram(network_summary)
    return network_summary


def search_coincidences_and_store_esd(network_summary):
    logger.info("Processing coincidences and storing ESD for %s" %
                network_summary)
    t0 = time.time()
    num_coincidences = \
        esd.search_coincidences_and_store_in_esd(network_summary)
    t1 = time.time()
    network_summary.num_coincidences = num_coincidences
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


def update_gps_coordinates():
    """Update GPS coordinates for all stations"""

    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    for detector in DetectorHisparc.objects.all():
        try:
            config = (Configuration.objects
                                   .filter(source__station=detector.station,
                                           timestamp__lt=tomorrow)
                                   .latest('timestamp'))
        except Configuration.DoesNotExist:
            pass
        else:
            if config.gps_latitude == 0. and config.gps_longitude == 0.:
                logger.error('Invalid GPS location (0, 0) for station: %s' %
                             detector.station)
            else:
                detector.latitude = config.gps_latitude
                detector.longitude = config.gps_longitude
                detector.height = config.gps_altitude
                django.db.close_connection()
                detector.save()


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


def update_detector_timing_offsets(summary):
    """Determine detector timing offsets"""

    logger.debug("Determining detector timing offsets for %s" % summary)
    offsets = esd.determine_detector_timing_offsets(summary)
    save_offsets(summary, offsets)


def update_temperature_dataset(summary):
    """Create dataset of timestamped temperature data"""

    logger.debug("Updating temperature dataset for %s" % summary)
    temperature = esd.get_temperature(summary)
    ERR = [-999, -2 ** 15]
    temperature = [(x, y) for x, y in temperature if y not in ERR]
    if temperature != []:
        temperature = shrink_dataset(temperature, INTERVAL_TEMP)
        save_dataset(summary, 'temperature', temperature)


def update_barometer_dataset(summary):
    """Create dataset of timestamped barometer data"""

    logger.debug("Updating barometer dataset for %s" % summary)
    barometer = esd.get_barometer(summary)
    ERR = [-999]
    barometer = [(x, y) for x, y in barometer if y not in ERR]
    if barometer != []:
        barometer = shrink_dataset(barometer, INTERVAL_BARO)
        save_dataset(summary, 'barometer', barometer)


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


def update_config(summary):
    cluster, station_number = get_station_cluster_number(summary.station)
    file, configs, blobs = datastore.get_config_messages(cluster,
                                                         station_number,
                                                         summary.date)
    for config in configs[summary.num_config:]:
        new_config = Configuration(source=summary)
        for var in vars(new_config):
            if var in ['source', 'id', 'source_id'] or var[0] == '_':
                pass
            elif var in ['mas_version', 'slv_version']:
                vars(new_config)[var] = blobs[config[var]]
            elif var == 'timestamp':
                ts = datetime.datetime.fromtimestamp(config[var])
                vars(new_config)[var] = ts
            else:
                vars(new_config)[var] = config[var]
        django.db.close_connection()
        new_config.save()

    num_config = len(configs)
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
    DailyHistogram.objects.update_or_create(source=summary, type=type,
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


def save_dataset(summary, slug, data):
    """Store the data in database"""
    logger.debug("Saving dataset %s for %s" % (slug, summary))
    type = DatasetType.objects.get(slug=slug)
    x, y = zip(*data)
    dataset = {'x': x, 'y': y}
    DailyDataset.objects.update_or_create(source=summary, type=type,
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


def get_station_cluster_number(station):
    return station.cluster.main_cluster(), station.number
