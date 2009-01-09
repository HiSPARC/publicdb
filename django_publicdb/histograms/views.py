from django.shortcuts import render_to_response
import eventwarehouse
from models import *
import datetime
import numpy

#from IPython.Shell import IPShellEmbed
#ipshell = IPShellEmbed()

BIN_PH_STEP = 10
BIN_IN_STEP = 200

def update_check(request):
    check_for_updates()
    return render_to_response('histograms/update_check.html')

def update_histograms(request):
    update_all_histograms()
    return render_to_response('histograms/update_histograms.html')

def check_for_updates():
    state = GeneratorState.objects.get()

    if state.check_is_running:
        return False
    else:
        state.check_last_run = datetime.date.today()
        state.check_is_running = True
        state.save()

        new_last_event_id, new_events = \
            eventwarehouse.check_for_new_events(state.last_event_id)
        state.last_event_id = new_last_event_id
        state.save()

        for eventgroup in new_events:
            station_id, date = eventgroup
            try:
                s = Summary.objects.get(station_id=station_id, date=date)
            except Summary.DoesNotExist:
                s = Summary(station_id=station_id, date=date)
            s.needs_update = True
            s.has_raw_data = True
            s.save()

    state.check_is_running = False
    state.save()

    return True

def update_all_histograms():
    state = GeneratorState.objects.get()

    if state.update_is_running:
        return False
    else:
        state.update_last_run = datetime.date.today()
        state.update_is_running = True
        state.save()

        for summary in Summary.objects.filter(needs_update=True,
                                              has_raw_data=True):
            number_of_events = update_eventtime_histogram(summary)
            update_pulseheight_histogram(summary)
            update_pulseintegral_histogram(summary)
            summary.needs_update = False
            summary.number_of_events = number_of_events
            summary.save()

    state.update_is_running = False
    state.save()

def update_eventtime_histogram(summary):
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
    pulseheights = eventwarehouse.get_pulseheights(summary.station_id,
                                                   summary.date)
    bins, histograms = create_histogram(pulseheights, BIN_PH_STEP)
    save_histograms(summary, 'pulseheight', bins, histograms)

def update_pulseintegral_histogram(summary):
    integrals = eventwarehouse.get_pulseintegrals(summary.station_id,
                                                  summary.date)
    bins, histograms = create_histogram(integrals, BIN_IN_STEP)
    save_histograms(summary, 'pulseintegral', bins, histograms)

def create_histogram(data, step):
    high = []
    for array in data:
        if array:
            high.append(max(array))
    high = max(high)

    histograms = []
    for array in data:
        hist, bins = numpy.histogram(array, bins=numpy.arange(0, high, step))
        histograms.append(hist)

    bins = bins.tolist()
    histograms = [x.tolist() for x in histograms]

    return bins, histograms

def save_histograms(summary, code, bins, histograms):
    type = HistogramType.objects.get(code=code)
    try:
        h = DailyHistogram.objects.get(source=summary, type=type)
    except DailyHistogram.DoesNotExist:
        h = DailyHistogram(source=summary, type=type)
    h.bins = bins
    h.histograms = histograms
    h.save()
