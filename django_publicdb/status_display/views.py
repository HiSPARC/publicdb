from django.shortcuts import (render, get_object_or_404,
                              get_list_or_404, redirect)
from django.http import Http404
from django.db.models import Q

from collections import OrderedDict
from operator import itemgetter
import calendar
import datetime

from numpy import arange

from sapphire.transformations.clock import datetime_to_gps

from ..histograms.models import (DailyHistogram, DailyDataset, Configuration,
                                 NetworkHistogram, HistogramType, DatasetType,
                                 DetectorTimingOffset, Summary, NetworkSummary)
from ..inforecords.models import (Pc, Station, Cluster, Country,
                                  DetectorHisparc)
from ..station_layout.models import StationLayout
from ..raw_data.date_generator import daterange
from .nagios import status_lists, get_status_counts, get_station_status


FIRSTDATE = datetime.date(2002, 1, 1)


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
                                   .order_by('number')
                                   .select_related('cluster__country',
                                                   'cluster__parent')):
        if station.number in data_stations:
            link = station.number
        else:
            link = None
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
        if station.number in data_stations:
            link = station.number
        else:
            link = None
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
        if station.number in data_stations:
            link = station.number
        else:
            link = None
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
    today = datetime.datetime.utcnow()

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
            try:
                detector = (DetectorHisparc.objects.filter(station=station,
                                                           startdate__lte=today)
                                                   .latest('startdate'))
            except DetectorHisparc.DoesNotExist:
                continue
            link = station.number in data_stations
            status = get_station_status(station.number, down, problem, up)
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

    return render(request, 'stations_on_map.html',
                  {'subclusters': subclusters,
                   'focus': focus,
                   'statuscount': statuscount})


def network_coincidences(request, year=None, month=None, day=None):
    """Show daily coincidences histograms for the entire network"""

    # Redirect to latest date with data if no date is given
    if year is None:
        try:
            summary = (NetworkSummary.objects
                                     .filter(num_coincidences__isnull=False,
                                             date__gte=FIRSTDATE,
                                             date__lte=datetime.date.today())
                                     .latest('date'))
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
        previous = (NetworkSummary.objects.filter(num_coincidences__isnull=False,
                                                  date__gte=FIRSTDATE,
                                                  date__lt=date)
                                  .latest('date')).date
    except NetworkSummary.DoesNotExist:
        previous = None

    try:
        next = (NetworkSummary.objects.filter(num_coincidences__isnull=False,
                                              date__gt=date,
                                              date__lte=datetime.date.today())
                                      .order_by('date'))[0].date
    except IndexError:
        next = None

    station_summaries = Summary.objects.filter(date=date,
                                               num_events__isnull=False)
    status = {'station_count': station_summaries.count(),
              'n_events': sum([s.num_events for s in station_summaries])}

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
                   'prev': previous,
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
                                   .latest('date')).date
    except Summary.DoesNotExist:
        previous = None

    try:
        next = (Summary.objects.filter(Q(num_events__isnull=False) |
                                       Q(num_weather__isnull=False),
                                       station=station,
                                       date__gt=date,
                                       date__lte=datetime.date.today())
                               .order_by('date'))[0].date
    except IndexError:
        next = None

    try:
        source = (Summary.objects.filter(station=station,
                                         num_config__isnull=False,
                                         date__lte=date)
                                 .latest('date'))
        config = (Configuration.objects.filter(source=source)
                                       .latest('timestamp'))
        if config.slv_version.count('0') == 2:
            has_slave = False
        else:
            has_slave = True
        has_config = True
    except (Summary.DoesNotExist, Configuration.DoesNotExist):
        config = None
        has_slave = False
        has_config = False

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
    barometerdata = plot_dataset('barometer', station, date)
    temperaturedata = plot_dataset('temperature', station, date)

    return render(request, 'station_data.html',
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
    has_config = Configuration.objects.filter(source__station=station).exists()

    return render(request, 'station_status.html',
                  {'station': station,
                   'pc': pc,
                   'has_data': has_data,
                   'has_config': has_config,
                   'coincidences_found': True})


def station_config(request, station_number):
    """Show configuration history for a particular station"""

    station_number = int(station_number)

    station = get_object_or_404(Station, number=station_number)
    configs = get_list_or_404(Configuration.objects.order_by('timestamp'),
                              source__station=station,
                              timestamp__gte=FIRSTDATE,
                              timestamp__lte=datetime.date.today())

    has_data = station_has_data(station)

    config = configs[-1]
    if config.slv_version.count('0') == 2:
        has_slave = False
    else:
        has_slave = True

    voltagegraph = plot_config('voltage', configs)
    currentgraph = plot_config('current', configs)
    timingoffsetgraph = plot_timing_offsets(station.number)
    altitudegraph = plot_config('altitude', configs)
    gpstrack = get_gpspositions(configs)

    return render(request, 'station_config.html',
                  {'station': station,
                   'config': config,
                   'voltagegraph': voltagegraph,
                   'currentgraph': currentgraph,
                   'timingoffsetgraph': timingoffsetgraph,
                   'altitudegraph': altitudegraph,
                   'gpstrack': gpstrack,
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
                                  .latest('date'))

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
                                  .latest('date'))
    except Summary.DoesNotExist:
        raise Http404

    return redirect(station_data,
                    station_number=str(station_number),
                    year=str(summary.date.year),
                    month=str(summary.date.month),
                    day=str(summary.date.day))


def get_coincidencetime_histogram_source(request, year, month, day):
    data = get_histogram_source(year, month, day, 'coincidencetime')
    response = render(request, 'source_coincidencetime_histogram.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day))},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=coincidencetime-network-%d%02d%02d.csv' %
        (int(year), int(month), int(day)))
    return response


def get_coincidencenumber_histogram_source(request, year, month, day):
    data = get_histogram_source(year, month, day, 'coincidencenumber')
    response = render(request, 'source_coincidencenumber_histogram.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day))},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=coincidencenumber-network-%d%02d%02d.csv' %
        (int(year), int(month), int(day)))
    return response


def get_eventtime_histogram_source(request, station_number, year, month, day):
    """Get all eventtime histograms for a specific date"""

    data = get_histogram_source(year, month, day, 'eventtime', station_number)
    response = render(request, 'source_eventtime_histogram.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=eventtime-s%s-%d%02d%02d.csv' %
        (station_number, int(year), int(month), int(day)))
    return response


def get_eventtime_source(request, station_number, start=None, end=None):
    """Get all eventtime data from start to end"""

    if end is None:
        end = datetime.date.today()
    if start is None:
        # Get first date with data
        start = Summary.objects.filter(station__number=station_number,
                                       date__gte=FIRSTDATE, date__lt=end,
                                       num_events__isnull=False).first()

    data = get_eventtime_histogram_sources(station_number, start, end)
    response = render(request, 'source_eventtime.csv',
                      {'data': data,
                       'start': start,
                       'end': end,
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=eventtime-s%s-%s-%s.csv' %
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
        ts = datetime_to_gps(date)
        bins.extend(ts + hours)
        if histograms[i].source.date == date:
            values.extend(histograms[i].values)
            i += 1
            if i == len(histograms):
                break
        else:
            values.extend(no_data)
    return zip(bins, values)


def get_pulseheight_histogram_source(request, station_number, year, month,
                                     day):
    data = get_histogram_source(year, month, day, 'pulseheight',
                                station_number)
    response = render(request, 'source_pulseheight_histogram.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=pulseheight-s%s-%d%02d%02d.csv' %
        (station_number, int(year), int(month), int(day)))
    return response


def get_pulseintegral_histogram_source(request, station_number, year, month,
                                       day):
    data = get_histogram_source(year, month, day, 'pulseintegral',
                                station_number)
    response = render(request, 'source_pulseintegral_histogram.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=pulseintegral-s%s-%d%02d%02d.csv' %
        (station_number, int(year), int(month), int(day)))
    return response


def get_barometer_dataset_source(request, station_number, year, month, day):
    data = get_dataset_source(year, month, day, 'barometer', station_number)
    response = render(request, 'source_barometer_dataset.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=barometer-s%s-%d%02d%02d.csv' %
        (station_number, int(year), int(month), int(day)))
    return response


def get_temperature_dataset_source(request, station_number, year, month, day):
    data = get_dataset_source(year, month, day, 'temperature', station_number)
    response = render(request, 'source_temperature_dataset.csv',
                      {'data': data,
                       'date': '-'.join((year, month, day)),
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=temperature-s%s-%d%02d%02d.csv' %
        (station_number, int(year), int(month), int(day)))
    return response


def get_voltage_config_source(request, station_number):
    data = get_config_source(station_number, 'voltage')
    response = render(request, 'source_voltage_config.csv',
                      {'data': data,
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=voltage-s%s.csv' % station_number)
    return response


def get_current_config_source(request, station_number):
    data = get_config_source(station_number, 'current')
    response = render(request, 'source_current_config.csv',
                      {'data': data,
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=current-s%s.csv' % station_number)
    return response


def get_gps_config_source(request, station_number):
    data = get_config_source(station_number, 'gps')
    response = render(request, 'source_gps_config.csv',
                      {'data': data,
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=gps-s%s.csv' % station_number)
    return response


def get_station_layout_source(request, station_number):
    layouts = (StationLayout.objects.filter(station__number=station_number,
                                            active_date__gte=FIRSTDATE,
                                            active_date__lte=datetime.date.today())
                                    .order_by('active_date'))

    for layout in layouts:
        layout.timestamp = calendar.timegm(layout.active_date.utctimetuple())

    response = render(request, 'source_station_layout.csv',
                      {'layouts': layouts,
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=station_layout-s%s.csv' %
        station_number)
    return response


def get_detector_timing_offsets_source(request, station_number):
    data = get_detector_timing_offsets(station_number)
    response = render(request, 'source_detector_timing_offsets.csv',
                      {'data': data,
                       'station_number': station_number},
                      content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=detector_timing_offsets-s%s.csv' %
        station_number)
    return response


def get_histogram_source(year, month, day, type, station_number=None):
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
    if type in ['eventtime', 'coincidencetime', 'coincidencenumber']:
        return zip(histogram.bins, histogram.values)
    else:
        return zip(histogram.bins, *histogram.values)


def get_dataset_source(year, month, day, type, station_number):
    date = datetime.date(int(year), int(month), int(day))
    dataset = get_object_or_404(DailyDataset,
                                source__station__number=int(station_number),
                                source__date=date,
                                type__slug=type)
    return zip(dataset.x, dataset.y)


def get_config_source(station_number, type):
    configs = (Configuration.objects.filter(source__station__number=station_number,
                                            timestamp__gte=FIRSTDATE,
                                            timestamp__lte=datetime.date.today())
                                    .order_by('timestamp'))
    if type == 'voltage':
        data = configs.values_list('timestamp', 'mas_ch1_voltage',
                                   'mas_ch2_voltage', 'slv_ch1_voltage',
                                   'slv_ch2_voltage')
        data = [[calendar.timegm(row[0].utctimetuple()), row[1], row[2],
                 row[3], row[4]] for row in data]
    elif type == 'current':
        data = configs.values_list('timestamp', 'mas_ch1_current',
                                   'mas_ch2_current', 'slv_ch1_current',
                                   'slv_ch2_current')
        data = [[calendar.timegm(row[0].utctimetuple()), row[1], row[2],
                 row[3], row[4]] for row in data]
    elif type == 'gps':
        data = configs.values_list('timestamp', 'gps_latitude',
                                   'gps_longitude', 'gps_altitude')
        data = [[calendar.timegm(row[0].utctimetuple()), row[1], row[2],
                 row[3]] for row in data]
    else:
        data = None

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
        values = [config.gps_altitude for config in configs]
        y_label = 'Altitude (m)'
    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def plot_timing_offsets(station_number):
    """Create a plot object from station configs"""

    data = get_detector_timing_offsets(station_number)
    data = zip(*data)

    timestamps = data[0]
    values = zip(*data[1])

    x_label = 'Date (month/year)'
    y_label = 'Timing offset (ns)'

    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def get_detector_timing_offsets(station_number):
    offsets = (DetectorTimingOffset.objects.filter(
        source__station__number=station_number,
        source__date__gte=FIRSTDATE,
        source__date__lte=datetime.date.today()).order_by('source__date'))

    data = offsets.values_list('source__date', 'offset_1', 'offset_2',
                               'offset_3', 'offset_4')
    data = [[calendar.timegm(row[0].timetuple()), row[1:]] for row in data]
    return data


def get_gpspositions(configs):
    """Get all unique gps positions from the configs"""

    gps = [(config.gps_longitude, config.gps_latitude) for config in configs
           if config.gps_longitude != 0.0 and config.gps_latitude != 0.0]
    return set(gps)


def create_plot_object(x_values, y_series, x_label, y_label):
    if type(y_series[0]) != list and type(y_series[0]) != tuple:
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
                       .distinct()
                       .values_list('number', flat=True))

    return stations


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


def help(request):
    """Show the static help page"""
    return render(request, 'help.html')
