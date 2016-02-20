from django.http import HttpResponse, HttpResponseNotFound
from django.core import serializers

import json
from operator import itemgetter
import datetime

import numpy
from scipy import optimize, stats

from ..inforecords.models import (Pc, Station, Cluster, Country,
                                  MonitorPulseheightThresholds)
from ..histograms.models import (Summary, DailyHistogram, HistogramType,
                                 Configuration, PulseheightFit)
from ..station_layout.models import StationLayout
import datastore


FIRSTDATE = datetime.date(2004, 1, 1)


class Nagios:
    ok = (0, 'OK')
    warning = (1, 'WARNING')
    critical = (2, 'CRITICAL')
    unknown = (3, 'UNKNOWN')


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
        "stations_in_subcluster": 'subclusters/{subcluster_number}/',
        "subclusters": 'subclusters/',
        "subclusters_in_cluster": 'clusters/{cluster_number}/',
        "clusters": 'clusters/',
        "clusters_in_country": 'countries/{country_number}/',
        "countries": 'countries/',
        "stations_with_data": 'stations/data/{year}/{month}/{day}/',
        "stations_with_weather": 'stations/weather/{year}/{month}/{day}/',
        "station_info": 'station/{station_number}/{year}/{month}/{day}/',
        "has_data": 'station/{station_number}/data/{year}/{month}/{day}/',
        "has_weather": 'station/{station_number}/weather/{year}/{month}/{day}/',
        "configuration": 'station/{station_number}/config/{year}/{month}/{day}/',
        "number_of_events": 'station/{station_number}/num_events/{year}/{month}/{day}/{hour}/',
        "event_trace": 'station/{station_number}/trace/{ext_timestamp}/',
        "pulseheight_fit": 'station/{station_number}/plate/{plate_number}/pulseheight/fit/{year}/{month}/{day}/',
        "pulseheight_drift": 'station/{station_number}/plate/{plate_number}/pulseheight/drift/{year}/{month}/{day}/{number_of_days}/'}

    return json_dict(man)


def station(request, station_number, year=None, month=None, day=None):
    """Get station info

    Retrieve important information about a station. If no date if given
    the latest valid info will be sent, otherwise the latest on or
    before the given date.

    :param station_number: a station number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: dictionary containing info about the station. Most importantly,
             this contains information about the position of the station,
             including the position of the individual scintillators.

    """
    if year and month and day:
        date = datetime.date(int(year), int(month), int(day))
        if not validate_date(date):
            return HttpResponseNotFound()
    else:
        date = datetime.date.today()

    try:
        station = Station.objects.get(number=station_number)
        source_events = (Summary.objects.filter(station=station,
                                                num_events__isnull=False,
                                                date__lte=date).latest())
        source_config = (Summary.objects.filter(station=station,
                                                num_config__isnull=False,
                                                date__lte=date).latest())
        config = (Configuration.objects.filter(source=source_config)
                                       .exclude(gps_latitude=0,
                                                gps_longitude=0).latest())
    except (Station.DoesNotExist, Summary.DoesNotExist,
            Configuration.DoesNotExist):
        return HttpResponseNotFound()

    try:
        layout = StationLayout.objects.filter(station=station,
                                              active_date__lte=date).latest()
    except StationLayout.DoesNotExist:
        # Get new StationLayout with all None values
        layout = StationLayout()

    is_active = Pc.objects.filter(station=station, is_active=True).exists()

    mpv_fits = []

    for i in range(1, 5):
        try:
            mpv = (PulseheightFit.objects.get(source=source_events, plate=i)
                                         .fitted_mpv)
        except PulseheightFit.DoesNotExist:
            mpv_fits.append(None)
        else:
            if mpv == 0:
                mpv_fits.append(None)
            else:
                mpv_fits.append(round(mpv))

    scintillators = [{'radius': layout.detector_1_radius,
                      'alpha': layout.detector_1_alpha,
                      'height': layout.detector_1_height,
                      'beta': layout.detector_1_beta,
                      'mpv': mpv_fits[0]}]
    scintillators.append({'radius': layout.detector_2_radius,
                          'alpha': layout.detector_2_alpha,
                          'height': layout.detector_2_height,
                          'beta': layout.detector_2_beta,
                          'mpv': mpv_fits[1]})

    if config.slave() != "no slave":
        scintillators.append({'radius': layout.detector_3_radius,
                              'alpha': layout.detector_3_alpha,
                              'height': layout.detector_3_height,
                              'beta': layout.detector_3_beta,
                              'mpv': mpv_fits[2]})
        scintillators.append({'radius': layout.detector_4_radius,
                              'alpha': layout.detector_4_alpha,
                              'height': layout.detector_4_height,
                              'beta': layout.detector_4_beta,
                              'mpv': mpv_fits[3]})

    station_info = {'number': station.number,
                    'name': station.name,
                    'subcluster': station.cluster.name,
                    'cluster': station.cluster.main_cluster(),
                    'country': station.cluster.country.name,
                    'latitude': round(config.gps_latitude, 7),
                    'longitude': round(config.gps_longitude, 7),
                    'altitude': round(config.gps_altitude, 2),
                    'active': is_active,
                    'scintillators': scintillators}

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


def stations_with_data(request, type=None, year=None, month=None, day=None):
    """Get stations with event or weather data

    Retrieve a list of all stations which have recorded events or
    weather data in the given year, month, day or at all.

    :param type: data type to check for, either weather or events.
    :param year, month, day: the date, this has to be within the time
                             HiSPARC has been operational and can be as
                             specific as you desire.

    :return: list of dictionaries containing the name and number of each
             station that has measured weather data in the given year.

    """
    filters = {'pc__is_test': False}

    if type == 'events':
        filters['summary__num_events__isnull'] = False
    elif type == 'weather':
        filters['summary__num_weather__isnull'] = False
    else:
        return HttpResponseNotFound()

    if not year:
        date = datetime.date.today()
        filters['summary__date__gte'] = FIRSTDATE
        filters['summary__date__lte'] = date
    elif not month:
        date = datetime.date(int(year), 1, 1)
        filters['summary__date__year'] = date.year
    elif not day:
        date = datetime.date(int(year), int(month), 1)
        filters['summary__date__year'] = date.year
        filters['summary__date__month'] = date.month
    else:
        date = datetime.date(int(year), int(month), int(day))
        filters['summary__date'] = date

    stations = Station.objects.filter(**filters).distinct()

    if not validate_date(date):
        return HttpResponseNotFound()

    stations = [{'number': station.number, 'name': station.name}
                for station in stations]

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
    if subcluster:
        stations = (Station.objects.filter(cluster=subcluster,
                                           pc__is_test=False,
                                           summary__num_config__isnull=False)
                                   .distinct())
    else:
        stations = (Station.objects.filter(pc__is_test=False,
                                           summary__num_config__isnull=False)
                                   .distinct())

    station_dict = [{'number': station.number, 'name': station.name}
                    for station in stations]

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


def get_pulseheight_drift(request, station_number, plate_number,
                          year, month, day, number_of_days):
    """Get pulseheight drift

    :param station_number: station number
    :param plate_number: detector number, either 1, 2, 3 or 4.
    :param year, month, day: date for which to check
    :param number_of_days: number of days over which to determine drift
    """
    station_number = int(station_number)
    plate_number = int(plate_number)
    requested_date = datetime.date(int(year), int(month), int(day))
    number_of_days = int(number_of_days)

    dict = {'station': station_number,
            'plate_number': plate_number,
            'year': requested_date.year,
            'month': requested_date.month,
            'day': requested_date.day}

    if (plate_number < 1) or (plate_number > 4):
        dict.update({"nagios": Nagios.unknown,
                     "error": "Platenumber (value = %s) is out of range, "
                              "should be between 1 and 4" % plate_number})
        return json_dict(dict)

    try:
        station = Station.objects.get(number=station_number)
        date_range = (requested_date - datetime.timedelta(days=number_of_days - 1),
                      requested_date)
        summaries = Summary.objects.filter(station=station,
                                           date__range=date_range)
        fits = PulseheightFit.objects.filter(source__in=summaries,
                                             plate=plate_number,
                                             chi_square_reduced__gt=0.01,
                                             chi_square_reduced__lt=8.0,
                                             initial_width__gt=45.0)
    except Exception, e:
        dict.update({"nagios": Nagios.unknown,
                     "error": "Error retrieving fits",
                     "exception": str(e)})
        return json_dict(dict)

    if len(fits) < 14:
        dict.update({"nagios": Nagios.unknown,
                     "error": ("There are less than 14 fits in the requested "
                               "date range, no drift rate will be calculated.")})
        return json_dict(dict)

    try:
        # Fit drift

        t_array = numpy.float_([int(fit.source.date.strftime("%s"))
                                for fit in fits])
        mpv_array = numpy.float_([fit.fitted_mpv for fit in fits])

        linear_fit = lambda p, t: p[0] + p[1] * t  # Target function

        # Determine the drift by a linear fit
        errfunc = lambda p, t, y: linear_fit(p, t) - y  # Distance to the target function

        p0 = [1.0, 1.0 / 86400.0]  # Initial guess for the parameters
        p1, success = optimize.leastsq(errfunc, p0, args=(t_array, mpv_array))

        drift = p1[1] * 86400.0

        # Calculate the relative fluctuation

        relative_mpv = []

        for t, mpv in zip(t_array, mpv_array):
            relative_mpv.append(mpv / linear_fit(p1, t))

        # Fit the relative fluctation with a gauss
        gauss = lambda x, N, m, s: N * stats.norm.pdf(x, m, s)

        # x = ADC, y = number of events per dPulseheight

        bins = numpy.arange(0.0, 2.0, 0.005)
        y, bins = numpy.histogram(relative_mpv, bins=bins)
        x = (bins[:-1] + bins[1:]) / 2

        initial_N = 16
        initial_mean = 1
        initial_width = 0.03

        popt, pcov = optimize.curve_fit(gauss, x, y, p0=(initial_N,
                                                         initial_mean,
                                                         initial_width))

        dict.update({'number_of_selected_days': len(t_array),
                     'number_of_requested_days': number_of_days,
                     'fit_offset': p1[0],
                     'fit_slope': p1[1],
                     'drift_per_day': drift,
                     'timestamp': t_array.tolist(),
                     'mpv': mpv_array.tolist(),
                     'relative_mean': popt[1],
                     'relative_width': popt[2],

                     # Debug
                     # 'relative_mpv': relative_mpv,
                     # 'frequency': frequency.tolist(),
                     # 'x': x.tolist()
                     })

        return json_dict(dict)
    except Exception, e:
        dict.update({"nagios": Nagios.unknown,
                     "error": "Error in calculating the drift",
                     "exception": str(e)})
        return json_dict(dict)


def get_pulseheight_drift_last_14_days(request, station_number, plate_number):
    today = datetime.date.today()

    return get_pulseheight_drift(request, station_number, plate_number,
                                 today.year, today.month, today.day, 14)


def get_pulseheight_drift_last_30_days(request, station_number, plate_number):
    today = datetime.date.today()

    return get_pulseheight_drift(request, station_number, plate_number,
                                 today.year, today.month, today.day, 30)


def get_pulseheight_fit(request, station_number, plate_number,
                        year=None, month=None, day=None):
    """Get fit values of the pulseheight distribution for a station on a date

    Retrieve fit values of the pulseheight distribution. The fitting has
    to be done before and stored somewhere. This function retrieves the
    fit values from storage and returns to the client. Returns an error
    meesage if the values are not found on storage.

    :param station_number: a station number identifier.
    :param plate_number: plate number in the range 1..4
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: dictionary containing fit results of the specified station, plate
             and date

    """

    station_number = int(station_number)
    plate_number = int(plate_number)

    if year is None and month is None and day is None:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        requested_date = yesterday
    else:
        requested_date = datetime.date(int(year), int(month), int(day))

    dict = {'station': station_number,
            'plate_number': plate_number,
            'year': requested_date.year,
            'month': requested_date.month,
            'day': requested_date.day}

    try:
        fit = PulseheightFit.objects.get(source__station__number=station_number,
                                         source__date=requested_date,
                                         plate=plate_number)
    except Exception, e:
        dict.update({"nagios": Nagios.unknown,
                     "error": "Fit has not been found",
                     "exception": str(e)})
        return json_dict(dict)

    try:
        dict.update({"entries": fit.source.num_events,
                     "initial_mpv": fit.initial_mpv,
                     "initial_width": fit.initial_width,
                     "fitted_mpv": fit.fitted_mpv,
                     "fitted_mpv_error": fit.fitted_mpv_error,
                     "fitted_width": fit.fitted_width,
                     "fitted_width_error": fit.fitted_width_error,
                     "degrees_of_freedom": fit.degrees_of_freedom,
                     "chi_square_reduced": fit.chi_square_reduced,
                     "error_type": fit.error_type,
                     "error_message": fit.error_message})
    except Exception, e:
        dict.update({"nagios": Nagios.unknown,
                     "error": "Data has been found, "
                              "but error in converting data to numbers",
                     "exception": str(e)})
        return json_dict(dict)

    # Fit failures

    if len(fit.error_message) > 0:
        dict.update({"nagios": Nagios.critical,
                     "quality": fit.error_message})
        return json_dict(dict)

    # Based on chi2 of the fit

    if fit.chi_square_reduced < 0.01:
        dict.update({"nagios": Nagios.critical,
                     "quality": "Chi2 of the fit is smaller than 0.01: %.1f" %
                                fit.chi_square_reduced})
        return json_dict(dict)

    if fit.chi_square_reduced > 8.0:
        dict.update({"nagios": Nagios.critical,
                     "quality": "Chi2 of the fit is greater than 8.0: %.1f" %
                                fit.chi_square_reduced})
        return json_dict(dict)

    # Based on the fit range (= initial_width)

    if fit.initial_width < 45:
        dict.update({"nagios": Nagios.critical,
                     "quality": "Fit range is smaller than 45 ADC: %.1f ADC" %
                                fit.initial_width})
        return json_dict(dict)

    # Based on MPV and 4*sigma

    threshold = MonitorPulseheightThresholds.objects.get(station__number=station_number,
                                                         plate=plate_number)

    lower_bound = threshold.mpv_mean * (1 - 4 * threshold.mpv_sigma)
    upper_bound = threshold.mpv_mean * (1 + 4 * threshold.mpv_sigma)

    if fit.fitted_mpv < lower_bound or fit.fitted_mpv > upper_bound:
        dict.update({"nagios": Nagios.critical,
                     "quality": "Fitted MPV is outside bounds (%.1f;%.1f): %.1f" %
                                (lower_bound, upper_bound, fit.fitted_mpv)})
        return json_dict(dict)

    dict.update({"nagios": Nagios.ok,
                 "quality": "Fitted MPV is within bounds (%.1f;%.1f): %.1f" %
                            (lower_bound, upper_bound, fit.fitted_mpv)})
    return json_dict(dict)


def has_data(request, station_number, type=None, year=None, month=None,
             day=None):
    """Check for presence of cosmic ray data

    Find out if the given station has measured shower data, either on a
    specific date, or at all.

    :param station_number: a stationn number identifier.
    :param type: the data type, either events or weather.
    :param year, month, day: the date, this has to be within the time
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

    if day:
        date = datetime.date(int(year), int(month), int(day))
        summaries = summaries.filter(date=date)
    elif month:
        date = datetime.date(int(year), int(month), 1)
        summaries = summaries.filter(date__year=date.year,
                                     date__month=date.month)
    elif year:
        date = datetime.date(int(year), 1, 1)
        summaries = summaries.filter(date__year=date.year)
    else:
        date = datetime.date.today()
        summaries = summaries.filter(date__gte=FIRSTDATE,
                                     date__lte=date)

    if not validate_date(date):
        return HttpResponseNotFound()

    has_data = summaries.exists()

    return json_dict(has_data)


def config(request, station_number, year=None, month=None, day=None):
    """Get station config settings

    Retrieve the entire configuration of a station. If no date if given the
    latest config will be sent, otherwise the latest on or before the given
    date.

    :param station_number: a station number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: dictionary containing the entire configuration from
             the HiSPARC DAQ.

    """
    try:
        station = Station.objects.get(number=station_number)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    if year and month and day:
        date = datetime.date(int(year), int(month), int(day))
        if not validate_date(date):
            return HttpResponseNotFound()
    else:
        date = datetime.date.today()

    try:
        source = Summary.objects.filter(station=station,
                                        num_config__isnull=False,
                                        date__lte=date).latest()
        c = Configuration.objects.filter(source=source).latest()
    except (Configuration.DoesNotExist, Summary.DoesNotExist):
        return HttpResponseNotFound()

    config = serializers.serialize("json", [c])
    config = json.loads(config)
    try:
        config = config[0]['fields']
    except IndexError:
        config = False

    return json_dict(config)


def num_events(request, station_number, year=None, month=None, day=None,
               hour=None):
    """Get number of events for a station

    Retrieve the number of events that a station has measured during its
    entire operation or during a specific period, which can be a year,
    month, day or an hour.

    :param station_number: a stationn number identifier.
    :param year, month, day, hour: the date, this has to be within the
            time HiSPARC has been operational and can be as specific as
            you desire.

    :return: integer containing the total number of events ever recorded by
             the given station.

    """
    try:
        station = Station.objects.get(number=station_number)
    except Station.DoesNotExist:
        return HttpResponseNotFound()

    histogram_type = HistogramType.objects.get(slug='eventtime')

    histograms = DailyHistogram.objects.filter(source__station=station,
                                               type=histogram_type)

    if not year:
        date = datetime.date.today()
        start = FIRSTDATE
        histograms = histograms.filter(source__date__gte=start,
                                       source__date__lt=date)
    elif not month:
        date = datetime.date(int(year), 1, 1)
        histograms = histograms.filter(source__date__year=date.year)
    elif not day:
        date = datetime.date(int(year), int(month), 1)
        histograms = histograms.filter(source__date__year=date.year,
                                       source__date__month=date.month)
    elif not hour:
        date = datetime.date(int(year), int(month), int(day))
        histograms = histograms.filter(source__date=date)
    else:
        try:
            date = datetime.date(int(year), int(month), int(day))
            histogram = histograms.get(source__date=date)
            num_events = histogram.values[int(hour)]
        except DailyHistogram.DoesNotExist:
            num_events = 0

    if not validate_date(date):
        return HttpResponseNotFound()

    if not hour:
        num_events = sum([sum(histogram.values) for histogram in histograms])

    return json_dict(num_events)


def get_event_traces(request, station_number, ext_timestamp):
    """Get the traces for an event

    :param station_number: a station number identifier.
    :param ext_timestamp: extended timestamp (nanoseconds since UNIX epoch).
    :param raw: (optional, GET) if present get the raw trace, i.e. without
                subtracted baseline.

    :return: two or four traces.

    """
    ext_timestamp = int(ext_timestamp)
    raw = 'raw' in request.GET

    date = datetime.datetime.utcfromtimestamp(ext_timestamp / 1e9).date()
    if not validate_date(date):
        return HttpResponseNotFound()

    try:
        station = Station.objects.get(number=station_number)
        Summary.objects.get(station=station, date=date,
                            num_events__isnull=False)
    except Station.DoesNotExist:
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
