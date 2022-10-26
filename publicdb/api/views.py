import datetime
import json

from django.core import serializers
from django.http import HttpResponse, HttpResponseNotFound

from ..histograms.models import Configuration, DailyHistogram, HistogramType, Summary
from ..inforecords.models import Cluster, Country, Pc, Station
from ..station_layout.models import StationLayout
from ..status_display.status import DataStatus
from . import datastore

FIRSTDATE = datetime.date(2004, 1, 1)


def json_dict(result):
    """Create a json HTTPResponse"""
    response = HttpResponse(json.dumps(result, sort_keys=True), content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def man(request):
    """Give overview of the possible urls"""

    man = {
        "base_url": 'https://data.hisparc.nl/api/',
        "stations": 'stations/',
        "stations_in_subcluster": 'subclusters/{subcluster_number}/',
        "subclusters": 'subclusters/',
        "subclusters_in_cluster": 'clusters/{cluster_number}/',
        "clusters": 'clusters/',
        "clusters_in_country": 'countries/{country_number}/',
        "countries": 'countries/',
        "stations_with_data": 'stations/data/{year}/{month}/{day}/',
        "stations_with_weather": 'stations/weather/{year}/{month}/{day}/',
        "stations_with_singles": 'stations/singles/{year}/{month}/{day}/',
        "station_info": 'station/{station_number}/{year}/{month}/{day}/',
        "has_data": 'station/{station_number}/data/{year}/{month}/{day}/',
        "has_weather": 'station/{station_number}/weather/{year}/{month}/{day}/',
        "has_singles": 'station/{station_number}/singles/{year}/{month}/{day}/',
        "configuration": 'station/{station_number}/config/{year}/{month}/{day}/',
        "number_of_events": 'station/{station_number}/num_events/{year}/{month}/{day}/{hour}/',
        "event_trace": 'station/{station_number}/trace/{ext_timestamp}/',
    }

    return json_dict(man)


def network_status(request):
    """Get status of the network

    :return: dictionary containing status info for each station.

    """
    station_status = DataStatus()
    stations = []
    for station in Station.objects.exclude(pcs__type__slug='admin'):
        status = station_status.get_status(station.number)

        stations.append({'number': station.number, 'status': status})
    return json_dict(stations)


def station(request, station_number, year=None, month=None, date=None):
    """Get station info

    Retrieve general information about a station. If no date if given
    the latest valid info will be sent, otherwise the latest on or
    before the given date.

    :param station_number: a station number identifier.
    :param date: the date for which to get station info.

    :return: dictionary containing info about the station. Most importantly,
             this contains information about the location of the station GPS
             and the relative locations of the individual scintillators.

    """
    if not date:
        date = datetime.date.today()

    try:
        station = Station.objects.get(number=station_number)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    location = station.latest_location(date)

    try:
        layout = StationLayout.objects.filter(station=station, active_date__lte=date).latest()
    except StationLayout.DoesNotExist:
        # Get new StationLayout with all None values
        layout = StationLayout()

    is_active = Pc.objects.filter(station=station, is_active=True).exists()

    scintillators = [
        {
            'radius': layout.detector_1_radius,
            'alpha': layout.detector_1_alpha,
            'height': layout.detector_1_height,
            'beta': layout.detector_1_beta,
        }
    ]
    scintillators.append(
        {
            'radius': layout.detector_2_radius,
            'alpha': layout.detector_2_alpha,
            'height': layout.detector_2_height,
            'beta': layout.detector_2_beta,
        }
    )

    if station.number_of_detectors() == 4:
        scintillators.append(
            {
                'radius': layout.detector_3_radius,
                'alpha': layout.detector_3_alpha,
                'height': layout.detector_3_height,
                'beta': layout.detector_3_beta,
            }
        )
        scintillators.append(
            {
                'radius': layout.detector_4_radius,
                'alpha': layout.detector_4_alpha,
                'height': layout.detector_4_height,
                'beta': layout.detector_4_beta,
            }
        )

    station_info = {
        'number': station.number,
        'name': station.name,
        'subcluster': station.cluster.name,
        'cluster': station.cluster.main_cluster(),
        'country': station.cluster.country.name,
        'active': is_active,
        'scintillators': scintillators,
    }
    station_info.update(location)

    return json_dict(station_info)


def stations(request, subcluster_number=None):
    """Get station list

    Retrieve a list of all stations or all stations in a subcluster.

    :param subcluster_number: a subcluster number identifier. If given, only
        stations belonging to that subcluster will be included in the list.

    :return: list containing dictionaries which consist of the name and number
             of each station (matching the subcluster).

    """
    if subcluster_number:
        try:
            subcluster = Cluster.objects.get(number=subcluster_number)
        except Cluster.DoesNotExist:
            return HttpResponseNotFound()
    else:
        subcluster = None

    stations = get_station_dict(subcluster=subcluster)

    return json_dict(stations)


def stations_with_data(request, type=None, year=None, month=None, date=None):
    """Get stations with event or weather data

    Retrieve a list of all stations which have recorded events, singles or
    weather data in the given year, month, day or at all.

    :param type: data type to check for: events, singles or weather.
    :param year,month,date: the date, this has to be within the time
        HiSPARC has been operational and can be as specific as you desire.

    :return: list of dictionaries containing the name and number of each
             station that has measured weather data in the given year.

    """
    filters = {'pcs__is_test': False}

    if type == 'events':
        filters['summaries__num_events__isnull'] = False
    elif type == 'weather':
        filters['summaries__num_weather__isnull'] = False
    elif type == 'singles':
        filters['summaries__num_singles__isnull'] = False
    else:
        return HttpResponseNotFound()

    if date:
        filters['summaries__date'] = date
    elif month:
        date = datetime.date(int(year), int(month), 1)
        filters['summaries__date__year'] = year
        filters['summaries__date__month'] = month
    elif year:
        date = datetime.date(int(year), 1, 1)
        filters['summaries__date__year'] = year
    else:
        date = datetime.date.today()
        filters['summaries__date__gte'] = FIRSTDATE
        filters['summaries__date__lte'] = date

    if not validate_date(date):
        return HttpResponseNotFound()

    stations = list(Station.objects.filter(**filters).distinct().values('number', 'name'))

    return json_dict(stations)


def subclusters(request, cluster_number=None):
    """Get subcluster list

    Retrieve a list of all subclusters or all subclusters in a specific
    cluster.

    :param cluster_number: a cluster number identifier, give this to only get
        subclusters from this cluster.

    :return: list of dictionaries containing the name and number of all
             subclusters that matched the given parameters.

    """
    if cluster_number:
        try:
            cluster = Cluster.objects.get(number=cluster_number, parent=None)
        except Cluster.DoesNotExist:
            return HttpResponseNotFound()
    else:
        cluster = None

    subclusters = get_subcluster_dict(cluster=cluster)

    return json_dict(subclusters)


def clusters(request, country_number=None):
    """Get cluster list

    Retrieve a list of all clusters or only the clusters in a specific country.
    By cluster we here mean the main clusters, which contain subclusters.

    :param country_number: a country number identifier, give this to only get
        clusters from a specific country.

    :return: list of dictionaries containing the name and number of all
             clusters that matched the given parameters.

    """
    if country_number:
        try:
            country = Country.objects.get(number=country_number)
        except Country.DoesNotExist:
            return HttpResponseNotFound()
    else:
        country = None

    clusters = get_cluster_dict(country=country)

    return json_dict(clusters)


def countries(request):
    """Get country list

    Retrieve a list of all countries.

    :return: list of dictionaries containing the name and number of
             all countries.

    """
    countries = get_country_dict()

    return json_dict(countries)


def get_station_dict(subcluster=None):
    """Return list of station numbers and names

    For all non-test stations in the given subcluster

    """
    stations = Station.objects.filter(pcs__is_test=False, summaries__num_config__isnull=False)
    if subcluster:
        stations = stations.filter(cluster=subcluster)
    return list(stations.distinct().values('number', 'name'))


def get_subcluster_dict(cluster=None):
    if cluster:
        subclusters = Cluster.objects.filter(parent=cluster).order_by('number')
    else:
        subclusters = Cluster.objects.all().order_by('number')

    subcluster_dict = list(subclusters.values('number', 'name'))
    if cluster:
        subcluster_dict.append({'number': cluster.number, 'name': cluster.name})

    return subcluster_dict


def get_cluster_dict(country=None):
    clusters = Cluster.objects.filter(parent=None)
    if country:
        clusters = clusters.filter(country=country)
    return list(clusters.order_by('number').values('number', 'name'))


def get_country_dict():
    return list(Country.objects.all().order_by('number').values('number', 'name'))


def has_data(request, station_number, type=None, year=None, month=None, date=None):
    """Check for presence of cosmic ray data

    Find out if the given station has measured shower data, either on a
    specific date, or at all.

    :param station_number: a stationn number identifier.
    :param type: the data type: events, singles or weather.
    :param year,month,date: the date, this has to be within the time
            HiSPARC has been operational and can be as specific as
            you desire.

    :return: boolean, True if the given station has data, False otherwise.

    """
    try:
        station = Station.objects.get(number=station_number)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    summaries = Summary.objects.filter(station=station)

    if type == 'events':
        summaries = summaries.filter(num_events__isnull=False)
    elif type == 'weather':
        summaries = summaries.filter(num_weather__isnull=False)
    elif type == 'singles':
        summaries = summaries.filter(num_singles__isnull=False)

    if date:
        summaries = summaries.filter(date=date)
    elif month:
        date = datetime.date(int(year), int(month), 1)
        summaries = summaries.filter(date__year=date.year, date__month=date.month)
    elif year:
        date = datetime.date(int(year), 1, 1)
        summaries = summaries.filter(date__year=date.year)
    else:
        date = datetime.date.today()
        summaries = summaries.filter(date__gte=FIRSTDATE, date__lte=date)

    if not validate_date(date):
        return HttpResponseNotFound()

    has_data = summaries.exists()

    return json_dict(has_data)


def config(request, station_number, date=None):
    """Get station config settings

    Retrieve the entire configuration of a station. If no date if given the
    latest config will be sent, otherwise the latest on or before the given
    date.

    :param station_number: a station number identifier.
    :param date: the date for which to get a configuration.

    :return: dictionary containing the entire configuration from
             the HiSPARC DAQ.

    """
    try:
        station = Station.objects.get(number=station_number)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    if not date:
        date = datetime.date.today()

    try:
        summary = Summary.objects.filter(station=station, num_config__isnull=False, date__lte=date).latest()
        configuration = Configuration.objects.filter(summary=summary).latest()
    except (Configuration.DoesNotExist, Summary.DoesNotExist):
        return HttpResponseNotFound()

    config = serializers.serialize("json", [configuration])
    config = json.loads(config)
    try:
        config = config[0]['fields']
    except IndexError:
        config = False

    return json_dict(config)


def num_events(request, station_number, year=None, month=None, date=None, hour=None):
    """Get number of events for a station

    Retrieve the number of events that a station has measured during its
    entire operation or during a specific period, which can be a year,
    month, day or an hour.

    :param station_number: a stationn number identifier.
    :param year,month,date,hour: the date, this has to be within the time
        HiSPARC has been operational and can be as specific as you desire.
    :return: integer containing the total number of events ever recorded by
             the given station.

    """
    try:
        station = Station.objects.get(number=station_number)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    histogram_type = HistogramType.objects.get(slug='eventtime')
    filters = {'type': histogram_type, 'summary__station': station}

    if hour:
        hour = int(hour)
        if not 0 <= hour <= 23:
            return HttpResponseNotFound()
        try:
            histogram_values = DailyHistogram.objects.get(summary__date=date, **filters).values
            num_events = histogram_values[hour]
        except DailyHistogram.DoesNotExist:
            num_events = 0
    elif date:
        # Events on specific day
        filters['summary__date'] = date
    elif month:
        # Events in specific month
        date = datetime.date(year, month, 1)
        filters['summary__date__year'] = year
        filters['summary__date__month'] = month
    elif year:
        # Events in specific year
        date = datetime.date(year, 1, 1)
        filters['summary__date__year'] = year
    else:
        # All events
        date = datetime.date.today()
        filters['summary__date__gte'] = FIRSTDATE
        filters['summary__date__lt'] = date

    if not validate_date(date):
        return HttpResponseNotFound()

    if hour is None:
        histograms = DailyHistogram.objects.filter(**filters)
        num_events = sum(sum(histogram.values) for histogram in histograms)

    return json_dict(num_events)


def get_event_traces(request, station_number, ext_timestamp):
    """Get the traces for an event

    :param station_number: a station number identifier.
    :param ext_timestamp: extended timestamp (nanoseconds since UNIX epoch).
    :param raw: (optional, GET) if present get the raw trace, i.e. without
                subtracted baseline.

    :return: two or four traces.

    """
    raw = 'raw' in request.GET

    try:
        date = datetime.datetime.utcfromtimestamp(ext_timestamp / 1e9).date()
    except ValueError:
        return HttpResponseNotFound()

    if not validate_date(date):
        return HttpResponseNotFound()

    try:
        station = Station.objects.get(number=station_number)
        Summary.objects.get(station=station, date=date, num_events__isnull=False)
    except (Station.DoesNotExist, Summary.DoesNotExist):
        return HttpResponseNotFound()

    try:
        traces = datastore.get_event_traces(station, ext_timestamp, raw)
    except IndexError:
        return HttpResponseNotFound()

    return json_dict(traces)


def validate_date(date):
    """Check if date is outside HiSPARC project range

    If not valid, a 404 (Not Found) should be returned to the user.

    :return: boolean, True if the date is in the range, False otherwise.

    """
    return FIRSTDATE <= date <= datetime.date.today()
