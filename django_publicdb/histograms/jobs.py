""" Various maintenance jobs that can either be executed by cron, are by
    accessing a view.

"""
from models import *
import eventwarehouse

import datetime
import logging
import numpy

logger = logging.getLogger('jobs')

MAX_PH = 1000
BIN_PH_STEP = 10
MAX_IN = 50000
BIN_IN_STEP = 200

def check_for_updates():
    state = GeneratorState.objects.get()

    if state.check_is_running:
        return False, False
    else:
        state.check_last_run = datetime.date.today()
        state.check_is_running = True
        state.save()

        new_last_event_id, new_events = \
            eventwarehouse.check_for_new_events(state.last_event_id)
        num_events = new_last_event_id - state.last_event_id
        state.last_event_id = new_last_event_id
        state.save()

        stations = {}
        for eventgroup in new_events:
            station_id, date = eventgroup
            logger.debug("Processing data for station %d from %s" % \
                (station_id, date))
            stations[station_id] = True
            try:
                s = Summary.objects.get(station_id=station_id, date=date)
            except Summary.DoesNotExist:
                s = Summary(station_id=station_id, date=date)
            s.needs_update = True
            s.has_raw_data = True
            s.save()

    state.check_is_running = False
    state.save()

    return num_events, len(stations)

def update_all_histograms():
    state = GeneratorState.objects.get()

    if state.update_is_running:
        return False
    else:
        state.update_last_run = datetime.date.today()
        state.update_is_running = True
        state.save()

        num_histograms = 0
        for summary in Summary.objects.filter(needs_update=True,
                                              has_raw_data=True):
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
    bins = range(24)
    data = eventwarehouse.get_eventtime_histogram(summary.station_id,
                                                  summary.date)

    histogram = []
    for hour in range(24):
        try:
            histogram.append(data[hour])
        except KeyError:
            histogram.append(0)

    save_histograms(summary, 'eventtime', bins, histogram)
    number_of_events = sum(histogram)
    return number_of_events

def update_pulseheight_histogram(summary):
    logger.debug("Updating pulseheight histogram for %s" % summary)
    pulseheights = eventwarehouse.get_pulseheights(summary.station_id,
                                                   summary.date)
    bins, histograms = create_histogram(pulseheights, MAX_PH, BIN_PH_STEP)
    save_histograms(summary, 'pulseheight', bins, histograms)

def update_pulseintegral_histogram(summary):
    logger.debug("Updating pulseintegral histogram for %s" % summary)
    integrals = eventwarehouse.get_pulseintegrals(summary.station_id,
                                                  summary.date)
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

def save_histograms(summary, slug, bins, histograms):
    logger.debug("Saving histogram %s for %s" % (slug, summary))
    type = HistogramType.objects.get(slug=slug)
    try:
        h = DailyHistogram.objects.get(source=summary, type=type)
    except DailyHistogram.DoesNotExist:
        h = DailyHistogram(source=summary, type=type)
    h.bins = bins
    h.histograms = histograms
    h.save()
    logger.debug("Saved succesfully")
