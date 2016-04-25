from django.shortcuts import (render, get_object_or_404,
                              get_list_or_404, redirect)
from django.http import Http404
from django.db.models import Q

from collections import OrderedDict
from operator import itemgetter
from itertools import izip, groupby
import calendar
import datetime
from cStringIO import StringIO
import csv

from numpy import arange, nan

from sapphire.transformations import clock

from ..histograms.models import (DailyHistogram, DailyDataset, Configuration,
                                 NetworkHistogram, HistogramType, DatasetType,
                                 DetectorTimingOffset, Summary, NetworkSummary)
from ..inforecords.models import Pc, Station, Cluster, Country
from ..station_layout.models import StationLayout
from ..raw_data.date_generator import daterange
from .nagios import status_lists, get_status_counts, get_station_status


FIRSTDATE = datetime.date(2004, 1, 1)
MIME_TSV = 'text/tab-separated-values'


def stations(request):
    """Show the default station list"""

    return redirect(stations_by_country)


def stations_by_country(request):
    """Show a list of stations, ordered by country, cluster and subcluster"""

    data_stations = stations_with_data()
    down, problem, up = status_lists()
    statuscount = get_status_counts(down, problem, up)

    countries = OrderedDict()
    test_stations = []

    for station in (Station.objects.exclude(pc__type__slug='admin')
                                   .select_related('cluster__country',
                                                   'cluster__parent')):
        link = station in data_stations
        status = get_station_status(station.number, down, problem, up)

        station_info = {'number': station.number,
                        'name': station.name,
                        'link': link,
                        'status': status}

        country = station.cluster.country.name
        if station.cluster.parent:
            cluster = station.cluster.parent.name
        else:
            cluster = station.cluster.name
        subcluster = station.cluster.name

        if len(station.pc_set.filter(is_test=True)):
            test_stations.append(station_info)
            continue
        if country not in countries:
            countries[country] = OrderedDict()
        if cluster not in countries[country]:
            countries[country][cluster] = OrderedDict()
        if subcluster not in countries[country][cluster]:
            countries[country][cluster][subcluster] = []
        countries[country][cluster][subcluster].append(station_info)

    return render(request, 'stations_by_country.html',
                  {'countries': countries,
                   'test_stations': test_stations,
                   'statuscount': statuscount})


def stations_by_number(request):
    """Show a list of stations, ordered by number"""

    data_stations = stations_with_data()
    down, problem, up = status_lists()
    statuscount = get_status_counts(down, problem, up)
    stations = []
    for station in Station.objects.exclude(pc__type__slug='admin'):
        link = station in data_stations
        status = get_station_status(station.number, down, problem, up)

        stations.append({'number': station.number,
                         'name': station.name,
                         'link': link,
                         'status': status})

    return render(request, 'stations_by_number.html',
                  {'stations': stations,
                   'statuscount': statuscount})


def stations_by_name(request):
    """Show a list of stations, ordered by station name"""

    data_stations = stations_with_data()
    down, problem, up = status_lists()
    statuscount = get_status_counts(down, problem, up)
    stations = []
    for station in Station.objects.exclude(pc__type__slug='admin'):
        link = station in data_stations
        status = get_station_status(station.number, down, problem, up)

        stations.append({'number': station.number,
                         'name': station.name,
                         'link': link,
                         'status': status})

    stations = sorted(stations, key=itemgetter('name'))

    return render(request, 'stations_by_name.html',
                  {'stations': stations,
                   'statuscount': statuscount})


def stations_on_map(request, country=None, cluster=None, subcluster=None):
    """Show all stations from a subcluster on a map"""

    data_stations = stations_with_data()
    down, problem, up = status_lists()
    statuscount = get_status_counts(down, problem, up)

    if country:
        get_object_or_404(Country, name=country)
        if cluster:
            get_object_or_404(Cluster, name=cluster, parent=None,
                              country__name=country)
            if subcluster:
                if cluster == subcluster:
                    get_object_or_404(Cluster, name=subcluster, parent=None)
                else:
                    get_object_or_404(Cluster, name=subcluster,
                                      parent__name=cluster)
                focus = (Cluster.objects.filter(name=subcluster)
                                        .values_list('name', flat=True))
            else:
                focus = [Cluster.objects.get(name=cluster, parent=None).name]
                focus.extend(Cluster.objects.filter(parent__name=cluster)
                                            .values_list('name', flat=True))
        else:
            focus = (Cluster.objects.filter(country__name=country)
                                    .values_list('name', flat=True))
    else:
        focus = Cluster.objects.all().values_list('name', flat=True)

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in (Station.objects.select_related('cluster__parent',
                                                       'cluster__country')
                                       .filter(cluster=subcluster,
                                               pc__is_test=False)):

            link = station in data_stations
            status = get_station_status(station.number, down, problem, up)
            location = station.latest_location()
            station_data = {'number': station.number,
                            'name': station.name,
                            'cluster': station.cluster,
                            'link': link,
                            'status': status}
            station_data.update(location)
            stations.append(station_data)
        subclusters.append({'name': subcluster.name,
                            'stations': stations})

    return render(request, 'stations_on_map.html',
                  {'subclusters': subclusters,
                   'focus': focus,
                   'statuscount': statuscount})


def network_coincidences(request, year=None, month=None, day=None):
    """Show daily coincidences histograms for the entire network"""

    today = datetime.date.today()
    # Redirect to latest date with data if no date is given
    if year is None:
        try:
            summary = (NetworkSummary.objects
                                     .filter(num_coincidences__isnull=False,
                                             date__gte=FIRSTDATE,
                                             date__lte=today)
                                     .latest())
        except NetworkSummary.DoesNotExist:
            raise Http404

        return redirect(network_coincidences,
                        year=str(summary.date.year),
                        month=str(summary.date.month),
                        day=str(summary.date.day))

    year = int(year)
    month = int(month)
    day = int(day)
    date = datetime.date(year, month, day)

    summary = get_object_or_404(NetworkSummary,
                                num_coincidences__isnull=False,
                                date=date)

    # Find previous/next dates with data
    try:
        prev = NetworkSummary.objects.filter(num_coincidences__isnull=False,
                                             date__gte=FIRSTDATE,
                                             date__lt=date).latest().date
    except NetworkSummary.DoesNotExist:
        prev = None

    try:
        next = NetworkSummary.objects.filter(num_coincidences__isnull=False,
                                             date__gt=date,
                                             date__lte=today).earliest().date
    except NetworkSummary.DoesNotExist:
        next = None

    n_stations = Station.objects.filter(summary__date=date,
                                        summary__num_events__isnull=False,
                                        pc__is_test=False).count()
    histograms = DailyHistogram.objects.filter(
        source__date=date, source__station__pc__is_test=False,
        type__slug='eventtime')
    number_of_events = sum(sum(histogram.values) for histogram in histograms)
    status = {'station_count': n_stations,
              'n_events': number_of_events}

    thismonth = nav_calendar(year, month)
    month_list = nav_months_network(year)
    year_list = nav_years_network()
    current_date = {'year': year,
                    'month': calendar.month_name[month][:3],
                    'day': day}

    coincidencetimehistogram = create_histogram_network('coincidencetime',
                                                        date)
    coincidencenumberhistogram = create_histogram_network('coincidencenumber',
                                                          date)

    return render(request, 'network_coincidences.html',
                  {'date': date,
                   'tomorrow': date + datetime.timedelta(days=1),
                   'coincidencetimehistogram': coincidencetimehistogram,
                   'coincidencenumberhistogram': coincidencenumberhistogram,
                   'status': status,
                   'thismonth': thismonth,
                   'month_list': month_list,
                   'year_list': year_list,
                   'current_date': current_date,
                   'prev': prev,
                   'next': next,
                   'link': (year, month, day)})


def station_data(request, station_number, year, month, day):
    """Show daily histograms for a particular station"""

    station_number = int(station_number)
    year = int(year)
    month = int(month)
    day = int(day)
    date = datetime.date(year, month, day)

    station = get_object_or_404(Station, number=station_number)
    get_object_or_404(Summary,
                      Q(num_events__isnull=False) |
                      Q(num_weather__isnull=False),
                      station=station,
                      date=date)

    # Find previous/next dates with data
    try:
        previous = (Summary.objects.filter(Q(num_events__isnull=False) |
                                           Q(num_weather__isnull=False),
                                           station=station,
                                           date__gte=FIRSTDATE,
                                           date__lt=date)
                                   .latest()).date
    except Summary.DoesNotExist:
        previous = None

    try:
        next = (Summary.objects.filter(Q(num_events__isnull=False) |
                                       Q(num_weather__isnull=False),
                                       station=station,
                                       date__gt=date,
                                       date__lte=datetime.date.today())
                               .earliest()).date
    except Summary.DoesNotExist:
        next = None

    try:
        source = (Summary.objects.filter(station=station,
                                         num_config__isnull=False,
                                         date__lte=date)
                                 .latest())
        config = Configuration.objects.filter(source=source).latest()
        if config.slave() == -1:
            has_slave = False
        else:
            has_slave = True
    except (Summary.DoesNotExist, Configuration.DoesNotExist):
        config = None
        has_slave = False

    location = station.latest_location(date=date)

    has_config = station_has_config(station)

    try:
        coincidences_found = NetworkSummary.objects.get(date=date)
    except NetworkSummary.DoesNotExist:
        coincidences_found = False

    thismonth = nav_calendar(year, month, station)
    month_list = nav_months(year, station)
    year_list = nav_years(station)
    current_date = {'year': year,
                    'month': calendar.month_name[month][:3],
                    'day': day}

    eventhistogram = create_histogram('eventtime', station, date)
    pulseheighthistogram = create_histogram('pulseheight', station, date)
    pulseintegralhistogram = create_histogram('pulseintegral', station, date)
    zenithhistogram = create_histogram('zenith', station, date)
    azimuthhistogram = create_histogram('azimuth', station, date)
    barometerdata = plot_dataset('barometer', station, date)
    temperaturedata = plot_dataset('temperature', station, date)

    return render(request, 'station_data.html',
                  {'station': station,
                   'date': date,
                   'tomorrow': date + datetime.timedelta(days=1),
                   'config': config,
                   'location': location,
                   'has_slave': has_slave,
                   'eventhistogram': eventhistogram,
                   'pulseheighthistogram': pulseheighthistogram,
                   'pulseintegralhistogram': pulseintegralhistogram,
                   'zenithhistogram': zenithhistogram,
                   'azimuthhistogram': azimuthhistogram,
                   'barometerdata': barometerdata,
                   'temperaturedata': temperaturedata,
                   'thismonth': thismonth,
                   'month_list': month_list,
                   'year_list': year_list,
                   'current_date': current_date,
                   'prev': previous,
                   'next': next,
                   'link': (station_number, year, month, day),
                   'has_data': True,
                   'has_config': has_config,
                   'coincidences_found': coincidences_found})


def station_status(request, station_number):
    """Show Nagios status for a particular station"""

    station_number = int(station_number)

    station = get_object_or_404(Station, number=station_number)
    # Check if there is at least one non-admin pc for the station
    pcs = get_list_or_404(Pc, ~Q(type__slug='admin'), station=station)
    # Get the first active Pc, if there are non get an inactive Pc
    pc = next((pc for pc in pcs if pc.is_active), pcs[0])

    has_data = station_has_data(station)
    has_config = station_has_config(station)

    return render(request, 'station_status.html',
                  {'station': station,
                   'pc': pc,
                   'has_data': has_data,
                   'has_config': has_config,
                   'coincidences_found': True})


def station_config(request, station_number):
    """Show configuration history for a particular station"""

    station_number = int(station_number)
    today = datetime.date.today()

    station = get_object_or_404(Station, number=station_number)
    configs = get_list_or_404(Configuration.objects.order_by('timestamp'),
                              source__station=station,
                              timestamp__gte=FIRSTDATE,
                              timestamp__lte=today)

    has_data = station_has_data(station)

    config = configs[-1]
    if config.slave() == -1:
        has_slave = False
    else:
        has_slave = True

    gpslocations = get_gpslocations(configs)

    # Get latest valid location
    try:
        lla = gpslocations[-1]
    except IndexError:
        lla = None

    voltagegraph = plot_config('voltage', configs)
    currentgraph = plot_config('current', configs)
    timingoffsetgraph = plot_timing_offsets(station.number)
    altitudegraph = plot_config('altitude', configs)
    gpstrack = set(gpslocations)
    layout = StationLayout.objects.filter(station=station,
                                          active_date__gte=FIRSTDATE,
                                          active_date__lte=today).last()

    return render(request, 'station_config.html',
                  {'station': station,
                   'config': config,
                   'lla': lla,
                   'voltagegraph': voltagegraph,
                   'currentgraph': currentgraph,
                   'timingoffsetgraph': timingoffsetgraph,
                   'altitudegraph': altitudegraph,
                   'gpstrack': gpstrack,
                   'layout': layout,
                   'has_slave': has_slave,
                   'has_data': has_data,
                   'has_config': True,
                   'coincidences_found': True})


def station_latest(request, station_number):
    """Show daily histograms for a particular station"""

    station_number = int(station_number)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    old_data = False

    station = get_object_or_404(Station, number=station_number)
    try:
        summary = Summary.objects.get(num_events__isnull=False,
                                      station=station,
                                      date=yesterday)
    except Summary.DoesNotExist:
        # Do something nice, get older data
        old_data = True
        summary = (Summary.objects.filter(num_events__isnull=False,
                                          station=station,
                                          date__gte=FIRSTDATE,
                                          date__lte=datetime.date.today())
                                  .latest())

    down, problem, up = status_lists()
    status = get_station_status(station.number, down, problem, up)

    date = summary.date

    eventhistogram = create_histogram('eventtime', station, date)
    pulseheighthistogram = create_histogram('pulseheight', station, date)
    pulseintegralhistogram = create_histogram('pulseintegral', station, date)
    barometerdata = plot_dataset('barometer', station, date)

    # Show alternative
    extra_station = None
    if barometerdata is None:
        try:
            sum_weather = Summary.objects.filter(num_weather__isnull=False,
                                                 date=summary.date)
            weather_stations = [s[0] for s in
                                sum_weather.values_list('station__number')]
            closest_station = min(weather_stations,
                                  key=lambda x: abs(x - station_number))
            summary_weather = sum_weather.get(station__number=closest_station)
            barometerdata = plot_dataset('barometer', summary_weather.station,
                                         summary_weather.date)
            if barometerdata is not None:
                extra_station = closest_station
        except IndexError:
            pass

    return render(request, 'station_latest.html',
                  {'station': station,
                   'date': date,
                   'status': status,
                   'eventhistogram': eventhistogram,
                   'pulseheighthistogram': pulseheighthistogram,
                   'pulseintegralhistogram': pulseintegralhistogram,
                   'barometerdata': barometerdata,
                   'extra_station': extra_station,
                   'old_data': old_data})


def station(request, station_number):
    """Show most recent histograms for a particular station"""

    try:
        summary = (Summary.objects.filter(Q(num_events__isnull=False) |
                                          Q(num_weather__isnull=False),
                                          station__number=station_number,
                                          date__gte=FIRSTDATE,
                                          date__lte=datetime.date.today())
                                  .latest())
    except Summary.DoesNotExist:
        raise Http404

    return redirect(station_data,
                    station_number=str(station_number),
                    year=str(summary.date.year),
                    month=str(summary.date.month),
                    day=str(summary.date.day))


def get_coincidencetime_histogram_source(request, year, month, day):
    return get_specific_network_histogram_source(year, month, day,
                                                 'coincidencetime')


def get_coincidencenumber_histogram_source(request, year, month, day):
    return get_specific_network_histogram_source(year, month, day,
                                                 'coincidencenumber')


def get_specific_network_histogram_source(request, year, month, day, type):
    data = get_histogram_source(year, month, day, type, station_number)
    response = render(request, 'source_%s_histogram.tsv' % type,
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=%s-network-%d%02d%02d.tsv' %
        (type, station_number, int(year), int(month), int(day)))
    return response


def get_eventtime_histogram_source(request, station_number, year, month, day):
    """Get eventtime histogram for a specific date"""
    return get_specific_histogram_source(station_number, year, month, day,
                                         'eventtime')


def get_pulseheight_histogram_source(request, station_number, year, month,
                                     day):
    return get_specific_histogram_source(station_number, year, month, day,
                                         'pulseheight')


def get_pulseintegral_histogram_source(request, station_number, year, month,
                                       day):
    return get_specific_histogram_source(station_number, year, month, day,
                                         'pulseintegral')


def get_zenith_histogram_source(request, station_number, year, month, day):
    return get_specific_histogram_source(station_number, year, month, day,
                                         'zenith')


def get_azimuth_histogram_source(request, station_number, year, month, day):
    return get_specific_histogram_source(station_number, year, month, day,
                                         'azimuth')


def get_specific_histogram_source(request, station_number, year, month, day,
                                  type):
    data = get_histogram_source(year, month, day, type, station_number)
    response = render(request, 'source_%s_histogram.tsv' % type,
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=%s-s%s-%d%02d%02d.tsv' %
        (type, station_number, int(year), int(month), int(day)))
    return response


def get_eventtime_source(request, station_number, start=None, end=None):
    """Get all eventtime data from start to end"""

    if end is None:
        today = datetime.date.today()
        try:
            last = (Summary.objects.filter(station__number=station_number,
                                           date__gte=FIRSTDATE, date__lt=today,
                                           num_events__isnull=False)
                                   .latest().date)
        except Summary.DoesNotExist:
            raise Http404
        end = last + datetime.timedelta(days=1)
    if start is None:
        # Get first date with data
        try:
            start = (Summary.objects.filter(station__number=station_number,
                                            date__gte=FIRSTDATE, date__lt=end,
                                            num_events__isnull=False)
                                    .earliest().date)
        except Summary.DoesNotExist:
            raise Http404

    data = get_eventtime_histogram_sources(station_number, start, end)

    buffer = StringIO()
    writer = csv.writer(buffer, delimiter='\t', lineterminator='\n')
    writer.writerows(data)
    tsvdata = buffer.getvalue().strip('\n')

    response = render(request, 'source_eventtime.tsv',
                      {'tsvdata': tsvdata,
                       'start': start,
                       'end': end,
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=eventtime-s%s-%s-%s.tsv' %
        (station_number, start.strftime('%Y%m%d'), end.strftime('%Y%m%d')))
    return response


def get_eventtime_histogram_sources(station_number, start, end):
    histograms = get_list_or_404(
        DailyHistogram.objects.select_related('source'),
        source__station__number=station_number,
        source__date__gte=start, source__date__lt=end,
        type__slug='eventtime')
    bins = []
    values = []
    hours = arange(24) * 3600
    no_data = [0] * 24
    i = 0
    for date in daterange(start, end):
        ts = clock.datetime_to_gps(date)
        bins.extend(ts + hours)
        if histograms[i].source.date == date:
            values.extend(histograms[i].values)
            i += 1
            if i == len(histograms):
                break
        else:
            values.extend(no_data)
    return izip(bins, values)


def get_barometer_dataset_source(request, station_number, year, month, day):
    return get_specific_dataset_source(station_number, year, month, day,
                                       'barometer')


def get_temperature_dataset_source(request, station_number, year, month, day):
    return get_specific_dataset_source(station_number, year, month, day,
                                       'temperature')


def get_specific_dataset_source(station_number, year, month, day, type):
    data = get_dataset_source(year, month, day, type, station_number)
    response = render(request, 'source_%s_dataset.tsv' % type,
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=%s-s%s-%d%02d%02d.tsv' %
        (type, station_number, int(year), int(month), int(day)))
    return response


def get_electronics_config_source(request, station_number):
    return get_specific_config_source(station_number, 'electronics')


def get_voltage_config_source(request, station_number):
    return get_specific_config_source(station_number, 'voltage')


def get_current_config_source(request, station_number):
    return get_specific_config_source(station_number, 'current')


def get_gps_config_source(request, station_number):
    return get_specific_config_source(station_number, 'gps')


def get_trigger_config_source(request, station_number):
    return get_specific_config_source(station_number, 'trigger')


def get_specific_config_source(station_number, type):
    data = get_config_source(station_number, type)
    response = render(request, 'source_%s_config.tsv' % type,
                      {'data': data,
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=%s-s%s.tsv' % (type, station_number))
    return response


def get_station_layout_source(request, station_number):
    today = datetime.date.today()
    layouts = StationLayout.objects.filter(station__number=station_number,
                                           active_date__gte=FIRSTDATE,
                                           active_date__lte=today)
    if not layouts:
        raise Http404

    for layout in layouts:
        layout.timestamp = calendar.timegm(layout.active_date.utctimetuple())

    response = render(request, 'source_station_layout.tsv',
                      {'layouts': layouts,
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=station_layout-s%s.tsv' %
        station_number)
    return response


def get_detector_timing_offsets_source(request, station_number):
    data = get_detector_timing_offsets(station_number)
    if not len(data):
        raise Http404

    data = [next(rows)
            for _, rows in groupby(data, key=itemgetter(1, 2, 3, 4))]

    data = [(calendar.timegm(r[0].timetuple()), none_to_nan(r[1]),
             none_to_nan(r[2]), none_to_nan(r[3]), none_to_nan(r[4]))
            for r in data]

    buffer = StringIO()
    writer = csv.writer(buffer, delimiter='\t', lineterminator='\n')
    writer.writerows(data)
    tsvdata = buffer.getvalue().strip('\n')

    response = render(request, 'source_detector_timing_offsets.tsv',
                      {'tsvdata': tsvdata,
                       'station_number': station_number},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=detector_timing_offsets-s%s.tsv' %
        station_number)
    return response


def get_station_timing_offsets_source(request, station_number1,
                                      station_number2):
    station_number1 = int(station_number1)
    station_number2 = int(station_number2)

    if station_number1 >= station_number2:
        raise Http404

    # Not implemented yet, for now raise 404.
    raise Http404

    tsvdata = ''

    response = render(request, 'source_station_timing_offsets.tsv',
                      {'tsvdata': tsvdata,
                       'station_number1': station_number1,
                       'station_number2': station_number2},
                      content_type=MIME_TSV)
    response['Content-Disposition'] = (
        'attachment; filename=station_timing_offsets-s%d-s%d.tsv' %
        (station_number1, station_number2))
    return response


def get_histogram_source(year, month, day, type, station_number=None):
    """Get histogram data for a specific date

    :param year,month,day: the date for which to get the histogram data.
    :param type: the type of histogram to retrieve.
    :param station_number: if None a NetworkHistogram is looked for, otherwise
        a DailyHistogram for a specific station is looked for.
    :return: list of tuples containing (bin, value) pairs.

    """
    date = datetime.date(int(year), int(month), int(day))
    if station_number is None:
        histogram = get_object_or_404(NetworkHistogram,
                                      source__date=date,
                                      type__slug=type)
    else:
        station_number = int(station_number)
        histogram = get_object_or_404(DailyHistogram,
                                      source__station__number=station_number,
                                      source__date=date,
                                      type__slug=type)
    if type in ['eventtime', 'zenith', 'azimuth', 'coincidencetime',
                'coincidencenumber']:
        return zip(histogram.bins, histogram.values)
    else:
        return zip(histogram.bins, *histogram.values)


def get_dataset_source(year, month, day, type, station_number):
    """Get a dataset for a specific date and station

    :param year,month,day: the date for which to get the dataset.
    :param type: the type of dataset to retrieve.
    :param station_number: the station to which the data belongs.
    :return: list of tuples containing (x, y) pairs.

    """
    date = datetime.date(int(year), int(month), int(day))
    dataset = get_object_or_404(DailyDataset,
                                source__station__number=int(station_number),
                                source__date=date,
                                type__slug=type)
    return zip(dataset.x, dataset.y)


def get_config_source(station_number, type):
    """Get configuration data for a specific station

    :param station_number: station for which to get the configuration data.
    :param type: the type of configuration data to get. The following
                 are supported: voltage, current, gps, trigger.
    :return: list of lists containing the configuration history.

    """
    if type == 'voltage':
        fields = ['timestamp', 'mas_ch1_voltage', 'mas_ch2_voltage',
                  'slv_ch1_voltage', 'slv_ch2_voltage']
    elif type == 'current':
        fields = ['timestamp', 'mas_ch1_current', 'mas_ch2_current',
                  'slv_ch1_current', 'slv_ch2_current']
    elif type == 'gps':
        fields = ['timestamp', 'gps_latitude', 'gps_longitude', 'gps_altitude']
    elif type == 'trigger':
        fields = ['timestamp']
        fields.extend('%s_ch%d_thres_%s' % (i, j, k) for k in ['low', 'high']
                      for i in ['mas', 'slv'] for j in [1, 2])
        fields.extend(['trig_low_signals', 'trig_high_signals', 'trig_and_or',
                       'trig_external'])
    else:
        return None

    configs = Configuration.objects.filter(
        source__station__number=station_number,
        timestamp__gte=FIRSTDATE,
        timestamp__lte=datetime.date.today()).order_by('timestamp')

    if not configs:
        raise Http404

    if type == 'electronics':
        data = list((config.timestamp, config.master(), config.slave(),
                     config.master_fpga(), config.slave_fpga())
                    for config in configs)
    else:
        data = list(configs.values_list(*fields))

    return data


def create_histogram_network(type, date):
    """Create a histogram object"""

    source = get_object_or_404(NetworkSummary, date=date)
    type = HistogramType.objects.get(slug=type)

    try:
        histogram = NetworkHistogram.objects.get(source=source, type=type)
    except NetworkHistogram.DoesNotExist:
        return None

    plot_object = create_plot_object(histogram.bins[:-1], histogram.values,
                                     type.bin_axis_title,
                                     type.value_axis_title)
    return plot_object


def create_histogram(type, station, date):
    """Create a histogram object"""

    source = get_object_or_404(Summary, station=station, date=date)
    type = HistogramType.objects.get(slug=type)

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
    type = DatasetType.objects.get(slug=type)

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
        values = [config.gps_altitude for config in configs
                  if config.gps_altitude != 0.]
        if not len(values):
            return None
        y_label = 'Altitude (m)'
    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def plot_timing_offsets(station_number):
    """Create a plot object from station configs"""

    data = get_detector_timing_offsets(station_number)
    data = [[calendar.timegm(row[0].timetuple()), row[1:]] for row in data]
    data = zip(*data)

    timestamps = data[0]
    values = zip(*data[1])

    x_label = 'Date (month/year)'
    y_label = 'Timing offset (ns)'

    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def get_detector_timing_offsets(station_number):
    offsets = DetectorTimingOffset.objects.filter(
        source__station__number=station_number,
        source__date__gte=FIRSTDATE,
        source__date__lte=datetime.date.today())

    data = offsets.values_list('source__date', 'offset_1', 'offset_2',
                               'offset_3', 'offset_4')
    return data


def get_gpslocations(configs):
    """Get all valid GPS locations from the configs"""

    gps = [(config.gps_latitude, config.gps_longitude, config.gps_altitude)
           for config in configs
           if config.gps_latitude != 0. and config.gps_longitude != 0.]
    return gps


def create_plot_object(x_values, y_series, x_label, y_label):
    if type(y_series[0]) not in [list, tuple]:
        y_series = [y_series]
    data = [[[xv, yv] for xv, yv in zip(x_values, y_values) if yv is not None]
            for y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label}
    return plot_object


def nav_calendar(theyear, themonth, station=None):
    """Create a month calendar with links"""

    month = calendar.Calendar().monthdatescalendar(theyear, themonth)
    month_name = '%s %d' % (calendar.month_name[themonth], theyear)
    days_names = calendar.weekheader(3).split(' ')

    if station is None:
        days_with_data = (NetworkSummary.objects
                                        .filter(num_coincidences__isnull=False,
                                                date__year=theyear,
                                                date__month=themonth)
                                        .values_list('date', flat=True))
    else:
        days_with_data = (Summary.objects.filter(Q(num_events__isnull=False) |
                                                 Q(num_weather__isnull=False),
                                                 station=station,
                                                 date__year=theyear,
                                                 date__month=themonth)
                                         .values_list('date', flat=True))

    weeks = []
    for week in month:
        days = []
        for day in week:
            if day.month == themonth:
                if day in days_with_data:
                    if station is None:
                        link = (theyear, themonth, day.day)
                    else:
                        link = (station.number, theyear, themonth, day.day)
                else:
                    link = None
                days.append({'day': day.day, 'link': link})
            else:
                days.append('')
        weeks.append(days)

    return {'month': month_name, 'days': days_names, 'weeks': weeks}


def nav_months_network(theyear):
    """Create list of months with links"""

    date_list = (NetworkSummary.objects.filter(date__year=theyear,
                                               num_coincidences__isnull=False)
                                       .dates('date', 'month'))

    month_list = [{'month': calendar.month_name[i][:3]} for i in range(1, 13)]

    for date in date_list:
        first_day = (NetworkSummary.objects
                                   .filter(date__year=date.year,
                                           date__month=date.month,
                                           num_coincidences__isnull=False)
                                   .dates('date', 'day')[0])
        link = (date.year, date.month, first_day.day)
        month_list[date.month - 1]['link'] = link

    return month_list


def nav_months(theyear, station):
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


def nav_years_network():
    """Create list of previous years"""

    valid_years = (NetworkSummary.objects
                                 .filter(num_coincidences__isnull=False,
                                         date__gte=FIRSTDATE,
                                         date__lte=datetime.date.today())
                                 .dates('date', 'year'))
    valid_years = [date.year for date in valid_years]

    year_list = []
    for year in range(valid_years[0], valid_years[-1] + 1):
        if year in valid_years:
            first_day = (NetworkSummary.objects
                                       .filter(date__year=year,
                                               num_coincidences__isnull=False)
                                       .dates('date', 'day')[0])
            link = (year, first_day.month, first_day.day)
            year_list.append({'year': year, 'link': link})
        else:
            year_list.append({'year': year, 'link': None})
    return year_list


def nav_years(station=None):
    """Create list of previous years"""

    valid_years = (Summary.objects.filter(Q(station=station),
                                          Q(num_events__isnull=False) |
                                          Q(num_weather__isnull=False),
                                          date__gte=FIRSTDATE,
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


def stations_with_data():
    """Get list of station numbers with valid event or weather data

    :return: list with station numbers for stations that recorded data, either
             weather or shower, between 2002 and now.

    """
    stations = (Station.objects
                       .filter(Q(summary__num_events__isnull=False) |
                               Q(summary__num_weather__isnull=False),
                               summary__date__gte=FIRSTDATE,
                               summary__date__lte=datetime.date.today())
                       .distinct())

    return stations


def station_has_config(station):
    """Check if there is a valid configuration for the given station

    :param station: Station object for which to check.
    :return: boolean indicating if the station has a configuration available.

    """
    has_config = (Summary.objects
                         .filter(station=station,
                                 num_config__isnull=False,
                                 date__gte=FIRSTDATE,
                                 date__lte=datetime.date.today())
                         .exists())

    return has_config


def station_has_data(station):
    """Check if there is valid event or weather data for the given station

    :param station: Station object for which to check.
    :return: boolean indicating if the station has recorded data, either
             weather or shower, between 2002 and now.

    """
    has_data = Summary.objects.filter(Q(station=station),
                                      Q(num_events__isnull=False) |
                                      Q(num_weather__isnull=False),
                                      date__gte=FIRSTDATE,
                                      date__lte=datetime.date.today()).exists()

    return has_data


def none_to_nan(x):
    if x is None:
        return nan
    else:
        return x


def help(request):
    """Show the static help page"""
    return render(request, 'help.html')
