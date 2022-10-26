import calendar
import csv
import datetime

from collections import OrderedDict
from io import StringIO
from itertools import groupby
from operator import itemgetter

from numpy import arange, nan

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.generic import DateDetailView, RedirectView

from sapphire.transformations import clock

from ..histograms.models import (
    Configuration,
    DailyDataset,
    DailyHistogram,
    DetectorTimingOffset,
    MultiDailyDataset,
    MultiDailyHistogram,
    NetworkHistogram,
    NetworkSummary,
    StationTimingOffset,
    Summary,
)
from ..inforecords.models import Cluster, Country, Station
from ..raw_data.date_generator import daterange
from ..station_layout.models import StationLayout
from .status import DataStatus

FIRSTDATE = datetime.date(2004, 1, 1)
MIME_TSV = 'text/tab-separated-values'


def stations(request):
    """Show the default station list"""

    return redirect('status:stations_by_country')


def stations_by_country(request):
    """Show a list of stations, ordered by country, cluster and subcluster"""

    station_status = DataStatus()
    statuscount = station_status.get_status_counts()

    data_stations = stations_with_data()

    countries = OrderedDict()
    test_stations = []

    for station in Station.objects.exclude(pcs__type__slug='admin').select_related(
        'cluster__country', 'cluster__parent'
    ):
        link = station in data_stations
        status = station_status.get_status(station.number)

        station_info = {'number': station.number, 'name': station.name, 'link': link, 'status': status}

        country = station.cluster.country.name
        if station.cluster.parent:
            cluster = station.cluster.parent.name
        else:
            cluster = station.cluster.name
        subcluster = station.cluster.name

        if len(station.pcs.filter(is_test=True)):
            test_stations.append(station_info)
            continue
        if country not in countries:
            countries[country] = OrderedDict()
        if cluster not in countries[country]:
            countries[country][cluster] = OrderedDict()
        if subcluster not in countries[country][cluster]:
            countries[country][cluster][subcluster] = []
        countries[country][cluster][subcluster].append(station_info)

    return render(
        request,
        'status_display/stations_by_country.html',
        {'countries': countries, 'test_stations': test_stations, 'statuscount': statuscount},
    )


def stations_by_number(request):
    """Show a list of stations, ordered by number"""

    station_status = DataStatus()
    statuscount = station_status.get_status_counts()

    data_stations = stations_with_data()
    stations = []
    for station in Station.objects.exclude(pcs__type__slug='admin'):
        link = station in data_stations
        status = station_status.get_status(station.number)

        stations.append({'number': station.number, 'name': station.name, 'link': link, 'status': status})

    return render(request, 'status_display/stations_by_number.html', {'stations': stations, 'statuscount': statuscount})


def stations_by_status(request):
    """Show a list of stations, ordered by status"""

    station_status = DataStatus()
    statuscount = station_status.get_status_counts()

    data_stations = stations_with_data()
    # keep a specific ordering of the status labels
    station_groups = OrderedDict([('up', []), ('problem', []), ('down', []), ('unknown', [])])
    for station in Station.objects.all():
        link = station in data_stations
        status = station_status.get_status(station.number)

        # use setdefault() to automatically include unforeseen status labels without crashing
        group = station_groups.setdefault(status, [])
        group.append({'number': station.number, 'name': station.name, 'link': link, 'status': status})

    return render(
        request,
        'status_display/stations_by_status.html',
        {'station_groups': station_groups, 'statuscount': statuscount},
    )


def stations_by_name(request):
    """Show a list of stations, ordered by station name"""

    station_status = DataStatus()
    statuscount = station_status.get_status_counts()

    data_stations = stations_with_data()
    stations = []
    for station in Station.objects.exclude(pcs__type__slug='admin'):
        link = station in data_stations
        status = station_status.get_status(station.number)

        stations.append({'number': station.number, 'name': station.name, 'link': link, 'status': status})

    stations = sorted(stations, key=itemgetter('name'))

    return render(request, 'status_display/stations_by_name.html', {'stations': stations, 'statuscount': statuscount})


def stations_on_map(request, country=None, cluster=None, subcluster=None):
    """Show all stations from a subcluster on a map"""

    if not country:
        focus = Cluster.objects.all().values_list('name', flat=True)
    else:
        country = get_object_or_404(Country, name=country)
        if not cluster:
            focus = country.clusters.values_list('name', flat=True)
        else:
            cluster = get_object_or_404(country.clusters, name=cluster, parent=None)
            if not subcluster:
                focus = [cluster.name]
                focus.extend(cluster.subclusters.values_list('name', flat=True))
            else:
                if cluster.name == subcluster:
                    focus = [cluster.name]
                else:
                    focus = [get_object_or_404(cluster.subclusters, name=subcluster).name]

    data_stations = stations_with_data()
    station_status = DataStatus()
    statuscount = station_status.get_status_counts()

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in subcluster.stations.filter(pcs__is_test=False).distinct():
            link = station in data_stations
            status = station_status.get_status(station.number)

            location = station.latest_location()
            station_data = {
                'number': station.number,
                'name': station.name,
                'cluster': subcluster,
                'link': link,
                'status': status,
            }
            station_data.update(location)
            stations.append(station_data)
        subclusters.append({'name': subcluster.name, 'stations': stations})

    return render(
        request,
        'status_display/stations_on_map.html',
        {'subclusters': subclusters, 'focus': focus, 'statuscount': statuscount},
    )


class NetworkSummaryDetailView(DateDetailView):
    http_method_names = ['get']
    template_name = 'status_display/network_coincidences.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        date = self.kwargs['date']

        try:
            obj = queryset.get(date=date)
        except queryset.model.DoesNotExist:
            raise Http404

        return obj

    def get_queryset(self):
        return NetworkSummary.objects.with_coincidences().prefetch_related(
            'network_histograms', 'network_histograms__type'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.object.date

        # Find previous/next dates with data
        try:
            prev = NetworkSummary.objects.with_coincidences().filter(date__lt=date).latest().date
        except NetworkSummary.DoesNotExist:
            prev = None

        try:
            next = NetworkSummary.objects.with_coincidences().filter(date__gt=date).earliest().date
        except NetworkSummary.DoesNotExist:
            next = None

        # Number of non-test stations with data on this date
        n_stations = (
            Station.objects.filter(summaries__date=date, summaries__num_events__isnull=False, pcs__is_test=False)
            .distinct()
            .count()
        )
        histograms = DailyHistogram.objects.filter(
            summary__date=date, summary__station__pcs__is_test=False, type__slug='eventtime'
        ).distinct()
        number_of_events = sum(sum(histogram.values) for histogram in histograms)
        status = {'station_count': n_stations, 'n_events': number_of_events}

        # Date navigation
        thismonth = self.nav_calendar()
        month_list = self.nav_months()
        year_list = self.nav_years()

        # Data for the plots
        plots = {histogram.type.slug: plot_histogram(histogram) for histogram in self.object.network_histograms.all()}

        # data for singles plots
        singles_datasets = MultiDailyDataset.objects.filter(
            summary__date=date, summary__station__pcs__is_test=False, type__slug='singlesratelow'
        ).distinct()
        singles_plots = [(dataset.summary.station.number, plot_dataset(dataset)) for dataset in singles_datasets]
        singles_plots = sorted(singles_plots)

        context.update(
            {
                'date': date,
                'tomorrow': date + datetime.timedelta(days=1),
                'status': status,
                'plots': plots,
                'singles_plots': singles_plots,
                'thismonth': thismonth,
                'month_list': month_list,
                'year_list': year_list,
                'prev': prev,
                'next': next,
            }
        )
        return context

    def nav_calendar(self):
        """Create a month calendar with links"""

        date = self.object.date

        month = calendar.Calendar().monthdatescalendar(date.year, date.month)

        days_with_data = self.get_queryset().filter(date__year=date.year, date__month=date.month)
        days_with_data = {day.date: day.get_absolute_url() for day in days_with_data}

        weeks = []
        for week in month:
            days = []
            for day in week:
                if day.month == date.month:
                    try:
                        link = days_with_data[day]
                    except KeyError:
                        link = None
                    days.append({'day': day.day, 'link': link})
                else:
                    days.append(None)
            weeks.append(days)

        return {'days': calendar.day_abbr[:], 'weeks': weeks}

    def nav_months(self):
        """Create list of months with links"""

        date = self.object.date

        date_list = self.get_queryset().filter(date__year=date.year).dates('date', 'month')

        month_list = [{'month': month} for month in calendar.month_abbr[1:]]

        for date in date_list:
            first_of_month = (
                self.get_queryset().filter(date__year=date.year, date__month=date.month).earliest().get_absolute_url()
            )
            month_list[date.month - 1]['link'] = first_of_month

        return month_list

    def nav_years(self):
        """Create list of previous years"""

        years_with_data = self.get_queryset().dates('date', 'year')
        years_with_data = [date.year for date in years_with_data]

        year_list = []
        for year in range(years_with_data[0], years_with_data[-1] + 1):
            if year in years_with_data:
                first_of_year = self.get_queryset().filter(date__year=year).earliest().get_absolute_url()
                year_list.append({'year': year, 'link': first_of_year})
            else:
                year_list.append({'year': year, 'link': None})
        return year_list


class LatestNetworkSummaryRedirectView(RedirectView):
    """Show most recent coincidence data page"""

    def get_redirect_url(self, *args, **kwargs):
        try:
            return NetworkSummary.objects.with_coincidences().latest().get_absolute_url()
        except NetworkSummary.DoesNotExist:
            return None


class SummaryDetailView(DateDetailView):
    http_method_names = ['get']
    template_name = 'status_display/station_data.html'

    def get_queryset(self):
        return Summary.objects.with_data()

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        queryset = (
            self.get_queryset()
            .select_related('station')
            .prefetch_related(
                'histograms',
                'histograms__type',
                'multi_histograms',
                'multi_histograms__type',
                'datasets',
                'datasets__type',
                'multi_datasets',
                'multi_datasets__type',
            )
        )

        date = self.kwargs['date']
        station_numner = self.kwargs['station_number']

        try:
            obj = queryset.get(
                date=date,
                station__number=station_numner,
            )
        except queryset.model.DoesNotExist:
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.object.station
        date = self.object.date

        # Find previous/next dates with data
        try:
            previous = self.get_queryset().filter(station=station, date__lt=date).latest().get_absolute_url()
        except Summary.DoesNotExist:
            previous = None
        try:
            next = self.get_queryset().filter(station=station, date__gt=date).earliest().get_absolute_url()
        except Summary.DoesNotExist:
            next = None

        # Get most recent configuration
        try:
            summary = Summary.objects.with_config().filter(station=station, date__lte=date).latest()
            config = Configuration.objects.filter(summary=summary).latest()
            if config.slave == -1:
                has_slave = False
            else:
                has_slave = True
        except (Summary.DoesNotExist, Configuration.DoesNotExist):
            config = None
            has_slave = False

        location = station.latest_location(date=date)

        has_config = config is not None

        try:
            coincidences_found = NetworkSummary.objects.get(date=date)
        except NetworkSummary.DoesNotExist:
            coincidences_found = False

        # Date navigation
        thismonth = self.nav_calendar()
        month_list = self.nav_months()
        year_list = self.nav_years()

        # Data for the plots
        plots = {histogram.type.slug: plot_histogram(histogram) for histogram in self.object.histograms.all()}
        plots.update(
            {histogram.type.slug: plot_histogram(histogram) for histogram in self.object.multi_histograms.all()}
        )
        plots.update({dataset.type.slug: plot_dataset(dataset) for dataset in self.object.datasets.all()})
        plots.update({dataset.type.slug: plot_dataset(dataset) for dataset in self.object.multi_datasets.all()})

        context.update(
            {
                'station': station,
                'date': date,
                'tomorrow': date + datetime.timedelta(days=1),
                'config': config,
                'location': location,
                'has_slave': has_slave,
                'plots': plots,
                'thismonth': thismonth,
                'month_list': month_list,
                'year_list': year_list,
                'previous': previous,
                'next': next,
                'has_data': True,
                'has_config': has_config,
                'coincidences_found': coincidences_found,
            }
        )
        return context

    def nav_calendar(self):
        """Create a month calendar with links"""

        date = self.object.date
        month = calendar.Calendar().monthdatescalendar(date.year, date.month)

        days_with_data = self.get_queryset().filter(
            station=self.object.station,
            date__year=date.year,
            date__month=date.month,
        )
        days_with_data = {day.date: day.get_absolute_url() for day in days_with_data}

        weeks = []
        for week in month:
            days = []
            for day in week:
                if day.month == date.month:
                    try:
                        link = days_with_data[day]
                    except KeyError:
                        link = None
                    days.append({'day': day.day, 'link': link})
                else:
                    days.append(None)
            weeks.append(days)

        return {'days': calendar.day_abbr[:], 'weeks': weeks}

    def nav_months(self):
        """Create list of months with links"""

        months_with_data = (
            self.get_queryset()
            .filter(station=self.object.station, date__year=self.object.date.year)
            .dates('date', 'month')
        )
        month_list = [{'month': month} for month in calendar.month_abbr[1:]]

        for date in months_with_data:
            first_of_month = (
                self.get_queryset()
                .filter(station=self.object.station, date__year=date.year, date__month=date.month)
                .earliest()
                .get_absolute_url()
            )
            month_list[date.month - 1]['link'] = first_of_month

        return month_list

    def nav_years(self):
        """Create list of previous years"""

        years_with_data = self.get_queryset().filter(station=self.object.station).dates('date', 'year')
        years_with_data = [date.year for date in years_with_data]

        year_list = []
        for year in range(years_with_data[0], years_with_data[-1] + 1):
            if year in years_with_data:
                first_of_year = (
                    self.get_queryset()
                    .filter(station=self.object.station, date__year=year)
                    .earliest()
                    .get_absolute_url()
                )
                year_list.append({'year': year, 'link': first_of_year})
            else:
                year_list.append({'year': year, 'link': None})
        return year_list


class LatestSummaryRedirectView(RedirectView):
    """Show most recent data for a particular station"""

    def get_redirect_url(self, *args, **kwargs):
        try:
            return (
                Summary.objects.with_data().filter(station__number=kwargs['station_number']).latest().get_absolute_url()
            )
        except Summary.DoesNotExist:
            return None


def station_status(request, station_number):
    """Show data status for a particular station"""

    station = get_object_or_404(Station, number=station_number)

    has_data = station_has_data(station)
    has_config = station_has_config(station)

    station_status = DataStatus()
    status = station_status.get_status(station_number)

    return render(
        request,
        'status_display/station_status.html',
        {
            'station': station,
            'has_data': has_data,
            'has_config': has_config,
            'status': status,
            'coincidences_found': True,
        },
    )


def station_config(request, station_number):
    """Show configuration history for a particular station"""

    today = datetime.date.today()

    station = get_object_or_404(Station, number=station_number)
    configs = get_list_or_404(
        Configuration.objects.order_by('timestamp'),
        summary__station=station,
        timestamp__gte=FIRSTDATE,
        timestamp__lte=today,
    )

    has_data = station_has_data(station)

    config = configs[-1]
    if config.slave == -1:
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
    layout = StationLayout.objects.filter(station=station, active_date__gte=FIRSTDATE, active_date__lte=today).last()

    return render(
        request,
        'status_display/station_config.html',
        {
            'station': station,
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
            'coincidences_found': True,
        },
    )


def station_latest(request, station_number):
    """Show daily histograms for a particular station"""

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    old_data = False

    station = get_object_or_404(Station, number=station_number)
    try:
        summary = Summary.objects.get(num_events__isnull=False, station=station, date=yesterday)
    except Summary.DoesNotExist:
        # Do something nice, get older data
        old_data = True
        summary = Summary.objects.valid_date().filter(num_events__isnull=False, station=station).latest()

    station_status = DataStatus()
    status = station_status.get_status(station.number)

    date = summary.date

    plots = {
        histogram.type.slug: plot_histogram(histogram)
        for histogram in summary.histograms.filter(type__slug='eventtime')
    }
    plots.update(
        {
            histogram.type.slug: plot_histogram(histogram)
            for histogram in summary.multi_histograms.filter(type__slug__in=['pulseheight', 'pulseintegral'])
        }
    )
    plots.update(
        {dataset.type.slug: plot_dataset(dataset) for dataset in summary.datasets.filter(type__slug='barometer')}
    )

    # Show alternative
    extra_station = None
    if 'barometer' not in plots:
        try:
            sum_weather = Summary.objects.filter(num_weather__isnull=False, date=summary.date)
            weather_stations = sum_weather.values_list('station__number', flat=True)
            closest_station = min(weather_stations, key=lambda x: abs(x - station_number))
            summary_weather = sum_weather.get(station__number=closest_station)
            barometerdata = summary_weather.datasets.filter(type__slug='barometer').first()
            if barometerdata is not None:
                plots['barometer'] = plot_dataset(barometerdata)
                extra_station = closest_station
        except IndexError:
            pass

    return render(
        request,
        'status_display/station_latest.html',
        {
            'station': station,
            'date': date,
            'status': status,
            'plots': plots,
            'extra_station': extra_station,
            'old_data': old_data,
        },
    )


def get_specific_network_histogram_source(request, date, type):
    data = get_histogram_source(date, type)
    response = render(
        request,
        f'source/{type}_histogram.tsv',
        {
            'data': data,
            'date': date,
        },
        content_type=MIME_TSV,
    )
    response['Content-Disposition'] = f'attachment; filename={type}-network-{date:%Y%-m%-d}.tsv'
    return response


def get_specific_histogram_source(request, station_number, date, type):
    """Get a station histogram for a specific date"""
    data = get_histogram_source(date, type, station_number)
    response = render(
        request,
        f'source/{type}_histogram.tsv',
        {
            'data': data,
            'date': date,
            'station_number': station_number,
        },
        content_type=MIME_TSV,
    )
    response['Content-Disposition'] = 'attachment; filename={type}-s{station_numer}-{date:%Y%-m%-d}.tsv'
    return response


def get_eventtime_source(request, station_number, start=None, end=None):
    """Get all eventtime data from start to end"""

    if end is None:
        try:
            last = (
                Summary.objects.valid_date()
                .filter(station__number=station_number, num_events__isnull=False)
                .latest()
                .date
            )
        except Summary.DoesNotExist:
            raise Http404
        end = last + datetime.timedelta(days=1)
    if start is None:
        # Get first date with data
        try:
            start = (
                Summary.objects.valid_date()
                .filter(station__number=station_number, date__lt=end, num_events__isnull=False)
                .earliest()
                .date
            )
        except Summary.DoesNotExist:
            raise Http404

    data = get_eventtime_histogram_sources(station_number, start, end)

    buffer = StringIO()
    writer = csv.writer(buffer, delimiter='\t', lineterminator='\n')
    writer.writerows(data)
    tsvdata = buffer.getvalue().strip('\n')

    response = render(
        request,
        'source/eventtime.tsv',
        {
            'tsvdata': tsvdata,
            'start': start,
            'end': end,
            'station_number': station_number,
        },
        content_type=MIME_TSV,
    )
    response[
        'Content-Disposition'
    ] = f'attachment; filename=eventtime-s{station_number}-{start:%Y%-m%-d}-{end:%Y%-m%-d}.tsv'
    return response


def get_eventtime_histogram_sources(station_number, start, end):
    histograms = get_list_or_404(
        DailyHistogram.objects.select_related('summary'),
        summary__station__number=station_number,
        summary__date__gte=start,
        summary__date__lt=end,
        type__slug='eventtime',
    )
    bins = []
    values = []
    hours = arange(24) * 3600
    no_data = [0] * 24
    i = 0
    for date in daterange(start, end):
        # Add new bins for each hour of the day, in GPS timestamps
        timestamp = clock.datetime_to_gps(date)
        bins.extend(timestamp + hours)
        if histograms[i].summary.date == date:
            values.extend(histograms[i].values)
            i += 1
            if i == len(histograms):
                break
        else:
            values.extend(no_data)
    return list(zip(bins, values))


def get_specific_dataset_source(request, station_number, date, type):
    data = get_dataset_source(date, type, station_number)
    response = render(
        request,
        f'source/{type}_dataset.tsv',
        {'data': data, 'date': date, 'station_number': station_number},
        content_type=MIME_TSV,
    )
    response['Content-Disposition'] = f'attachment; filename={type}-s{station_number}-{date:%Y%-m%-d}.tsv'
    return response


def get_specific_config_source(request, station_number, type):
    data = get_config_source(station_number, type)
    response = render(
        request,
        f'source/{type}_config.tsv',
        {'data': data, 'station_number': station_number},
        content_type=MIME_TSV,
    )
    response['Content-Disposition'] = f'attachment; filename={type}-s{station_number}.tsv'
    return response


def get_station_layout_source(request, station_number):
    layouts = StationLayout.objects.filter(
        station__number=station_number,
        active_date__gte=FIRSTDATE,
        active_date__lte=datetime.date.today(),
    )
    if not layouts:
        raise Http404

    for layout in layouts:
        layout.timestamp = calendar.timegm(layout.active_date.utctimetuple())

    response = render(
        request,
        'source/station_layout.tsv',
        {'layouts': layouts, 'station_number': station_number},
        content_type=MIME_TSV,
    )
    response['Content-Disposition'] = f'attachment; filename=station_layout-s{station_number}.tsv'
    return response


def get_detector_timing_offsets_source(request, station_number):
    data = get_detector_timing_offsets(station_number)
    if not len(data):
        raise Http404

    data = [next(rows) for _, rows in groupby(data, key=itemgetter(1, 2, 3, 4))]

    data = [
        (
            clock.datetime_to_gps(r[0]),
            none_to_nan(r[1]),
            none_to_nan(r[2]),
            none_to_nan(r[3]),
            none_to_nan(r[4]),
        )
        for r in data
    ]

    buffer = StringIO()
    writer = csv.writer(buffer, delimiter='\t', lineterminator='\n')
    writer.writerows(data)
    tsvdata = buffer.getvalue().strip('\n')

    response = render(
        request,
        'source/detector_timing_offsets.tsv',
        {'tsvdata': tsvdata, 'station_number': station_number},
        content_type=MIME_TSV,
    )
    response['Content-Disposition'] = f'attachment; filename=detector_timing_offsets-s{station_number}.tsv'
    return response


def get_station_timing_offsets_source(request, ref_station_number, station_number):
    if ref_station_number >= station_number:
        raise Http404

    data = get_station_timing_offsets(ref_station_number, station_number)

    if not len(data):
        try:
            Station.objects.get(number=ref_station_number)
            Station.objects.get(number=station_number)
        except Station.DoesNotExist:
            raise Http404
        else:
            # For existing pair without offsets return (nan, nan),
            # to be handled by analysis software.
            data = [(FIRSTDATE, nan, nan)]

    data = [next(rows) for _, rows in groupby(data, key=itemgetter(1))]

    data = [(clock.datetime_to_gps(r[0]), none_to_nan(r[1]), none_to_nan(r[2])) for r in data]

    buffer = StringIO()
    writer = csv.writer(buffer, delimiter='\t', lineterminator='\n')
    writer.writerows(data)
    tsvdata = buffer.getvalue().strip('\n')

    response = render(
        request,
        'source/station_timing_offsets.tsv',
        {'tsvdata': tsvdata, 'ref_station_number': ref_station_number, 'station_number': station_number},
        content_type=MIME_TSV,
    )
    response[
        'Content-Disposition'
    ] = f'attachment; filename=station_timing_offsets-s{ref_station_number}-s{station_number}.tsv'
    return response


def get_histogram_source(date, type, station_number=None):
    """Get histogram data for a specific date

    :param date: the date for which to get the histogram data.
    :param type: the type of histogram to retrieve.
    :param station_number: if None a NetworkHistogram is looked for, otherwise
        a DailyHistogram for a specific station is looked for.
    :return: list of tuples containing (bin, value) pairs.

    """
    if station_number is None:
        histogram = get_object_or_404(NetworkHistogram, network_summary__date=date, type__slug=type)
    else:
        station_number = int(station_number)
        if type in ['eventtime', 'zenith', 'azimuth']:
            histogram_model = DailyHistogram
        else:
            histogram_model = MultiDailyHistogram

        histogram = get_object_or_404(
            histogram_model,
            summary__station__number=station_number,
            summary__date=date,
            type__slug=type,
        )

    if type in ['eventtime', 'zenith', 'azimuth', 'coincidencetime', 'coincidencenumber']:
        return list(zip(histogram.bins, histogram.values))
    else:
        # Multiple value columns
        return list(zip(histogram.bins, *histogram.values))


def get_dataset_source(date, type, station_number):
    """Get a dataset for a specific date and station

    :param date: the date for which to get the dataset.
    :param type: the type of dataset to retrieve.
    :param station_number: the station to which the data belongs.
    :return: list of tuples containing (x, y) pairs.

    """
    if type in ['barometer', 'temperature']:
        dataset_model = DailyDataset
    else:
        dataset_model = MultiDailyDataset

    dataset = get_object_or_404(
        dataset_model,
        summary__station__number=int(station_number),
        summary__date=date,
        type__slug=type,
    )

    if type in ['barometer', 'temperature']:
        return list(zip(dataset.x, dataset.y))
    else:
        # Multiple value columns
        return list(zip(dataset.x, *dataset.y))


def get_config_source(station_number, type):
    """Get configuration data for a specific station

    :param station_number: station for which to get the configuration data.
    :param type: the type of configuration data to get. The following
                 are supported: voltage, current, gps, trigger.
    :return: list of lists containing the configuration history.

    """
    if type == 'voltage':
        fields = ['timestamp', 'mas_ch1_voltage', 'mas_ch2_voltage', 'slv_ch1_voltage', 'slv_ch2_voltage']
    elif type == 'current':
        fields = ['timestamp', 'mas_ch1_current', 'mas_ch2_current', 'slv_ch1_current', 'slv_ch2_current']
    elif type == 'gps':
        fields = ['timestamp', 'gps_latitude', 'gps_longitude', 'gps_altitude']
    elif type == 'trigger':
        fields = ['timestamp']
        fields.extend(
            f'{device}_ch{channel}_thres_{threshold}'
            for threshold in ['low', 'high']
            for device in ['mas', 'slv']
            for channel in [1, 2]
        )
        fields.extend(['trig_low_signals', 'trig_high_signals', 'trig_and_or', 'trig_external'])
    elif type == 'electronics':
        pass
    else:
        return None

    configs = Configuration.objects.filter(
        summary__station__number=station_number,
        timestamp__gte=FIRSTDATE,
        timestamp__lte=datetime.date.today(),
    ).order_by('timestamp')

    if not configs:
        raise Http404

    if type == 'electronics':
        data = [
            (config.timestamp, config.master, config.slave, config.master_fpga, config.slave_fpga) for config in configs
        ]
    else:
        data = list(configs.values_list(*fields))

    return data


def plot_histogram(histogram):
    """Create a histogram object"""
    type = histogram.type
    return create_plot_object(histogram.bins[:-1], histogram.values, type.bin_axis_title, type.value_axis_title)


def plot_dataset(dataset):
    """Create a dataset plot object"""
    return create_plot_object(dataset.x, dataset.y, dataset.type.x_axis_title, dataset.type.y_axis_title)


def plot_config(type, configs):
    """Create a plot object from station configs"""

    timestamps = [calendar.timegm(config.timestamp.utctimetuple()) for config in configs]
    x_label = 'Date (month/year)'

    if type == 'voltage':
        values = [
            [config.mas_ch1_voltage, config.mas_ch2_voltage, config.slv_ch1_voltage, config.slv_ch2_voltage]
            for config in configs
        ]
        values = list(zip(*values))
        y_label = 'PMT Voltage (V)'
    elif type == 'current':
        values = [
            [config.mas_ch1_current, config.mas_ch2_current, config.slv_ch1_current, config.slv_ch2_current]
            for config in configs
        ]
        values = list(zip(*values))
        y_label = 'PMT Current (mA)'
    if type == 'altitude':
        values = [config.gps_altitude for config in configs if config.gps_altitude != 0.0]
        if not len(values):
            return None
        y_label = 'Altitude (m)'
    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def plot_timing_offsets(station_number):
    """Create a plot object from station configs"""

    data = get_detector_timing_offsets(station_number)
    data = [[clock.datetime_to_gps(row[0]), row[1:]] for row in data]
    data = list(zip(*data))

    if not data:
        return None

    timestamps = data[0]
    values = list(zip(*data[1]))

    x_label = 'Date (month/year)'
    y_label = 'Timing offset (ns)'

    plot_object = create_plot_object(timestamps, values, x_label, y_label)
    return plot_object


def get_detector_timing_offsets(station_number):
    offsets = DetectorTimingOffset.objects.filter(
        summary__station__number=station_number,
        summary__date__gte=FIRSTDATE,
        summary__date__lte=datetime.date.today(),
    )

    data = offsets.values_list('summary__date', 'offset_1', 'offset_2', 'offset_3', 'offset_4')
    return data


def get_station_timing_offsets(ref_station_number, station_number):
    """Get all station timing offsets for a station pair

    :param ref_station_number,station_number: station numbers.
    :return: list of tuples with date, offset, and error.

    """
    offsets = StationTimingOffset.objects.filter(
        ref_summary__station__number=ref_station_number,
        summary__station__number=station_number,
        summary__date__gte=FIRSTDATE,
        summary__date__lte=datetime.date.today(),
    )

    data = offsets.values_list('summary__date', 'offset', 'error')
    return data


def get_gpslocations(configs):
    """Get all valid GPS locations from the configs"""

    gps = [
        (config.gps_latitude, config.gps_longitude, config.gps_altitude)
        for config in configs
        if config.gps_latitude != 0.0 and config.gps_longitude != 0.0
    ]
    return gps


def create_plot_object(x_values, y_series, x_label, y_label):
    if type(y_series[0]) not in [list, tuple]:
        y_series = [y_series]
    data = [[[xv, yv] for xv, yv in zip(x_values, y_values) if yv is not None] for y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label}
    return plot_object


def stations_with_data():
    """Get list of station numbers with valid event or weather data

    :return: list with station numbers for stations that recorded data, either
             weather or shower, between 2004 and now.

    """
    return Station.objects.filter(
        Q(summaries__num_events__isnull=False) | Q(summaries__num_weather__isnull=False),
        summaries__date__gte=FIRSTDATE,
        summaries__date__lte=datetime.date.today(),
    ).distinct()


def station_has_config(station):
    """Check if there is a valid configuration for the given station

    :param station: Station object for which to check.
    :return: boolean indicating if the station has a configuration available.

    """
    return Summary.objects.with_config().filter(station=station).exists()


def station_has_data(station):
    """Check if there is valid event or weather data for the given station

    :param station: Station object for which to check.
    :return: boolean indicating if the station has recorded data, either
             weather or shower, between 2002 and now.

    """
    return Summary.objects.with_data().filter(station=station).exists()


def none_to_nan(x):
    if x is None:
        return nan
    else:
        return x


def help(request):
    """Show the static help page"""
    return render(request, 'status_display/help.html')
