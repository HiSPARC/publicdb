from django.http import HttpResponse
from django.core import serializers

import json
from operator import itemgetter
import datetime

from django_publicdb.coincidences.models import *
from django_publicdb.analysissessions.models import *
from django_publicdb.inforecords.models import *
from django_publicdb.histograms.models import *


def json_dict(dict):
    """Create a json HTTPResponse"""
    response = HttpResponse(json.dumps(dict, sort_keys=True),
                            content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def station_info(request, station_id=None):
    """Get station info, can be filtered by station"""
    station = Station.objects.get(number=station_id)

    station_info = {'number': station.number, 'name': station.name,
                    'cluster': station.cluster.name,
                    'country': station.cluster.country.name}

    return json_dict(station_info)


def station(request, subcluster_name=None):
    """Get list of stations, can be filtered by subcluster"""
    cluster = Cluster.objects.filter(name=subcluster_name)
    station = get_station_dict(subcluster=cluster)

    return json_dict(station)


def subcluster(request, cluster_name=None):
    """Get list of subclusters, can be filtered by parent cluster"""
    cluster = Cluster.objects.filter(name=cluster_name, parent=None)
    clusters = get_subcluster_dict(cluster=cluster)

    return json_dict(clusters)


def cluster(request, country_name=None):
    """Get list of clusters, can be filtered by country"""
    country = Country.objects.filter(name=country_name)
    clusters = get_cluster_dict(country=country)

    return json_dict(clusters)


def country(request):
    """Get list of countries"""
    countries = get_country_dict()

    return json_dict(countries)


def get_station_dict(subcluster=None):
    if subcluster:
        stations = Station.objects.filter(cluster=subcluster)
    else:
        stations = Station.objects.all()

    station_dict = [{'number': station.number, 'name': station.name}
                    for station in stations]
    return sorted(station_dict, key=itemgetter('number'))


def get_subcluster_dict(cluster=None):
    if cluster:
        subclusters = Cluster.objects.filter(parent=cluster)
    else:
        subclusters = Cluster.objects.all()

    subcluster_dict = [{'number': subcluster.number, 'name': subcluster.name,
                        'stations': get_station_dict(subcluster)}
                       for subcluster in subclusters]
    if cluster:
        subcluster_dict.append({'number': cluster.number, 'name': cluster.name,
                                'stations': get_station_dict(cluster)})
    return sorted(subcluster_dict, key=itemgetter('number'))


def get_cluster_dict(country=None):
    if country:
        clusters = Cluster.objects.filter(country=country, parent=None)
    else:
        clusters = Cluster.objects.filter(parent=None)

    cluster_dict = [{'number': cluster.number, 'name': cluster.name,
                     'subclusters': get_subcluster_dict(cluster)}
                    for cluster in clusters]
    return sorted(cluster_dict, key=itemgetter('number'))


def get_country_dict():
    countries = Country.objects.all()
    country_dict = [{'number': country.number, 'name': country.name,
                     'clusters': get_cluster_dict(country=country)}
                    for country in countries]
    return sorted(country_dict, key=itemgetter('number'))


def has_data(request, station_id, year=None, month=None, day=None):
    """Check if there is valid event data for the given station and date"""

    station = Station.objects.get(number=station_id)

    try:
        if year and month and day:
            Summary.objects.filter(station=station,
                                   num_events__isnull=False,
                                   date=datetime.date(int(year), int(month), int(day)))[0]
        else:
            Summary.objects.filter(station=station,
                                   num_events__isnull=False,
                                   date__gte=datetime.date(2002, 1, 1),
                                   date__lte=datetime.date.today())[0]
        has_data = True
    except IndexError:
        has_data = False

    return json_dict(has_data)


def has_weather(request, station_id, year=None, month=None, day=None):
    """Check if there is valid weather data for the given station and date"""

    station = Station.objects.get(number=station_id)

    try:
        if year and month and day:
            Summary.objects.filter(station=station,
                                   num_weather__isnull=False,
                                   date=datetime.date(int(year), int(month), int(day)))[0]
        else:
            Summary.objects.filter(station=station,
                                   num_weather__isnull=False,
                                   date__gte=datetime.date(2002, 1, 1),
                                   date__lte=datetime.date.today())[0]
        has_weather = True
    except IndexError:
        has_weather = False

    return json_dict(has_weather)


def config(request, station_id, year=None, month=None, day=None):
    """Get the latest configuration of the station for a given date"""
    station = Station.objects.get(number=station_id)
    try:
        if year and month and day:
            c = (Configuration.objects.filter(source__station=station,
                                              timestamp__lte=datetime.date(int(year), int(month), int(day)))
                                      .latest('timestamp'))
        else:
            c = (Configuration.objects.filter(source__station=station,
                                              timestamp__lte=datetime.date.today())
                                      .latest('timestamp'))
        config = serializers.serialize("json", [c])
        config = json.loads(config)
        config = config[0]['fields']
    except IndexError:
        config = False

    return json_dict(config)
