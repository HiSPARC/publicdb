""" Various maintenance jobs that can either be executed by cron, are by
    accessing a view.

"""
import datetime
import time
import calendar
import logging
import numpy

from models import *
import datastore

logger = logging.getLogger('histograms.jobs')

MAX_PH = 1000
BIN_PH_STEP = 10
MAX_IN = 50000
BIN_IN_STEP = 200

def check_for_updates():
    state = GeneratorState.objects.get()

    if state.check_is_running:
        return False
    else:
        last_check_time = time.mktime(state.check_last_run.timetuple())
        state.check_last_run = datetime.datetime.now()
        state.check_is_running = True
        state.save()

        date_list = datastore.check_for_new_events(last_check_time)

        for date in date_list:
            logger.debug("New data on %s" % date.ctime())
            for station in datastore.get_stations(date):
                logger.debug("New data? for station %d" % station)
                station = inforecords.Station.objects.get(number=station)
                try:
                    s = Summary.objects.get(station=station, date=date)
                except Summary.DoesNotExist:
                    s = Summary(station=station, date=date)
                s.needs_update = True
                s.save()

    state.check_is_running = False
    state.save()

    return True

def update_all_histograms():
    state = GeneratorState.objects.get()

    if state.update_is_running:
        return False
    else:
        state.update_last_run = datetime.datetime.now()
        state.update_is_running = True
        state.save()

        num_histograms = 0
        for summary in Summary.objects.filter(needs_update=True):
            # updating histograms
            number_of_events = update_eventtime_histogram(summary)
            update_pulseheight_histogram(summary)
            update_pulseintegral_histogram(summary)
            # updated three histograms
            num_histograms += 3
            # updating summary
            summary.needs_update = False
            summary.number_of_events = number_of_events
            summary.save()

    state.update_is_running = False
    state.save()

    return num_histograms

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
    # create bins, don't forget closing boundary
    bins = [start + hour * 3600 for hour in range(25)]

    hist = numpy.histogram(timestamps, bins=bins)
    # redefine bins and histogram
    bins = range(24)
    hist = hist[0].tolist()

    save_histograms(summary, 'eventtime', bins, hist)
    number_of_events = sum(hist)
    return number_of_events

def update_pulseheight_histogram(summary):
    logger.debug("Updating pulseheight histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    pulseheights = datastore.get_pulseheights(cluster, station_id,
                                              summary.date)
    bins, histograms = create_histogram(pulseheights, MAX_PH, BIN_PH_STEP)
    save_histograms(summary, 'pulseheight', bins, histograms)

def update_pulseintegral_histogram(summary):
    logger.debug("Updating pulseintegral histogram for %s" % summary)
    cluster, station_id = get_station_cluster_id(summary.station)
    integrals = datastore.get_integrals(cluster, station_id, summary.date)
    bins, histograms = create_histogram(integrals, MAX_IN, BIN_IN_STEP)
    save_histograms(summary, 'pulseintegral', bins, histograms)

def create_histogram(data, high, step):
    histograms = []
    for array in data:
        hist, bins = numpy.histogram(array, bins=numpy.arange(0, high, step))
        histograms.append(hist)

    bins = bins.tolist()
    histograms = [x.tolist() for x in histograms]

    return bins, histograms

def save_histograms(summary, code, bins, histograms):
    logger.debug("Saving histogram %s for %s" % (code, summary))
    type = HistogramType.objects.get(code=code)
    try:
        h = DailyHistogram.objects.get(source=summary, type=type)
    except DailyHistogram.DoesNotExist:
        h = DailyHistogram(source=summary, type=type)
    h.bins = bins
    h.histograms = histograms
    h.save()
    logger.debug("Saved succesfully")

def get_station_cluster_id(station):
    return station.cluster().name, station.number
