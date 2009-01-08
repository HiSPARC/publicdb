from django.shortcuts import render_to_response
import eventwarehouse
from models import *
import datetime
import numpy

from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()

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

        for summary in Summary.objects.filter(needs_update=True):
            update_integral_histogram(summary)
            summary.needs_update = False
            summary.save()

    state.update_is_running = False
    state.save()

def update_integral_histogram(summary):
    print 'station: %d, date: %s' % (summary.station_id,
                                     summary.date.strftime('%c'))
    integrals = eventwarehouse.get_integrals(summary.station_id, summary.date)

    high = []
    for i in integrals:
        if i:
            high.append(max(i))
    high = max(high)

    histograms = []
    for array in integrals:
        hist, bins = numpy.histogram(array,
                                     bins=numpy.arange(0, high, BIN_IN_STEP))
        histograms.append(hist)

    bins = bins.tolist()
    histograms = [x.tolist() for x in histograms]

    type = HistogramType.objects.get(code='pulseintegral')
    try:
        h = DailyHistogram.objects.get(source=summary, type=type)
    except DailyHistogram.DoesNotExist:
        h = DailyHistogram(source=summary, type=type)
    h.bins = bins
    h.histogram = histograms
    h.save()
