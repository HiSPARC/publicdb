""" Various maintenance jobs that can either be executed by cron, are by
    accessing a view.

"""
import datetime
import time
import calendar
import logging
import numpy

from models import *
from django_publicdb.inforecords.models import DetectorHisparc
import datastore

logger = logging.getLogger('histograms.jobs')

MAX_PH = 2000
BIN_PH_NUM = 200
MAX_IN = 20000
BIN_IN_NUM = 200

def check_for_updates():
    state = GeneratorState.objects.get()

    if state.check_is_running:
        return False
    else:
        last_check_time = time.mktime(state.check_last_run.timetuple())
        check_last_run = datetime.datetime.now()
        state.check_is_running = True
        state.save()

        try:
            summary = datastore.check_for_new_events(last_check_time)

            for date, station_list in summary.iteritems():
                for station, table_list in station_list.iteritems():
                    station = (inforecords.Station.objects
                                          .get(number=station))
                    s, created = Summary.objects.get_or_create(
                                    station=station, date=date)
                    for table, num_events in table_list.iteritems():
                        if (table == 'events' or table == 'config' or
                            table == 'errors' or table == 'weather'):

                            number_of = 'num_%s' % table
                            update_type = 'needs_update_%s' % table
                            if vars(s)[number_of] != num_events:
                                logger.debug("New data (%s) on %s for station %d" %
                                             (table,
                                              date.strftime("%a %b %d %Y"),
                                              station.number))
                                s.needs_update = True
                                vars(s)[update_type] = True
                                if table == 'events' or table == 'weather':
                                    vars(s)[number_of] = num_events
                                s.save()
            state.check_last_run = check_last_run
        finally:
            state.check_is_running = False
            state.save()

    return True

def update_all_histograms():
    state = GeneratorState.objects.get()

    if state.update_is_running:
        return False
    else:
        update_last_run = datetime.datetime.now()
        state.update_is_running = True
        state.save()

        try:
            for summary in Summary.objects.filter(needs_update=True):
                if summary.needs_update_events:
                    update_eventtime_histogram(summary)
                    update_pulseheight_histogram(summary)
                    update_pulseintegral_histogram(summary)
                    summary.needs_update_events = False

                if summary.needs_update_config:
                    num_config = update_config(summary)
                    summary.num_config = num_config
                    summary.needs_update_config = False

                if summary.needs_update_weather:
                    update_temperature_dataset(summary)
                    update_barometer_dataset(summary)
                    summary.needs_update_weather = False

                summary.needs_update = False
                summary.save()
            state.update_last_run = update_last_run
        finally:
            state.update_is_running = False
            state.save()

    return True

def update_gps_coordinates():
    """Update GPS coordinates for all stations"""

    for detector in DetectorHisparc.objects.all():
        try:
            config = (Configuration.objects
                                   .filter(source__station=detector.station)
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
    timestamps = datastore.get_event_timestamps(cluster, station_id,
                                                summary.date)

    # creating a histogram with bins consisting of timestamps instead of
    # hours saves us from having to convert all timestamps to hours of
    # day.
    # timestamp at midnight (start of day) of date
    start = calendar.timegm(summary.date.timetuple())
    # create bins, don't forget right-most edge
    bins = [start + hour * 3600 for hour in range(25)]

    hist = numpy.histogram(timestamps, bins=bins)
    # redefine bins and histogram, don't forget right-most edge
    bins = range(25)
    hist = hist[0].tolist()
    save_histograms(summary, 'eventtime', bins, hist)

def update_pulseheight_histogram(summary):
    logger.debug("Updating pulseheight histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    pulseheights = datastore.get_pulseheights(cluster, station_id,
                                              summary.date)
    bins, histograms = create_histogram(pulseheights, MAX_PH, BIN_PH_NUM)
    save_histograms(summary, 'pulseheight', bins, histograms)

def update_pulseintegral_histogram(summary):
    logger.debug("Updating pulseintegral histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    integrals = datastore.get_integrals(cluster, station_id, summary.date)
    bins, histograms = create_histogram(integrals, MAX_IN, BIN_IN_NUM)
    save_histograms(summary, 'pulseintegral', bins, histograms)

def update_temperature_dataset(summary):
    logger.debug("Updating temperature dataset for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    temperature = datastore.get_temperature(cluster, station_id,
                                            summary.date)
    ERR = -2**15
    temperature = [(x, y) for x, y in temperature if y != ERR]
    if temperature != []:
        save_dataset(summary, 'temperature', temperature)

def update_barometer_dataset(summary):
    logger.debug("Updating barometer dataset for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    barometer = datastore.get_barometer(cluster, station_id, summary.date)
    save_dataset(summary, 'barometer', barometer)

def update_config(summary):
    logger.debug("Updating configuration messages for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    file, configs, blobs = datastore.get_config_messages(cluster,
                                                        station_id,
                                                        summary.date)
    for config in configs[summary.num_config:]:
        new_config = Configuration(source=summary)
        for var in vars(new_config):
            if (var == 'source' or var == 'id' or var == 'source_id' or
                var[0] == '_'):
                pass
            elif var == 'mas_version' or var == 'slv_version':
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
    if data is None:
        return [], []
    else:
        values = []
        for array in data:
            bins = numpy.linspace(0, high, samples + 1)
            hist, bins = numpy.histogram(array, bins=bins)
            values.append(hist)

        bins = bins.tolist()
        values = [x.tolist() for x in values]

        return bins, values

def save_histograms(summary, slug, bins, values):
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

def save_dataset(summary, slug, data):
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

def get_station_cluster_id(station):
    return station.cluster().main_cluster(), station.number
