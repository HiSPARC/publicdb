from pyamf.remoting.gateway.django import DjangoGateway
from models import *
from django.core.exceptions import ObjectDoesNotExist
from django_publicdb.inforecords.models import *

options_timehistogram = ['event time']
options_1dhistogram = ['pulse heights', 'pulse integrals']

import logging
logging.basicConfig(level=logging.INFO, filename='/tmp/test.log')
logger = logging.getLogger('test')

def get_services(request, arg1, arg2):
    logger.info('%r, %r' % (arg1, arg2))
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

def get_stations(request):
    """Get HiSPARC stations locations and status

    This function returns an array of dictionaries containing clusters,
    stations and their coordinates as well as status information

    """

    data = get_cluster_station_list(parent=None)

    return data

def get_cluster_station_list(parent):
    if parent:
        clusters = Cluster.objects.filter(parent=parent)
    else:
        clusters = Cluster.objects.filter(parent__isnull=True)

    data = []
    for cluster in clusters:
        c = {}
        c['name'] = cluster.name
        c['status'] = 1.0
        c['contents'] = get_cluster_station_list(parent=cluster)

        for station in Station.objects.filter(location__cluster=cluster):
            s = {}
            try:
                detector = DetectorHisparc.objects.get(station=station)
            except ObjectDoesNotExist:
                continue
            s['number'] = station.number
            s['latitude'] = detector.latitude
            if not s['latitude']:
                s['latitude'] = 52.0
            s['longitude'] = detector.longitude
            if not s['longitude']:
                s['longitude'] = 4.0
            s['status'] = 1.0

            c['contents'].append(s)

        data.append(c)

    return data


services = {
    'hisparc.get_services': get_services,
    'hisparc.get_timehistogram_options': get_timehistogram_options,
    'hisparc.get_timehistogram': get_timehistogram,
    'hisparc.get_1dhistogram_options': get_1dhistogram_options,
    'hisparc.get_1dhistogram': get_1dhistogram,
    'hisparc.get_stations': get_stations,
}

publicgateway = DjangoGateway(services)
