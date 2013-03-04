from django.http import HttpResponse, HttpResponseNotFound
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


def man(request):
    """Give overview of the possible urls"""

    man = {
        "base_url": 'http://data.hisparc.nl/api/',
        "stations": 'stations/',
        "stations_in_subcluster": 'subclusters/{subcluster_id}/',
        "subclusters": 'subclusters/',
        "subclusters_in_cluster": 'clusters/{cluster_id}/',
        "clusters": 'clusters/',
        "clusters_in_country": 'countries/{country_id}/',
        "countries": 'countries/',
        "stations_with_data": 'stations/{year}/{month}/{day}/',
        "station_info": 'station/{station_id}/',
        "has_data": 'station/{station_id}/data/{year}/{month}/{day}/',
        "has_weather": 'station/{station_id}/weather/{year}/{month}/{day}/',
        "configuration": 'station/{station_id}/config/{year}/{month}/{day}/',
        "number_of_events": 'station/{station_id}/num_events/{year}/{month}/{day}/{hour}/'}

    return json_dict(man)


def station(request, station_id=None):
    """Get station info, can be filtered by station"""
    try:
        station = Station.objects.get(number=station_id)
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__lte=datetime.date.today())
                                       .latest('timestamp'))
    except (Station.DoesNotExist, Configuration.DoesNotExist):
        return HttpResponseNotFound()

    try:
        is_active = Pc.objects.filter(station=station)[0].is_active
    except IndexError:
        is_active = False

    station_info = {'number': station.number,
                    'name': station.name,
                    'cluster': station.cluster.name,
                    'country': station.cluster.country.name,
                    'latitude': config.gps_latitude,
                    'longitude': config.gps_longitude,
                    'altitude': config.gps_altitude,
                    'active': is_active}

    return json_dict(station_info)


def stations(request, subcluster_id=None):
    """Get list of stations, can be filtered by subcluster"""
    if subcluster_id:
        try:
            subcluster = Cluster.objects.get(number=subcluster_id)
        except Cluster.DoesNotExist:
            return HttpResponseNotFound()
    else:
        subcluster = None

    station = get_station_dict(subcluster=subcluster)

    return json_dict(station)


def stations_with_data(request, year, month, day):
    """Check which stations have event data on the given date"""

    date = datetime.date(int(year), int(month), int(day))
    if not validate_date(date):
        return HttpResponseNotFound()

    summaries = Summary.objects.filter(num_events__isnull=False, date=date)
    stations = [{'number': summary.station.number, 'name': summary.station.name}
                    for summary in summaries]

    return json_dict(stations)


def subclusters(request, cluster_id=None):
    """Get list of subclusters, can be filtered by parent cluster"""
    if cluster_id:
        try:
            cluster = Cluster.objects.get(number=cluster_id, parent=None)
        except Cluster.DoesNotExist:
            return HttpResponseNotFound()
    else:
        cluster = None

    clusters = get_subcluster_dict(cluster=cluster)

    return json_dict(clusters)


def clusters(request, country_id=None):
    """Get list of clusters, can be filtered by country"""
    if country_id:
        try:
            country = Country.objects.get(number=country_id)
        except Country.DoesNotExist:
            return HttpResponseNotFound()
    else:
        country = None

    clusters = get_cluster_dict(country=country)

    return json_dict(clusters)


def countries(request):
    """Get list of countries"""
    countries = get_country_dict()

    return json_dict(countries)


def get_station_dict(subcluster=None):
    if subcluster:
        stations = Station.objects.filter(cluster=subcluster)
    else:
        stations = Station.objects.all()

    station_dict = []
    for station in stations:
        try:
            if Pc.objects.filter(station=station)[0].is_active:
                station_dict.append({'number': station.number,
                                     'name': station.name})
        except IndexError:
            pass

    return sorted(station_dict, key=itemgetter('number'))


def get_subcluster_dict(cluster=None):
    if cluster:
        subclusters = Cluster.objects.filter(parent=cluster)
    else:
        subclusters = Cluster.objects.all()

    subcluster_dict = [{'number': subcluster.number, 'name': subcluster.name}
                       for subcluster in subclusters]
    if cluster:
        subcluster_dict.append({'number': cluster.number, 'name': cluster.name})

    return sorted(subcluster_dict, key=itemgetter('number'))


def get_cluster_dict(country=None):
    if country:
        clusters = Cluster.objects.filter(country=country, parent=None)
    else:
        clusters = Cluster.objects.filter(parent=None)

    cluster_dict = [{'number': cluster.number, 'name': cluster.name}
                    for cluster in clusters]

    return sorted(cluster_dict, key=itemgetter('number'))


def get_country_dict():
    countries = Country.objects.all()
    country_dict = [{'number': country.number, 'name': country.name}
                    for country in countries]
    return sorted(country_dict, key=itemgetter('number'))


def has_data(request, station_id, year=None, month=None, day=None):
    """Check if there is valid event data for the given station and date"""

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    try:
        if year and month and day:
            date = datetime.date(int(year), int(month), int(day))
            if not validate_date(date):
                return HttpResponseNotFound()

            Summary.objects.filter(station=station,
                                   num_events__isnull=False,
                                   date=date)[0]
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

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    try:
        if year and month and day:
            date = datetime.date(int(year), int(month), int(day))
            if not validate_date(date):
                return HttpResponseNotFound()
            Summary.objects.filter(station=station,
                                   num_weather__isnull=False,
                                   date=date)[0]
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

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    try:
        if year and month and day:
            date = datetime.date(int(year), int(month), int(day))
            if not validate_date(date):
                return HttpResponseNotFound()
            c = (Configuration.objects.filter(source__station=station,
                                              timestamp__lte=date)
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


def num_events(request, station_id):
    """Get number of events in a certain year for the given station"""

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    start = datetime.date(2002, 1, 1)
    end = datetime.date.today()
    if not validate_date(start):
        return HttpResponseNotFound()

    summary = Summary.objects.filter(station=station,
                                     date__gte=start, date__lt=end,
                                     num_events__isnull=False)
    num_events = sum([s.num_events for s in summary])

    return json_dict(num_events)


def num_events_year(request, station_id, year):
    """Get number of events in a certain year for the given station"""

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    start = datetime.date(int(year), 1, 1)
    end = datetime.date(int(year) + 1, 1, 1)
    if not validate_date(start):
        return HttpResponseNotFound()

    summary = Summary.objects.filter(station=station,
                                     date__gte=start, date__lt=end,
                                     num_events__isnull=False)
    num_events = sum([s.num_events for s in summary])

    return json_dict(num_events)


def num_events_month(request, station_id, year, month):
    """Get number of events in a certain month for the given station"""

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    start = datetime.date(int(year), int(month), 1)
    if int(month) == 12:
        end = datetime.date(int(year) + 1, 1, 1)
    else:
        end = datetime.date(int(year), int(month) + 1, 1)
    if not validate_date(start):
        return HttpResponseNotFound()

    summary = Summary.objects.filter(station=station,
                                     date__gte=start, date__lt=end,
                                     num_events__isnull=False)
    num_events = sum([s.num_events for s in summary])

    return json_dict(num_events)


def num_events_day(request, station_id, year, month, day):
    """Get number of events for the given station and date"""

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    date = datetime.date(int(year), int(month), int(day))
    if not validate_date(date):
        return HttpResponseNotFound()

    try:
        summary = Summary.objects.get(station=station, date=date,
                                      num_events__isnull=False)
        num_events = summary.num_events
    except Summary.DoesNotExist:
        num_events = 0

    return json_dict(num_events)


def num_events_hour(request, station_id, year, month, day, hour):
    """Get number of events for the given station in the hour of the date"""

    try:
        station = Station.objects.get(number=station_id)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    date = datetime.date(int(year), int(month), int(day))
    if not validate_date(date):
        return HttpResponseNotFound()

    try:
        histogram = DailyHistogram.objects.get(source__station=station,
                                               type__slug='eventtime',
                                               source__date=date)
        num_events = histogram.values[int(hour)]
    except (DailyHistogram.DoesNotExist, IndexError):
        num_events = 0

    return json_dict(num_events)


def validate_date(date):
    """Give 404 is date is outside HiSPARC project range"""
    return datetime.date(2002, 1, 1) <= date <= datetime.date.today()

