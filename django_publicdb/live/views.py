from django.http import HttpResponse
from django.shortcuts import (render_to_response, get_object_or_404,
                              get_list_or_404, redirect)
from django.template import RequestContext
from django.conf import settings

import json
import datetime
import random

import numpy as np

from django_publicdb.histograms.models import *
from django_publicdb.inforecords.models import *
from datastore import get_event


def station(request, station_id):
    """Show daily histograms for a particular station"""
    today = datetime.date.today()
    station_id = int(station_id)
    station = get_object_or_404(Station, number=station_id)
    config = (Configuration.objects.filter(source__station=station,
                                           timestamp__lt=datetime.date.today())
                                   .latest('timestamp'))
    detectorhisparc = (DetectorHisparc.objects.filter(station=station,
                                                      startdate__lte=today)
                                              .latest('startdate'))

    positions = [{"alpha": detectorhisparc.scintillator_1_alpha,
                  "beta": detectorhisparc.scintillator_1_beta,
                  "radius": detectorhisparc.scintillator_1_radius,
                  "height": detectorhisparc.scintillator_1_height},
                 {"alpha": detectorhisparc.scintillator_2_alpha,
                  "beta": detectorhisparc.scintillator_2_beta,
                  "radius": detectorhisparc.scintillator_2_radius,
                  "height": detectorhisparc.scintillator_2_height}]
    if config.slave() != "no slave":
        positions.extend([{"alpha": detectorhisparc.scintillator_3_alpha,
                           "beta": detectorhisparc.scintillator_3_beta,
                           "radius": detectorhisparc.scintillator_3_radius,
                           "height": detectorhisparc.scintillator_3_height},
                          {"alpha": detectorhisparc.scintillator_4_alpha,
                           "beta": detectorhisparc.scintillator_4_beta,
                           "radius": detectorhisparc.scintillator_4_radius,
                           "height": detectorhisparc.scintillator_4_height}])
    scintillators = {'number': len(positions),
                     'positions': positions}

    return render_to_response('live_display.html',
        {'station': station,
         'config': config,
         'scintillators': json.dumps(scintillators)},
        context_instance=RequestContext(request))


def get_new_event(request, station_id, iterator):
    iterator = int(iterator)
    station = get_object_or_404(Station, number=station_id)
    try:
        cluster_name = station.cluster.parent.name
    except:
        cluster_name = station.cluster.name
    event, traces, event_count = get_event(cluster_name, station.number, iterator)
    traces = subtract_baseline(event, traces)
    traces = create_plot_object(traces, 'Time (ns)', 'Signal (ADC)')
    return json_dict({"event": event, "traces": traces, "count": event_count})


def subtract_baseline(event, traces):
    traces = [[val - event['baseline'][i] for val in trace] for i, trace in enumerate(traces)]
    return traces


def create_plot_object(y_series, x_label, y_label):
    if type(y_series[0]) != list and type(y_series[0]) != tuple:
            y_series = [y_series]
    data = [[[xv * 2.5, -yv] for xv, yv in enumerate(y_values)] for
            y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label}
    return plot_object


def json_dict(dict):
    """Create a json HTTPResponse"""
    response = HttpResponse(json.dumps(dict, sort_keys=True),
                            content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
