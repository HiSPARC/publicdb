""" Various maintenance jobs that can either be executed by cron or by
    accessing a view.

"""
import datetime
import time
import calendar
import logging
import multiprocessing

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
MAX_PH = 2000
BIN_PH_NUM = 200
MAX_IN = 50000
BIN_IN_NUM = 200

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
    """Check stations for possible new data"""

    logger.debug('Now processing %s' % date)
    unique_table_list = set([table_name for table_list in station_list.values()
                                        for table_name in table_list.keys()])
    for table_name in unique_table_list:
        process_possible_tables_for_network(date, table_name)
    for station, table_list in station_list.iteritems():
        process_possible_tables_for_station(station, table_list, date)


def process_possible_tables_for_network(date, table_name):
    """Check table and store summary for the network"""
    try:
        update_flag_attr = 'needs_update_%s' % NETWORK_TABLES[table_name]
        logger.debug("New %s data on %s.", table_name,
                                           date.strftime("%a %b %d %Y"))
        networksummary, created = NetworkSummary.objects.get_or_create(date=date)
        setattr(networksummary, update_flag_attr, True)
        networksummary.needs_update = True
        networksummary.save()
    except KeyError:
        logger.debug('Unsupported table type for network: %s', table_name)


def process_possible_tables_for_station(station, table_list, date):
    """Check all tables and store summary for single station"""

    try:
        station = inforecords.Station.objects.get(number=station)
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
            logger.debug("New data (%s) on %s for station %d", table_name,
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
            state.update_is_running = False
            state.save()

    return True


def perform_update_tasks():
    update_esd()
    update_coincidences()
    update_histograms()


def update_esd():
    worker_pool = multiprocessing.Pool()
    summaries = Summary.objects.filter(needs_update=True).reverse()
    results = worker_pool.imap_unordered(
        process_and_store_temporary_esd_for_summary, summaries)

    for summary, tmp_locations in results:
        for tmpfile_path, node_path in tmp_locations:
            esd.copy_temporary_esd_node_to_esd(summary, tmpfile_path,
                                               node_path)
        summary.needs_update = False
        summary.save()

    worker_pool.close()
    worker_pool.join()


def update_coincidences():
    worker_pool = multiprocessing.Pool()
    summaries = NetworkSummary.objects.filter(needs_update=True).reverse()
    results = worker_pool.imap_unordered(
        process_and_store_coincidences_for_network_summary, summaries)

    for summary in results:
        summary.needs_update = False
        summary.save()

    worker_pool.close()
    worker_pool.join()


def process_and_store_temporary_esd_for_summary(summary):
    django.db.close_connection()
        for tmpfile_path, node_path in tmp_locations:
            esd.copy_temporary_esd_node_to_esd(summary, tmpfile_path,
                                               node_path)

    tmp_locations = []
    if summary.needs_update_events:
        tmp_locations.append(process_events_and_store_esd(summary))
    if summary.needs_update_weather:
        tmp_locations.append(process_weather_and_store_esd(summary))
    return summary, tmp_locations


def process_and_store_coincidences_for_network_summary(summary):
    django.db.close_connection()
    if summary.needs_update_coincidences:
        process_coincidences_and_store_esd(summary)
    return summary


def update_histograms():
    """Update all histograms"""

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
    summaries = eval("%s.objects.filter(%s=True).reverse()" %
                     (model, needs_update_item))

    if settings.USE_MULTIPROCESSING:
        worker_pool = multiprocessing.Pool()
        results = worker_pool.imap_unordered(perform_certain_tasks, summaries)
        for summary in results:
            exec "summary.%s=False" % needs_update_item
            summary.save()
        worker_pool.close()
        worker_pool.join()
    else:
        for summary in summaries:
            if not eval("summary.%s" % needs_update_item):
                continue

            perform_certain_tasks(summary)
            exec "summary.%s=False" % needs_update_item
            summary.save()


def perform_events_tasks(summary):
    django.db.close_connection()
    update_eventtime_histogram(summary)
    update_pulseheight_histogram(summary)
    update_pulseheight_fit(summary)
    update_pulseintegral_histogram(summary)
    return summary


def perform_config_tasks(summary):
    django.db.close_connection()
    num_config = update_config(summary)
    summary.num_config = num_config
    return summary


def perform_weather_tasks(summary):
    django.db.close_connection()
    update_temperature_dataset(summary)
    update_barometer_dataset(summary)
    return summary


def perform_coincidences_tasks(summary):
    django.db.close_connection()
    update_coincidencetime_histogram(summary)
    update_coincidencenumber_histogram(summary)
    return summary


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
            detector.latitude = config.gps_latitude
            detector.longitude = config.gps_longitude
            detector.height = config.gps_altitude
            detector.save()


def update_eventtime_histogram(summary):
    logger.debug("Updating eventtime histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
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


def update_coincidencetime_histogram(summary):
    logger.debug("Updating coincidencetime histogram for %s" % summary)
    timestamps = esd.get_coincidence_timestamps(summary)

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
    save_histograms(summary, 'coincidencetime', bins, hist)


def update_coincidencenumber_histogram(summary):
    logger.debug("Updating coincidencenumber histogram for %s" % summary)
    n_stations = esd.get_coincidence_data(summary, 'N')

    # create bins, don't forget right-most edge
    bins = range(2, 101)

    hist = np.histogram(n_stations, bins=bins)
    hist = hist[0].tolist()
    save_histograms(summary, 'coincidencenumber', bins, hist)


def update_pulseheight_histogram(summary):
    logger.debug("Updating pulseheight histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    pulseheights = esd.get_pulseheights(summary)
    bins, histograms = create_histogram(pulseheights, MAX_PH, BIN_PH_NUM)
    save_histograms(summary, 'pulseheight', bins, histograms)


def update_pulseheight_fit(summary):
    logger.debug("Updating pulseheight fit for %s" % summary)
    try:
        fits = fit_pulseheight_peak.getPulseheightFits(summary)
    except Configuration.DoesNotExist:
        logger.debug("No Configuration for station: %d." %
                     summary.station.number)
        return
    save_pulseheight_fits(summary, fits)


def update_pulseintegral_histogram(summary):
    logger.debug("Updating pulseintegral histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    integrals = esd.get_integrals(summary)
    bins, histograms = create_histogram(integrals, MAX_IN, BIN_IN_NUM)
    save_histograms(summary, 'pulseintegral', bins, histograms)


def process_coincidences_and_store_esd(summary):
    logger.debug("Processing coincidences and storing ESD for %s", summary)
    t0 = time.time()
    esd.process_coincidences_and_store_in_esd(summary)
    t1 = time.time()
    logger.debug("Processing took %.1f s.", t1 - t0)


def process_events_and_store_esd(summary):
    logger.debug("Processing events and storing ESD for %s", summary)
    t0 = time.time()
    tmpfile_path, node_path = \
        esd.process_events_and_store_temporary_esd(summary)
    t1 = time.time()
    logger.debug("Processing took %.1f s.", t1 - t0)
    return tmpfile_path, node_path


def process_weather_and_store_esd(summary):
    logger.debug("Processing weather events and storing ESD for %s", summary)
    tmpfile_path, node_path = \
        esd.process_weather_and_store_temporary_esd(summary)
    return tmpfile_path, node_path


def update_temperature_dataset(summary):
    logger.debug("Updating temperature dataset for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    temperature = esd.get_temperature(summary)
    ERR = [-999, -2 ** 15]
    temperature = [(x, y) for x, y in temperature if y not in ERR]
    if temperature != []:
        save_dataset(summary, 'temperature', temperature)


def update_barometer_dataset(summary):
    logger.debug("Updating barometer dataset for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    barometer = esd.get_barometer(summary)
    save_dataset(summary, 'barometer', barometer)


def update_config(summary):
    logger.debug("Updating configuration messages for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    file, configs, blobs = datastore.get_config_messages(cluster, station_id,
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
    try:
        h = DailyHistogram.objects.get(source=summary, type=type)
    except DailyHistogram.DoesNotExist:
        h = DailyHistogram(source=summary, type=type)
    h.bins = bins
    h.values = values
    h.save()
    logger.debug("Saved succesfully")


def save_network_histograms(summary, slug, bins, values):
    """Store the binned data in database"""
    logger.debug("Saving histogram %s for %s" % (slug, summary))
    type = HistogramType.objects.get(slug=slug)
    try:
        h = NetworkHistogram.objects.get(source=summary, type=type)
    except NetworkHistogram.DoesNotExist:
        h = NetworkHistogram(source=summary, type=type)
    h.bins = bins
    h.values = values
    h.save()
    logger.debug("Saved succesfully")


def save_dataset(summary, slug, data):
    """Store the data in database"""
    logger.debug("Saving dataset %s for %s" % (slug, summary))
    type = DatasetType.objects.get(slug=slug)
    try:
        d = DailyDataset.objects.get(source=summary, type=type)
    except DailyDataset.DoesNotExist:
        d = DailyDataset(source=summary, type=type)
    x, y = zip(*data)
    d.x = x
    d.y = y
    d.save()
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


def get_station_cluster_id(station):
    return station.cluster.main_cluster(), station.number
