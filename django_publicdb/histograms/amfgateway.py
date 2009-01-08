from pyamf.remoting.gateway.django import DjangoGateway
from models import *

options_1dhistogram = ['pulse heights', 'pulse integrals']

def get_services(request):
    return services.keys()

def get_1dhistogram_options(request):
    return options_1dhistogram

def get_1dhistogram(request, station_id, date, type):
    options = options_1dhistogram

    summary = Summary.objects.get(station_id=station_id, date=date)
    if type == options[0]:
        pass
    elif type == options[1]:
        histtype = HistogramType.objects.get(code='pulseintegral')
        histogram = DailyHistogram.objects.get(source=summary, type=histtype)
        data = ['Pulse integral', 'ADC values * sample', histogram.bins,
                histogram.histogram]
    else:
        data = None

    return data

services = {'hisparc.get_services': get_services,
            'hisparc.get_1dhistogram_options': get_1dhistogram_options,
            'hisparc.get_1dhistogram': get_1dhistogram}

publicgateway = DjangoGateway(services)
