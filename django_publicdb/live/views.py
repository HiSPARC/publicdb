from django.http import HttpResponse
from django.shortcuts import (render_to_response, get_object_or_404,
                              get_list_or_404, redirect)
from django.template import RequestContext
from django.conf import settings

import json
import datetime
import random

from django_publicdb.inforecords.models import *
from datastore import *

def station(request, station_id):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)
    station = get_object_or_404(Station, number=station_id)
    try:
        cluster_name = station.cluster.parent.name
    except:
        cluster_name = station.cluster.name
    event, traces = get_trace(cluster_name, station.number)
    traces = subtract_baseline(event, traces)
    traces = create_plot_object(traces, 'Time [sample]', 'Signal [ADC]')
    return render_to_response('live_display.html',
        {'station': station,
         'event': event,
         'traces': traces},
        context_instance=RequestContext(request))


def get_new_event(request, station_id, iterator):
    iterator = int(iterator)
    station = get_object_or_404(Station, number=station_id)
    try:
        cluster_name = station.cluster.parent.name
    except:
        cluster_name = station.cluster.name
    event, traces = get_trace(cluster_name, station.number, iterator)
    traces = subtract_baseline(event, traces)
    traces = create_plot_object(traces, 'Time [sample]', 'Signal [ADC]')

    return json_dict(traces)


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


def json_dict(dict):
    """Create a json HTTPResponse"""
    response = HttpResponse(json.dumps(dict, sort_keys=True),
                            content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
