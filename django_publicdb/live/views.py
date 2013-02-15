from django.shortcuts import (render_to_response, get_object_or_404,
                              get_list_or_404, redirect)
from django.template import RequestContext
from django.conf import settings
from django.db.models import Q

import datetime

from django_publicdb.inforecords.models import *
from datastore import *

def station(request, station_id):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)
    station = get_object_or_404(Station, number=station_id)
    event, traces = get_trace(station.cluster.parent.name, station.number)
    traces = subtract_baseline(event, traces)
    traces = create_plot_object(traces, 'Time [sample]', 'Signal [ADC]')
    return render_to_response('live_display.html',
        {'station': station,
         'event': event,
         'traces': traces},
        context_instance=RequestContext(request))

def subtract_baseline(event, traces):
    traces = [[val - event['baseline'][i] for val in trace] for i, trace in enumerate(traces)]
    return traces


def create_plot_object(y_series, x_label, y_label):
    if type(y_series[0]) != list and type(y_series[0]) != tuple:
            y_series = [y_series]
    data = [[[xv, -yv] for xv, yv in enumerate(y_values)] for
            y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label}
    return plot_object


def get_new_trace(request, station_id):

    today = datetime.date.today()

    tracedata = create_histogram('eventtime', station, date)

    return trace
