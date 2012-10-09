from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.conf import settings
from django.db.models import Q

from operator import itemgetter
import calendar
import os
from numpy import arange, pi, sin, cos, radians, sqrt, arctan2, array, genfromtxt
import datetime
import time
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError
from socket import timeout

from django_publicdb.histograms.models import *
from django_publicdb.inforecords.models import *


def stations(request):
    """Show a list of stations, ordered by subcluster"""

    clusters = []
    for cluster in Cluster.objects.all():
        stations = []
        for station in Station.objects.filter(cluster=cluster):
            try:
                Summary.objects.filter(station=station)[0]
                link = station.number
            except IndexError:
                link = None

            stations.append({'number': station.number,
                             'name': station.name,
                             'link': link})
        clusters.append({'name': cluster.name, 'stations': stations})


    return render_to_response('stations.html', {'clusters': clusters},
                              context_instance=RequestContext(request))


def stations_by_country(request):
    """Show a list of stations, ordered by country, cluster and subcluster"""

    countries = []
    for country in Country.objects.all():
        clusters = []
        for cluster in Cluster.objects.filter(country=country):
            stations = []
            for station in Station.objects.filter(cluster=cluster):
                try:
                    Summary.objects.filter(station=station)[0]
                    link = station.number
                except IndexError:
                    link = None

                stations.append({'number': station.number,
                                 'name': station.name,
                                 'link': link})
            clusters.append({'name': cluster.name, 'stations': stations})
        countries.append({'name': country.name, 'number': country.number, 'clusters': clusters})

    countries = sorted(countries, key=itemgetter('number'))

    return render_to_response('stations_by_country.html', {'countries': countries},
                              context_instance=RequestContext(request))


def stations_by_number(request):
    """Show a list of stations, ordered by number"""

    stations = []
    for station in Station.objects.all():
        try:
            Summary.objects.filter(station=station)[0]
            link = station.number
        except IndexError:
            link = None

        stations.append({'number': station.number,
                         'name': station.name,
                         'link': link})

    return render_to_response('stations_by_number.html',
                              {'stations': stations},
                              context_instance=RequestContext(request))


def stations_by_name(request):
    """Show a list of stations, ordered by station name"""

    stations = []
    for station in Station.objects.all():
        try:
            Summary.objects.filter(station=station)[0]
            link = station.number
        except IndexError:
            link = None

        stations.append({'number': station.number,
                         'name': station.name,
                         'link': link})

    stations = sorted(stations, key=itemgetter('name'))

    return render_to_response('stations_by_name.html', {'stations': stations},
                              context_instance=RequestContext(request))


def stations_on_map(request):
    """Show all stations on a map"""

    today = datetime.datetime.utcnow()
    tomorrow = today + datetime.timedelta(days=1)
    stations = []
    for detector in DetectorHisparc.objects.exclude(enddate__lt=today):
        try:
            Summary.objects.filter(station=detector.station)[0]
            link = detector.station.number
        except IndexError:
            link = None

        if link:
            stations.append({'number': detector.station.number,
                             'name': detector.station.name,
                             'cluster': detector.station.cluster,
                             'link': link,
                             'longitude': detector.longitude,
                             'latitude': detector.latitude,
                             'altitude': detector.height})

    return render_to_response('stations_on_map.html', {'stations': stations},
                              context_instance=RequestContext(request))


def station_page(request, station_id, year, month, day):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)
    year = int(year)
    month = int(month)
    day = int(day)

    station = get_object_or_404(Station, number=station_id)

    # Use yesterday and tomorrow to add previous/next links
    yesterday = datetime.date(year, month, day) - datetime.timedelta(days=1)
    tomorrow = datetime.date(year, month, day) + datetime.timedelta(days=1)

    try:
        previous = (Summary.objects.filter(Q(station__number=station_id),
                                           Q(num_events__isnull=False) |
                                           Q(num_weather__isnull=False))
                                   .filter(date__lte=yesterday)
                                   .latest('date')).date
    except Summary.DoesNotExist:
        previous = None

    try:
        next = (Summary.objects.filter(Q(station__number=station_id),
                                       Q(num_events__isnull=False) |
                                       Q(num_weather__isnull=False))
                               .filter(date__gte=tomorrow)
                               .order_by('date'))[0].date
    except IndexError:
        next = None

    try:
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__lt=tomorrow)
                                       .latest('timestamp'))
        if config.slv_version.count('0') == 2:
            has_slave = False
        else:
            has_slave = True
    except Configuration.DoesNotExist:
        config = None
        has_slave = False

    thismonth = nav_calendar(station, year, month)
    month_list = nav_months(station, year)
    year_list = nav_years(station)
    current_date = {'year': year,
                    'month': calendar.month_name[month][:3],
                    'day': day}

    eventhistogram = create_histogram('eventtime', station, year, month, day)
    pulseheighthistogram = create_histogram('pulseheight', station,
                                            year, month, day)
    pulseintegralhistogram = create_histogram('pulseintegral', station,
                                              year, month, day)
    barometerdata = plot_dataset('barometer', station, year, month, day)
    temperaturedata = plot_dataset('temperature', station, year, month, day)

    return render_to_response('station_page.html',
        {'station': station,
         'date': datetime.date(year, month, day),
         'config': config,
         'has_slave': has_slave,
         'eventhistogram': eventhistogram,
         'pulseheighthistogram': pulseheighthistogram,
         'pulseintegralhistogram': pulseintegralhistogram,
         'barometerdata': barometerdata,
         'temperaturedata': temperaturedata,
         'thismonth': thismonth,
         'month_list': month_list,
         'year_list': year_list,
         'current_date': current_date,
         'prev': previous,
         'next': next,
         'link': (station_id, year, month, day)},
        context_instance=RequestContext(request))


def station(request, station_id):
    """Show most recent histograms for a particular station"""

    summary = (Summary.objects.filter(Q(station__number=station_id),
                                      Q(num_events__isnull=False) |
                                      Q(num_weather__isnull=False))
                              .filter(date__lt=datetime.date.today())
                              .latest('date'))
    return redirect(station_page, station_id=str(station_id),
                    year=str(summary.date.year),
                    month=str(summary.date.month),
                    day=str(summary.date.day))


def get_eventtime_histogram_source(request, station_id, year, month, day):
    data = get_histogram_source(station_id, year, month, day, 'eventtime')
    response = render_to_response('source_eventtime_histogram.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=eventtime-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response


def get_pulseheight_histogram_source(request, station_id, year, month, day):
    data = get_histogram_source(station_id, year, month, day, 'pulseheight')
    response = render_to_response('source_pulseheight_histogram.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=pulseheight-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response


def get_pulseintegral_histogram_source(request, station_id, year, month, day):
    data = get_histogram_source(station_id, year, month, day, 'pulseintegral')
    response = render_to_response('source_pulseintegral_histogram.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=pulseintegral-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response


def get_barometer_dataset_source(request, station_id, year, month, day):
    data = get_dataset_source(station_id, year, month, day, 'barometer')
    response = render_to_response('source_barometer_dataset.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=barometer-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response


def get_temperature_dataset_source(request, station_id, year, month, day):
    data = get_dataset_source(station_id, year, month, day, 'temperature')
    response = render_to_response('source_temperature_dataset.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=temperature-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response


def get_histogram_source(station_id, year, month, day, type):
    histogram = DailyHistogram.objects.get(
            source__station__number=int(station_id),
            source__date=datetime.date(int(year), int(month), int(day)),
            type__slug=type)
    if type == 'eventtime':
        return zip(histogram.bins, histogram.values)
    else:
        return zip(histogram.bins, *histogram.values)


def get_dataset_source(station_id, year, month, day, type):
    dataset = DailyDataset.objects.get(
            source__station__number=int(station_id),
            source__date=datetime.date(int(year), int(month), int(day)),
            type__slug=type)
    return zip(dataset.x, dataset.y)


def create_histogram(type, station, year, month, day):
    """Create a histogram object"""

    date = datetime.date(year, month, day)
    source = get_object_or_404(Summary, station=station, date=date)
    type = HistogramType.objects.get(slug__exact=type)

    try:
        histogram = DailyHistogram.objects.get(source=source, type=type)
    except DailyHistogram.DoesNotExist:
        return None

    plot_object = create_plot_object(histogram.bins[:-1], histogram.values,
                                     type.bin_axis_title,
                                     type.value_axis_title)
    return plot_object


def plot_dataset(type, station, year, month, day, log=False):
    """Create a dataset plot object"""

    date = datetime.date(year, month, day)
    source = get_object_or_404(Summary, station=station, date=date)
    type = DatasetType.objects.get(slug__exact=type)

    try:
        dataset = DailyDataset.objects.get(source=source, type=type)
        plot_object = create_plot_object(dataset.x, dataset.y,
                                         type.x_axis_title, type.y_axis_title)
    except DailyDataset.DoesNotExist:
        if type.slug in ('temperature', 'barometer'):
            dataset = get_KNMI_weather(station, date, type)
            plot_object = create_plot_object(dataset['x'], dataset['y'],
                                             type.x_axis_title, type.y_axis_title,
                                             'KNMI')
        else:
            return None
    return plot_object


def get_KNMI_weather(station, date, type):
    """Get weather data from closest KNMI station"""

    url = 'http://www.knmi.nl/klimatologie/uurgegevens/getdata_uur.cgi'

    tomorrow = date + datetime.timedelta(days=1)

    try:
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__lt=tomorrow)
                                       .latest('timestamp'))
        knmi_station = closest_KNMI(config.gps_longitude, config.gps_latitude)
    except Configuration.DoesNotExist:
        knmi_station = 260

    params = urlencode({'start': date.strftime('%Y%m%d') + '01',
                        'end': date.strftime('%Y%m%d') + '24', 'inseason': 1,
                        'vars': 'T:P', 'stns': knmi_station, 'zipped': 0})
    response = urlopen(url, params)
    res = genfromtxt(response, delimiter=',', filling_values=-999,
                     dtype=([('station', 'u2'), ('date', 'u4'), ('hour', 'u1'),
                             ('temperature', 'f4'), ('barometer', 'f4')]))

    dataset = {'x': res['hour'].tolist(), 'y': res[type.slug].tolist()}

    return dataset


def closest_KNMI(lon1, lat1):
    """Find closest KNMI Station"""
    KNMI = ((210, 4.419, 52.165), (225, 4.575, 52.463), (235, 4.785, 52.924),
            (240, 4.774, 52.301), (242, 4.942, 53.255), (249, 4.979, 52.644),
            (251, 5.346, 53.393), (257, 4.603, 52.506), (260, 5.177, 52.101),
            (265, 5.274, 52.130), (267, 5.384, 52.896), (269, 5.526, 52.458),
            (270, 5.755, 53.225), (273, 5.889, 52.703), (275, 5.888, 52.061),
            (277, 6.196, 53.409), (278, 6.263, 52.437), (279, 6.575, 52.750),
            (280, 6.586, 53.125), (283, 6.650, 52.073), (286, 7.150, 53.196),
            (290, 6.897, 52.273), (310, 3.596, 51.442), (319, 3.862, 51.226),
            (323, 3.884, 51.527), (330, 4.124, 51.993), (340, 4.349, 51.448),
            (344, 4.444, 51.955), (348, 4.927, 51.972), (350, 4.933, 51.568),
            (356, 5.145, 51.858), (370, 5.414, 51.446), (375, 5.706, 51.657),
            (377, 5.764, 51.197), (380, 5.768, 50.910), (391, 6.196, 51.498))

    KNMI_stations = [{'stn': x[0], 'lon': x[1], 'lat': x[2]} for x in KNMI]
    stns = array([KNMI_station['stn'] for KNMI_station in KNMI_stations])
    lat2 = array([KNMI_station['lat'] for KNMI_station in KNMI_stations])
    lon2 = array([KNMI_station['lon'] for KNMI_station in KNMI_stations])

    R = 6371  # km Radius of earth
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2
    c = 2 * arctan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    closet = stns[min(enumerate(distance), key=itemgetter(1))[0]]

    return closet


def create_plot_object(x_values, y_series, x_label, y_label, source='HiSPARC'):
    if type(y_series[0]) != list:
        y_series = [y_series]

    data = [[[xv, yv] for xv, yv in zip(x_values, y_values)] for
            y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label,
                   'source': source}
    return plot_object


def nav_calendar(station, theyear, themonth):
    """Create a month calendar with links"""

    month = calendar.Calendar().monthdatescalendar(theyear, themonth)
    month_name = '%s %d' % (calendar.month_name[themonth], theyear)
    days_names = calendar.weekheader(3).split(' ')

    weeks = []
    for week in month:
        days = []
        for day in week:
            if day.month == themonth:
                try:
                    summary = (Summary.objects
                                      .get(Q(station=station),
                                           Q(date=day),
                                           Q(num_events__isnull=False) |
                                           Q(num_weather__isnull=False)))
                except Summary.DoesNotExist:
                    link = None
                else:
                    link = (station.number, theyear, themonth, day.day)
                days.append({'day': day.day, 'link': link})
            else:
                days.append('')
        weeks.append(days)

    return {'month': month_name, 'days': days_names, 'weeks': weeks}


def nav_months(station, theyear):
    """Create list of months with links"""

    date_list = (Summary.objects.filter(Q(station=station),
                                        Q(date__year=theyear),
                                        Q(num_events__isnull=False) |
                                        Q(num_weather__isnull=False))
                        .dates('date', 'month'))

    month_list = [{'month': calendar.month_name[i][:3]} for i in range(1, 13)]
    for date in date_list:
        first_day = (Summary.objects.filter(station=station,
                                            date__year=date.year,
                                            date__month=date.month)
                            .dates('date', 'day')[0])
        link = (station.number, date.year, date.month, first_day.day)
        month_list[date.month - 1]['link'] = link

    return month_list


def nav_years(station):
    """Create list of previous years"""

    date_list = (Summary.objects.filter(Q(station=station),
                                        Q(num_events__isnull=False) |
                                        Q(num_weather__isnull=False))
                        .dates('date', 'year'))

    year_list = []
    for date in date_list:
        first_day = (Summary.objects.filter(station=station,
                                            date__year=date.year)
                            .dates('date', 'day')[0])
        link = (station.number, date.year, first_day.month, first_day.day)
        year_list.append({'year': date.year, 'link': link})

    return year_list
