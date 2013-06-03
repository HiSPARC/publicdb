from django.http import HttpResponse, HttpResponseNotFound
from django.core import serializers

import json
from operator import itemgetter
import datetime

from django_publicdb.coincidences.models import *
from django_publicdb.analysissessions.models import *
from django_publicdb.inforecords.models import *
from django_publicdb.histograms.models import *

import os
import numpy
import scipy
from scipy import optimize

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

    :param station_id: a station number identifier.

    :return: dictionary containing info about the station. Most importantly,
             this contains information about the position of the station,
             including the position of the individual scintillators.

    """
    today = datetime.date.today()
    try:
        station = Station.objects.get(number=station_id)
        detector = (DetectorHisparc.objects.filter(station=station,
                                                   startdate__lte=today)
                                           .latest('startdate'))
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__lte=today)
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

    :return: list containing dictionaries which consist of the name and number
             of each station (matching the subcluster).

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

    :return: list of dictionaries containing the name and number of each
             station that has measured events on the given date.

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

    :return: list of dictionaries containing the name and number of each
             station that has measured weather data on the given date.

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

    :return: list of dictionaries containing the name and number of all
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

    :return: list of dictionaries containing the name and number of all
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

    :return: list of dictionaries containing the name and number of all countries.

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

def get_pulseheight_drift(request, station_id, plate_number,
                          year, month, day, number_of_days):

    requested_date = datetime.date(int(year), int(month), int(day))

    station_id   = int(station_id)
    plate_number = int(plate_number)

    if (plate_number < 1) or (plate_number > 4):
        return json_dict({
            'error' : "Platenumber (value = %s) is out of range, should be between 1 and 4" % plate_number
        })

    #---------------------------------------------------------------------------
    # Read in all data into these two dictionaries: t, mpv

    t   = []
    mpv = []

    for days in range(int(number_of_days)):

        fit_date = requested_date - datetime.timedelta(days=days)

        # Check path

        filepath = os.path.join(
            "/home/cblam/Projects/hisparc/data-quality/analysis",
            "%s_%s_%s.%s.pulseheights.dat" % (
                fit_date.year, fit_date.month, fit_date.day, station_id
            )
        )

        if not os.path.exists(filepath):
            print "Unable to get fit values. Path doesn't exist: %s" % filepath
            continue

        # Transform file format to dictionary

        with open(filepath, "r") as f:
            for line in f.readlines():
                # The stripping is primarily for removing the newline character
                # at the end
                line = line.strip()

                try:

                    # Assign values to readable variables

                    t0, station, numberOfPlate, entries = line.split(" ")[0:4]
                    fitCenter, fitRange                 = line.split(" ")[4:6]
                    peakFit, peakFitError               = line.split(" ")[6:8]
                    widthFit, widthFitError             = line.split(" ")[8:10]
                    chiSquare                           = line.split(" ")[10]

                    if int(numberOfPlate) + 1 != int(plate_number):
                        continue

                    # Make cuts

                    if chiSquare < 1.5:
                        continue

                    if fitRange < 45.0:
                        continue

                    print "%s %s %s" %( peakFit, fitRange, chiSquare)

                    #

                    t.append(float(t0))
                    mpv.append(float(peakFit))

                except:
                    raise
                    pass

            f.close()

    #return json_dict([t, mpv])

    #---------------------------------------------------------------------------
    # Preparing results

    t_array   = numpy.float_(t)
    mpv_array = numpy.float_(mpv)

    linear_fit = lambda p, t: p[0] + p[1]*t # Target function

    # Determine the drift by a linear fit

    errfunc = lambda p, t, y: linear_fit(p, t) - y # Distance to the target function

    p0 = [1.0, 1.0 / 86400.0] # Initial guess for the parameters
    p1, success = optimize.leastsq(errfunc, p0, args=(t_array, mpv_array))

    drift = p1[1] * 86400.0

    # Calculate the relative fluctuation

    relative_mpv = []

    for i in range(len(t)):
        relative_mpv.append( mpv[i] / linear_fit(p1, t[i]) )

    # Fit the relative fluctation with a gauss

    bins = numpy.arange(0.0, 2.0, 0.005)
    gauss = lambda x, N, m, s: N * scipy.stats.norm.pdf(x, m, s)

    frequency, bins = numpy.histogram(relative_mpv, bins=bins)
    x = (bins[:-1] + bins[1:]) / 2

    initial_N = 16
    initial_mean = 1
    initial_width = 0.03

    popt, pcov = scipy.optimize.curve_fit(gauss, x, frequency,
                           p0=(initial_N, initial_mean, initial_width))

    #---------------------------------------------------------------------------
    # Insert values into dictionary

    dict = {
        'station'        : station_id,
        'plate_number'   : plate_number,

        'year'           : requested_date.year,
        'month'          : requested_date.month,
        'day'            : requested_date.day,

        'number_of_selected_days'  : len(t),
        'number_of_requested_days' : number_of_days,

        'fit_offset'     : p1[0],
        'fit_slope'      : p1[1],

        'drift_per_day'  : drift,

        'timestamp'      : t,
        'mpv'            : mpv,

        'relative_mean'  : popt[1],
        'relative_width' : popt[2],

        # Debug
        #'relative_mpv'   : relative_mpv,
        #'frequency'      : frequency.tolist(),
        #'x'              : x.tolist()
    }

    #---------------------------------------------------------------------------
    # Return

    return json_dict(dict)

def get_pulseheight_drift_last_14_days(request, station_id, plate_number):
    today = datetime.date.today()

    return get_pulseheight_drift(request, station_id, plate_number,
                                 today.year, today.month, today.day, 14)

def get_pulseheight_drift_last_30_days(request, station_id, plate_number):
    today = datetime.date.today()

    return get_pulseheight_drift(request, station_id, plate_number,
                                 today.year, today.month, today.day, 30)

def get_pulseheight_fit(request, station_id, plate_number, year=None, month=None, day=None):
    """Get fit values of the pulseheight distribution for a station on a given day

    Retrieve fit values of the pulseheight distribution. The fitting has to be
    done before and stored somewhere. This function retrieves the fit values from
    storage and returns to the client. Returns an error meesage if the values
    are not found on storage.

    :param station_id: a station number identifier.
    :param plate_number: plate number in the range 1..4
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: dictionary containing fit results of the specified station, plate
             and date

    """

    #---------------------------------------------------------------------------
    # Initialize
    #---------------------------------------------------------------------------

    station_id   = int(station_id)
    plate_number = int(plate_number)

    if year == None and month == None and day == None:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        year  = yesterday.year
        month = yesterday.month
        day   = yesterday.day

    year  = int(year)
    month = int(month)
    day   = int(day)

    dict = {
        'station'      : station_id,
        'plate_number' : plate_number,
        'year'         : year,
        'month'        : month,
        'day'          : day
    }

    class nagios:
        ok = (0, 'OK')
        warning = (1, 'WARNING')
        critical = (2, 'CRITICAL')
        unknown = (3, 'UNKNOWN')

    #---------------------------------------------------------------------------
    # Check path
    #---------------------------------------------------------------------------

    filepath = os.path.join(
        "/home/cblam/Projects/hisparc/data-quality/analysis",
        "%s_%s_%s.%s.pulseheights.dat" % (
            year, month, day, station_id
        )
    )

    if not os.path.exists(filepath):
        dict.update({
            "nagios": nagios.unknown,
            "error" : "Unable to get fit values due to missing data file. Please make sure the following path does exist: %s" % filepath
        })

        return json_dict(dict)

    #---------------------------------------------------------------------------
    # Extract data to dictionary
    #---------------------------------------------------------------------------

    with open(filepath, "r") as f:
        for line in f.readlines():
            # The stripping is primarily for removing the newline character
            # at the end
            line = line.strip()

            try:
                t0, station, numberOfPlate, entries = line.split(" ")[0:4]
                initialPeak, initialWidth           = line.split(" ")[4:6]
                peakFit, peakFitError               = line.split(" ")[6:8]
                widthFit, widthFitError             = line.split(" ")[8:10]
                chiSquare                           = line.split(" ")[10]
            except:
                dict.update({
                    "nagios": nagios.unknown,
                    "error" : "Data file has been opened, but error in extracting values from line"
                })
                return json_dict(dict)

            if int(numberOfPlate)+1 != int(plate_number):
                continue

            try:
                dict.update({
                    "timestamp"       : int(t0),
                    "entries"         : int(float(entries)),

                    "initial_mpv"     : float(initialPeak),
                    "initial_width"   : float(initialWidth),

                    "fit_mpv"         : float(peakFit),
                    "fit_mpv_error"   : float(peakFitError),
                    "fit_width"       : float(widthFit),
                    "fit_width_error" : float(widthFitError),
                    "chi_square"      : float(chiSquare)
                })
            except:
                dict.update({
                    "nagios": nagios.unknown,
                    "error" : "Data file has been found, but error in converting data to numbers"
                })
                return json_dict(dict)

            break

        f.close()

    if "fit_mpv" not in dict:
        dict.update({
            "nagios": nagios.unknown,
            'error' : "Data file exists but no fit found for plate. Probably the station doesn't have this plate."
        })
        return json_dict(dict)

    #---------------------------------------------------------------------------
    # Data quality
    #---------------------------------------------------------------------------

    # Based on chi2 of the fit

    if dict["chi_square"] < 1.5:
        dict.update({
            "nagios" : nagios.critical,
            "quality": "Chi2 of the fit is smaller than 1.5: %.1f" % dict["chi_square"]
        })
        return json_dict(dict)

    # Based on the fit range (= initial_width)

    if dict["initial_width"] < 45:
        dict.update({
            "nagios" : nagios.critical,
            "quality": "Fit range is smaller than 45 ADC: %.1f ADC" % dict["initial_width"]
        })
        return json_dict(dict)

    # Based on MPV and 4*sigma

    station   = Station.objects.get(number=station_id)
    threshold = MonitorPulseheightThresholds.objects.get(station=station, plate=plate_number)

    lower_bound = threshold.mpv_mean * (1 - 4*threshold.mpv_sigma)
    upper_bound = threshold.mpv_mean * (1 + 4*threshold.mpv_sigma)

    if dict["fit_mpv"] < lower_bound or dict["fit_mpv"] > upper_bound:
        dict.update({
            "nagios" : nagios.critical,
            "quality": "Fitted MPV is outside bounds (%.1f;%.1f): %.1f" % (
                lower_bound, upper_bound, dict["fit_mpv"]
            )
        })
        return json_dict(dict)

    # Everything seems to be a-ok

    dict.update({
        "nagios" : nagios.ok,
        "quality": "Fitted MPV is within bounds (%.1f;%.1f): %.1f" % (
            lower_bound, upper_bound, dict["fit_mpv"]
        )
    })
    return json_dict(dict)

def has_data(request, station_id, year=None, month=None, day=None):
    """Check for presence of cosmic ray data

    Find out if the given station has measured shower data, either on a
    specific date, or at all.

    :param station_id: a stationn number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: boolean, True if the given station has shower data, False otherwise.

    """
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
    """Check for presence of weather data

    Find out if the given station has measured weather data, either on a
    specific date, or at all.

    :param station_id: a stationn number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: boolean, True if the given station has weather data, False otherwise.

    """
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
    """Get station config settings

    Retrieve the entire configuration of a station. If no date if given the
    latest config will be sent, otherwise the latest on or before the given
    date.

    :param station_id: a stationn number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: dictionary containing the entire configuration from
             the HiSPARC DAQ.

    """
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
    """Get total number of events for a station

    Retrieve the number of events that a station has measured during its
    entire operation. The following functions each dig a little deeper,
    going for a shorter time period.

    :param station_id: a stationn number identifier.

    :return: integer containing the total number of events ever recorded by
             the given station.

    """
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
    """Get total number of events for a station in the given year

    Retrieve the total number of events that a station has measured during
    the given year.

    :param station_id: a station number identifier.
    :param year: the year for which the number of events is to be given.

    :return: integer containing the total number of events recorded by the
             given station in the given year.

    """
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
    """Get total number of events for a station in the given month of a year

    Retrieve the total number of events that a station has measured during the given
    month.

    :param station_id: a station number identifier.
    :param year: the year in which to look for the month.
    :param month: the month for which the number of events is to be given.

    :return: integer containing the total number of events recorded by the
             given station in the given month of the given year.

    """
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
    """Get total number of events for a station on a given date

    Retrieve the total number of events that a station has measured on a date.

    :param station_id: a station number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.

    :return: integer denoting the number of events recorded by the station
             on the given date.

    """
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
    """Get number of events for a station in an hour on the given date

    Retrieve the total number of events that a station has measured in that
    hour.

    :param station_id: a station number identifier.
    :param year: the year part of the date.
    :param month: the month part of the date.
    :param day: the day part of the date.
    :param hour: the hour for which the number of events is to be retrieved.

    :return: integer giving the number of events recorded by the station
             in hour on date.

    """
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
    """Check if date is outside HiSPARC project range

    If not valid, a 404 (Not Found) should be returned to the user.

    :return: boolean, True if the date is in the range, False otherwise.

    """
    return datetime.date(2002, 1, 1) <= date <= datetime.date.today()

