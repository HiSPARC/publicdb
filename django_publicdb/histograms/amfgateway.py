from pyamf.remoting.gateway.django import DjangoGateway
from models import *
from django.core.exceptions import ObjectDoesNotExist

options_timehistogram = ['event time']
options_1dhistogram = ['pulse heights', 'pulse integrals']

def get_services(request):
    return services.keys()

def get_timehistogram_options(request):
    return options_timehistogram

def get_timehistogram(request, station_id, date, type):
    options = options_timehistogram
    
    if type == options[0]:
        histogram = get_histogram(station_id, date, 'eventtime')
        data = ['Event time distribution', 'counts per hour']
    else:
        histogram = None

    if histogram:
        data += [histogram.bins, histogram.histograms]
    else:
        data = None

    return data

def get_1dhistogram_options(request):
    return options_1dhistogram

def get_1dhistogram(request, station_id, date, type):
    options = options_1dhistogram

    if type == options[0]:
        histogram = get_histogram(station_id, date, 'pulseheight')
        data = ['Pulse integral', 'ADC values']
    elif type == options[1]:
        histogram = get_histogram(station_id, date, 'pulseintegral')
        data = ['Pulse integral', 'ADC values * sample']
    else:
        histogram = None

    if histogram:
        data += [histogram.bins, histogram.histograms]
    else:
        data = None

    return data

def get_histogram(station_id, date, type):
    try:
        summary = Summary.objects.get(station_id=station_id, date=date)
        histtype = HistogramType.objects.get(code=type)
        histogram = DailyHistogram.objects.get(source=summary, type=histtype)
    except ObjectDoesNotExist:
        return None
    else:
        return histogram


services = {'hisparc.get_services': get_services,
            'hisparc.get_timehistogram_options': get_timehistogram_options,
            'hisparc.get_timehistogram': get_timehistogram,
            'hisparc.get_1dhistogram_options': get_1dhistogram_options,
            'hisparc.get_1dhistogram': get_1dhistogram}

publicgateway = DjangoGateway(services)
