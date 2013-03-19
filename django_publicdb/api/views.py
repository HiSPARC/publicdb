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
        "stations_with_data": 'stations/data/{year}/{month}/{day}/',
        "stations_with_weather": 'stations/weather/{year}/{month}/{day}/',
        "station_info": 'station/{station_id}/',
        "has_data": 'station/{station_id}/data/{year}/{month}/{day}/',
        "has_weather": 'station/{station_id}/weather/{year}/{month}/{day}/',
        "configuration": 'station/{station_id}/config/{year}/{month}/{day}/',
        "number_of_events": 'station/{station_id}/num_events/{year}/{month}/{day}/{hour}/'}

    return json_dict(man)


def station(request, station_id):
    """Get station info

    Retrieve important information about a station.

    :param station_id: a station number identifier

    :return: station_info. This is a dictionary containing info about the
        station. Most importantly, this contains information about the
        position of the station, including the position of the individual
        scintillators.

    """
    try:
        station = Station.objects.get(number=station_id)
        detector = DetectorHisparc.objects.get(station=station)
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__lte=datetime.date.today())
                                       .latest('timestamp'))
    except (Station.DoesNotExist, Configuration.DoesNotExist):
        return HttpResponseNotFound()

    try:
        is_active = Pc.objects.filter(station=station)[0].is_active
    except IndexError:
        is_active = False

    scintillator1 = {"perpendicular": detector.scintillator_1_perp,
                     "longitudinal": detector.scintillator_1_long,
                     "angle": detector.scintillator_1_angle}
    scintillator2 = {"perpendicular": detector.scintillator_2_perp,
                     "longitudinal": detector.scintillator_2_long,
                     "angle": detector.scintillator_2_angle}

    if config.slave() != "no slave":
        scintillator3 = {"perpendicular": detector.scintillator_3_perp,
                         "longitudinal": detector.scintillator_3_long,
                         "angle": detector.scintillator_3_angle}
        scintillator4 = {"perpendicular": detector.scintillator_4_perp,
                         "longitudinal": detector.scintillator_4_long,
                         "angle": detector.scintillator_4_angle}

        station_info = {'number': station.number,
                        'name': station.name,
                        'cluster': station.cluster.name,
                        'country': station.cluster.country.name,
                        'latitude': config.gps_latitude,
                        'longitude': config.gps_longitude,
                        'altitude': config.gps_altitude,
                        'active': is_active,
                        'scintillators': 4,
                        'scintillator1': scintillator1,
                        'scintillator2': scintillator2,
                        'scintillator3': scintillator3,
                        'scintillator4': scintillator4}
    else:
        station_info = {'number': station.number,
                        'name': station.name,
                        'cluster': station.cluster.name,
                        'country': station.cluster.country.name,
                        'latitude': config.gps_latitude,
                        'longitude': config.gps_longitude,
                        'altitude': config.gps_altitude,
                        'active': is_active,
                        'scintillators': 2,
                        'scintillator1': scintillator1,
                        'scintillator2': scintillator2}

    return json_dict(station_info)


def stations(request, subcluster_id=None):
    """Get station list

    Retrieve a list of all stations or all stations in a subcluster.

    :param subcluster_id: a subcluster number identifier. If given, only
        stations belonging to that subcluster will be included in the list.

    :return: stations. This is a list containing dictionaries which consist of
        the name and number of each station (matching the subcluster).

    """
    if subcluster_id:
        try:
            subcluster = Cluster.objects.get(number=subcluster_id)
        except Cluster.DoesNotExist:
            return HttpResponseNotFound()
    else:
        subcluster = None

    stations = get_station_dict(subcluster=subcluster)

    return json_dict(stations)


def stations_with_data(request, year, month, day):
    """Get stations with data

    Retrieve a list of all stations which have data on the given date.

    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: stations. A list containing the name and number of each station
        that has measured events on the given date.

    """
    date = datetime.date(int(year), int(month), int(day))
    if not validate_date(date):
        return HttpResponseNotFound()

    summaries = Summary.objects.filter(num_events__isnull=False, date=date)
    stations = [{'number': summary.station.number, 'name': summary.station.name}
                for summary in summaries]

    return json_dict(stations)


def stations_with_weather(request, year, month, day):
    """Get stations with weather data

    Retrieve a list of all stations which have weather data on the given date.

    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: stations. A list containing the name and number of each station
        that has measured weather data on the given date.

    """
    date = datetime.date(int(year), int(month), int(day))
    if not validate_date(date):
        return HttpResponseNotFound()

    summaries = Summary.objects.filter(num_weather__isnull=False, date=date)
    stations = [{'number': summary.station.number, 'name': summary.station.name}
                for summary in summaries]

    return json_dict(stations)


def subclusters(request, cluster_id=None):
    """Get subcluster list

    Retrieve a list of all subclusters or all subclusters in a specific
    cluster.

    :param cluster_id: a cluster number identifier, give this to only get
        subclusters from this cluster.

    :return: subclusters. A list containing the name and number of all
        subclusters that matched the given parameters.

    """
    if cluster_id:
        try:
            cluster = Cluster.objects.get(number=cluster_id, parent=None)
        except Cluster.DoesNotExist:
            return HttpResponseNotFound()
    else:
        cluster = None

    subclusters = get_subcluster_dict(cluster=cluster)

    return json_dict(subclusters)


def clusters(request, country_id=None):
    """Get cluster list

    Retrieve a list of all clusters or only the clusters in a specific country.
    By cluster we here mean the main clusters, which contain subclusters.

    :param country_id: a country number identifier, give this to only get
        clusters from a specific country.

    :return: clusters. A list containing the name and number of all
        clusters that matched the given parameters.

    """
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
    """Get country list

    Retrieve a list of all countries with active stations.

    :return: countries. A list containing the name and number of all
        countries.

    """
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

