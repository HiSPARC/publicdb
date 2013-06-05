from django.shortcuts import (render_to_response, get_object_or_404,
                              get_list_or_404, redirect)
from django.template import RequestContext
from django.conf import settings
from django.db.models import Q

from operator import itemgetter
import calendar
from numpy import arange, pi, sin
import datetime
import time

from django_publicdb.histograms.models import *
from django_publicdb.inforecords.models import *
from nagios import *


def stations(request):
    """Show the default station list"""

    return redirect(stations_by_country)


def stations_by_country(request):
    """Show a list of stations, ordered by country, cluster and subcluster"""

    down, problem, up = status_lists()
    countries = []
    for country in Country.objects.all():
        clusters = []
        for cluster in Cluster.objects.filter(country=country, parent=None):
            subclusters = []
            for subcluster in Cluster.objects.filter(parent=cluster):
                stations = []
                for station in Station.objects.filter(cluster=subcluster):
                    if station_has_data(station):
                        link = station.number
                    else:
                        link = None
                    status = get_station_status(station, down, problem, up)

                    stations.append({'number': station.number,
                                     'name': station.name,
                                     'link': link,
                                     'status': status})
                subclusters.append({'name': subcluster.name,
                                    'stations': stations})
            stations = []
            for station in Station.objects.filter(cluster=cluster):
                if station_has_data(station):
                    link = station.number
                else:
                    link = None
                status = get_station_status(station, down, problem, up)

                stations.append({'number': station.number,
                                 'name': station.name,
                                 'link': link,
                                 'status': status})
            clusters.append({'name': cluster.name,
                             'subclusters': subclusters,
                             'stations': stations})
        countries.append({'number': country.number,
                          'name': country.name,
                          'clusters': clusters})

    countries = sorted(countries, key=itemgetter('number'))

    return render_to_response('stations_by_country.html',
                              {'countries': countries},
                              context_instance=RequestContext(request))


def stations_by_number(request):
    """Show a list of stations, ordered by number"""

    down, problem, up = status_lists()
    stations = []
    for station in Station.objects.all():
        if station_has_data(station):
            link = station.number
        else:
            link = None
        status = get_station_status(station, down, problem, up)

        stations.append({'number': station.number,
                         'name': station.name,
                         'link': link,
                         'status': status})

    return render_to_response('stations_by_number.html',
                              {'stations': stations},
                              context_instance=RequestContext(request))


def stations_by_name(request):
    """Show a list of stations, ordered by station name"""

    down, problem, up = status_lists()
    stations = []
    for station in Station.objects.all():
        if station_has_data(station):
            link = station.number
        else:
            link = None
        status = get_station_status(station, down, problem, up)

        stations.append({'number': station.number,
                         'name': station.name,
                         'link': link,
                         'status': status})

    stations = sorted(stations, key=itemgetter('name'))

    return render_to_response('stations_by_name.html', {'stations': stations},
                              context_instance=RequestContext(request))


def stations_on_map(request, country=None, cluster=None, subcluster=None):
    """Show all stations from a subcluster on a map"""

    down, problem, up = status_lists()
    today = datetime.datetime.utcnow()

    if country:
        get_object_or_404(Country, name=country)
        if cluster:
            get_object_or_404(Cluster, name=cluster, parent=None, country__name=country)
            if subcluster:
                if cluster == subcluster:
                    get_object_or_404(Cluster, name=subcluster, parent=None)
                else:
                    get_object_or_404(Cluster, name=subcluster, parent__name=cluster)
                focus = Cluster.objects.filter(name=subcluster).values_list('name', flat=True)
            else:
                focus = [Cluster.objects.get(name=cluster, parent=None).name]
                focus.extend(Cluster.objects.filter(parent__name=cluster).values_list('name', flat=True))
        else:
            focus = Cluster.objects.filter(country__name=country).values_list('name', flat=True)
    else:
        focus = Cluster.objects.all().values_list('name', flat=True)

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in Station.objects.filter(cluster=subcluster,
                                              pc__is_active=True,
                                              pc__is_test=False):
            detector = (DetectorHisparc.objects.filter(station=station,
                                                       startdate__lte=today)
                                               .latest('startdate'))
            link = station_has_data(station)
            status = get_station_status(station, down, problem, up)
            stations.append({'number': station.number,
                             'name': station.name,
                             'cluster': station.cluster,
                             'link': link,
                             'status': status,
                             'longitude': detector.longitude,
                             'latitude': detector.latitude,
                             'altitude': detector.height})
        subclusters.append({'name': subcluster.name,
                            'stations': stations})

    return render_to_response('stations_on_map.html',
        {'subclusters': subclusters,
         'focus': focus},
        context_instance=RequestContext(request))


def station_data(request, station_id, year, month, day):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)
    year = int(year)
    month = int(month)
    day = int(day)
    date = datetime.date(year, month, day)

    station = get_object_or_404(Station, number=station_id)
    data = get_object_or_404(Summary.objects.filter(Q(station=station),
                                                    Q(date=date),
                                                    Q(num_events__isnull=False) |
                                                    Q(num_weather__isnull=False)))

    # Use next_day and prev_day to add previous/next links
    prev_day = date - datetime.timedelta(days=1)
    next_day = date + datetime.timedelta(days=1)

    try:
        previous = (Summary.objects.filter(Q(station=station),
                                           Q(num_events__isnull=False) |
                                           Q(num_weather__isnull=False),
                                           date__gte=datetime.date(2002, 1, 1),
                                           date__lte=prev_day)
                                   .latest('date')).date
    except Summary.DoesNotExist:
        previous = None

    try:
        next = (Summary.objects.filter(Q(station=station),
                                       Q(num_events__isnull=False) |
                                       Q(num_weather__isnull=False),
                                       date__gte=next_day,
                                       date__lte=datetime.date.today())
                               .order_by('date'))[0].date
    except IndexError:
        next = None

    try:
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__lt=next_day)
                                       .latest('timestamp'))
        if config.slv_version.count('0') == 2:
            has_slave = False
        else:
            has_slave = True
        has_config = True
    except Configuration.DoesNotExist:
        config = None
        has_slave = False
        has_config = False

    try:
        is_active = Pc.objects.filter(station=station)[0].is_active
    except IndexError:
        is_active = False

    thismonth = nav_calendar(station, year, month)
    month_list = nav_months(station, year)
    year_list = nav_years(station)
    current_date = {'year': year,
                    'month': calendar.month_name[month][:3],
                    'day': day}

    eventhistogram = create_histogram('eventtime', station, date)
    pulseheighthistogram = create_histogram('pulseheight', station, date)
    pulseintegralhistogram = create_histogram('pulseintegral', station, date)
    barometerdata = plot_dataset('barometer', station, date)
    temperaturedata = plot_dataset('temperature', station, date)

    return render_to_response('station_data.html',
        {'station': station,
         'date': date,
         'tomorrow': date + datetime.timedelta(days=1),
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
         'link': (station_id, year, month, day),
         'has_data': True,
         'is_active': is_active,
         'has_config': has_config},
        context_instance=RequestContext(request))


def station_status(request, station_id):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)

    station = get_object_or_404(Station, number=station_id)
    pc = get_object_or_404(Pc, station=station, is_active=True)

    has_data = station_has_data(station)

    try:
        Configuration.objects.filter(source__station=station)[0]
        has_config = True
    except IndexError:
        has_config = False

    return render_to_response('station_status.html',
        {'station': station,
         'pc': pc,
         'has_data': has_data,
         'is_active': True,
         'has_config': has_config},
        context_instance=RequestContext(request))


def station_config(request, station_id):
    """Show configuration history for a particular station"""

    station_id = int(station_id)

    station = get_object_or_404(Station, number=station_id)
    configs = get_list_or_404(Configuration.objects.order_by('timestamp'),
                              source__station=station,
                              timestamp__gte=datetime.date(2002, 1, 1),
                              timestamp__lte=datetime.date.today())

    has_data = station_has_data(station)

    try:
        is_active = Pc.objects.filter(station=station)[0].is_active
    except IndexError:
        is_active = False

    config = configs[-1]
    if config.slv_version.count('0') == 2:
        has_slave = False
    else:
        has_slave = True

    voltagegraph = plot_config('voltage', configs)
    currentgraph = plot_config('current', configs)
    altitudegraph = plot_config('altitude', configs)
    gpstrack = get_gpspositions(configs)

    return render_to_response('station_config.html',
        {'station': station,
         'config': config,
         'voltagegraph': voltagegraph,
         'currentgraph': currentgraph,
         'altitudegraph': altitudegraph,
         'gpstrack': gpstrack,
         'has_slave': has_slave,
         'has_data': has_data,
         'is_active': is_active,
         'has_config': True},
        context_instance=RequestContext(request))


def station(request, station_id):
    """Show most recent histograms for a particular station"""

    summary = (Summary.objects.filter(Q(station__number=station_id),
                                      Q(num_events__isnull=False) |
                                      Q(num_weather__isnull=False),
                                      date__gte=datetime.date(2002, 1, 1),
                                      date__lte=datetime.date.today())
                              .latest('date'))
    return redirect(station_data,
                    station_id=str(station_id),
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


def get_voltage_config_source(request, station_id):
    data = get_config_source(station_id, 'voltage')
    response = render_to_response('source_voltage_config.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=voltage-%s.csv' % station_id)
    return response


def get_current_config_source(request, station_id):
    data = get_config_source(station_id, 'current')
    response = render_to_response('source_current_config.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=current-%s.csv' % station_id)
    return response


def get_gps_config_source(request, station_id):
    data = get_config_source(station_id, 'gps')
    response = render_to_response('source_gps_config.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=gps-%s.csv' % station_id)
    return response


def get_histogram_source(station_id, year, month, day, type):
    date = datetime.date(int(year), int(month), int(day))
    histogram = get_object_or_404(DailyHistogram,
                                  source__station__number=int(station_id),
                                  source__date=date,
                                  type__slug=type)
    if type == 'eventtime':
        return zip(histogram.bins, histogram.values)
    else:
        return zip(histogram.bins, *histogram.values)


def get_dataset_source(station_id, year, month, day, type):
    date = datetime.date(int(year), int(month), int(day))
    dataset = get_object_or_404(DailyDataset,
                                source__station__number=int(station_id),
                                source__date=date,
                                type__slug=type)
    return zip(dataset.x, dataset.y)


def get_config_source(station_id, type):
    configs = (Configuration.objects.filter(source__station__number=station_id,
                                            timestamp__gte=datetime.date(2002, 1, 1),
                                            timestamp__lte=datetime.date.today())
                                    .order_by('timestamp'))
    if type == 'voltage':
        data = configs.values_list('timestamp', 'mas_ch1_voltage', 'mas_ch2_voltage', 'slv_ch1_voltage', 'slv_ch2_voltage')
        data = [[calendar.timegm(row[0].utctimetuple()), row[1], row[2], row[3], row[4]] for row in data]
    elif type == 'current':
        data = configs.values_list('timestamp', 'mas_ch1_current', 'mas_ch2_current', 'slv_ch1_current', 'slv_ch2_current')
        data = [[calendar.timegm(row[0].utctimetuple()), row[1], row[2], row[3], row[4]] for row in data]
    elif type == 'gps':
        data = configs.values_list('timestamp', 'gps_latitude', 'gps_longitude', 'gps_altitude')
        data = [[calendar.timegm(row[0].utctimetuple()), row[1], row[2], row[3]] for row in data]
    else:
        data = None

    return data


def create_histogram(type, station, date):
    """Create a histogram object"""

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


def plot_dataset(type, station, date, log=False):
    """Create a dataset plot object"""

    source = get_object_or_404(Summary, station=station, date=date)
    type = DatasetType.objects.get(slug__exact=type)

    try:
        dataset = DailyDataset.objects.get(source=source, type=type)
    except DailyDataset.DoesNotExist:
        return None

    plot_object = create_plot_object(dataset.x, dataset.y, type.x_axis_title,
                                     type.y_axis_title)
    return plot_object


def plot_config(type, configs):
    """Create a plot object from station configs"""

    timestamps = [calendar.timegm(config.timestamp.utctimetuple())
                  for config in configs]
    x_label = 'Date (month/year)'

    if type == 'voltage':
        values = [[config.mas_ch1_voltage, config.mas_ch2_voltage,
                   config.slv_ch1_voltage, config.slv_ch2_voltage]
                  for config in configs]
        values = zip(*values)
        y_label = 'PMT Voltage (V)'
    elif type == 'current':
        values = [[config.mas_ch1_current, config.mas_ch2_current,
                   config.slv_ch1_current, config.slv_ch2_current]
                  for config in configs]
        values = zip(*values)
        y_label = 'PMT Current (mA)'
    if type == 'altitude':
        values = [config.gps_altitude for config in configs]
        y_label = 'Altitude (m)'
    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def get_gpspositions(configs):
    """Get all unique gps positions from the configs"""

    gps = [(config.gps_longitude, config.gps_latitude) for config in configs
           if config.gps_longitude != 0.0 and config.gps_latitude != 0.0]
    return set(gps)


def create_plot_object(x_values, y_series, x_label, y_label):
    if type(y_series[0]) != list and type(y_series[0]) != tuple:
            y_series = [y_series]
    data = [[[xv, yv] for xv, yv in zip(x_values, y_values)] for
            y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label}
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
                    link = (station.number, theyear, themonth, day.day)
                except Summary.DoesNotExist:
                    link = None
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
        first_day = (Summary.objects.filter(Q(station=station),
                                            Q(date__year=date.year),
                                            Q(date__month=date.month),
                                            Q(num_events__isnull=False) |
                                            Q(num_weather__isnull=False))
                            .dates('date', 'day')[0])
        link = (station.number, date.year, date.month, first_day.day)
        month_list[date.month - 1]['link'] = link

    return month_list


def nav_years(station):
    """Create list of previous years"""

    valid_years = (Summary.objects.filter(Q(station=station),
                                          Q(num_events__isnull=False) |
                                          Q(num_weather__isnull=False),
                                          date__gte=datetime.date(2002, 1, 1),
                                          date__lte=datetime.date.today())
                          .dates('date', 'year'))
    valid_years = [date.year for date in valid_years]

    year_list = []
    for year in range(valid_years[0], valid_years[-1] + 1):
        if year in valid_years:
            first_day = (Summary.objects.filter(Q(station=station),
                                                Q(date__year=year),
                                                Q(num_events__isnull=False) |
                                                Q(num_weather__isnull=False))
                                .dates('date', 'day')[0])
            link = (station.number, year, first_day.month, first_day.day)
            year_list.append({'year': year, 'link': link})
        else:
            year_list.append({'year': year, 'link': None})
    return year_list


def station_has_data(station):
    """Check if there is valid event or weather data for the given station

    :param station: Station object for which to check.

    :return: boolean indicating if the station has recorded data, either
             weather or shower, between 2002 and now.

    """
    try:
        Summary.objects.filter(Q(station=station),
                               Q(num_events__isnull=False) |
                               Q(num_weather__isnull=False),
                               date__gte=datetime.date(2002, 1, 1),
                               date__lte=datetime.date.today())[0]
        has_data = True
    except IndexError:
        has_data = False

    return has_data


def help(request):
    """Show the static help page"""
    return render_to_response('help.html',
                              context_instance=RequestContext(request))
