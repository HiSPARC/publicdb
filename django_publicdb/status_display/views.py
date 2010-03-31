from django.shortcuts import render_to_response, get_object_or_404, \
                             redirect
from django.template import RequestContext
from django.conf import settings

import calendar
import os
from numpy import arange, pi, sin, linspace
import datetime

from enthought.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'null'
ETSConfig.enable_toolkit = 'null'
import enthought.chaco.api as chaco

from django_publicdb.histograms.models import *
from django_publicdb.inforecords.models import *


def stations(request):
    """Show a list of stations, ordered by cluster"""

    clusters = []
    for cluster in Cluster.objects.all():
        stations = []
        for station in Station.objects.filter(location__cluster=cluster):
            try:
                Summary.objects.filter(station=station)[0]
                link = station.number
            except IndexError:
                link = None

            stations.append({'number': station.number,
                             'name': station.location.name,
                             'link': link})
        clusters.append({'name': cluster.name, 'stations': stations})

    return render_to_response('stations.html', {'clusters': clusters},
                              context_instance=RequestContext(request))

def station_histograms(request, station_id, year, month, day):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)
    year = int(year)
    month = int(month)
    day = int(day)
    
    if (month, day) == (3, 31):
        # This data is shown on April, 1st
        april_fools_day = True
        (month, day) = (3, 24)
    else:
        april_fools_day = False

    station = get_object_or_404(Station, number=station_id)
    tomorrow = (datetime.date(year, month, day) +
                datetime.timedelta(days=1))
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

    eventhistogram = create_histogram('eventtime', station, year, month,
                                      day, april_fools_day)
    pulseheighthistogram = create_histogram('pulseheight', station,
                                            year, month, day,
                                            april_fools_day, log=True)
    pulseintegralhistogram = create_histogram('pulseintegral', station,
                                              year, month, day,
                                              april_fools_day, log=True)

    return render_to_response('station_histograms.html',
        { 'station': station,
          'date': datetime.date(year, month, day),
          'config': config,
          'has_slave': has_slave,
          'eventhistogram': eventhistogram,
          'pulseheighthistogram': pulseheighthistogram,
          'pulseintegralhistogram': pulseintegralhistogram,
          'thismonth': thismonth,
          'month_list': month_list,
          'year_list': year_list,
          'link': (station_id, year, month, day),
        }, context_instance=RequestContext(request))

def station(request, station_id):
    """Show most recent histograms for a particular station"""

    summary = (Summary.objects.filter(station__number=station_id)
                              .latest('date'))
    return redirect(station_histograms, station_id=str(station_id),
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
    data = get_histogram_source(station_id, year, month, day,
                                'pulseheight')
    response = render_to_response('source_pulseheight_histogram.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=pulseheight-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response

def get_pulseintegral_histogram_source(request, station_id, year, month, day):
    data = get_histogram_source(station_id, year, month, day,
                                'pulseintegral')
    response = render_to_response('source_pulseintegral_histogram.csv',
                                  {'data': data}, mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=pulseintegral-%s-%s-%s-%s.csv' %
        (station_id, year, month, day))
    return response

def get_histogram_source(station_id, year, month, day, type):
    histogram = DailyHistogram.objects.get(
                    source__station__number=int(station_id),
                    source__date=datetime.date(int(year), int(month),
                                               int(day)),
                    type__slug=type)
    if type == 'eventtime':
        return zip(histogram.bins, histogram.values)
    else:
        return zip(histogram.bins, *histogram.values)

def create_histogram(type, station, year, month, day, april_fools_day,
                     log=False):
    """Create a histogram and save it to disk"""

    name = 'histogram-%s-%d-%d-%02d-%02d.png' % (type, station.number,
                                                 year, month, day)
    date = datetime.date(year, month, day)
    source = get_object_or_404(Summary, station=station, date=date)
    type = HistogramType.objects.get(slug__exact=type)
    histogram = get_object_or_404(DailyHistogram, source=source, type=type)

    if april_fools_day:
        if type.slug == 'eventtime':
            histogram.values = [x * (1 + .15 * sin(y - .3 * pi)) for x, y
                                in zip(histogram.values, linspace(0, 2 *
                                                                  pi, 24))]
        if type.slug == 'pulseheight':
            w = []
            for v in histogram.values:
                u = []
                for x in [0] * 10 + v[10:]:
                    u.extend([.2 * x, .2 * x])
                w.append([x + y for x, y in zip(v, u)])
            histogram.values = w
        if type.slug == 'pulseintegral':
            w = []
            for v in histogram.values:
                u = []
                for x in [0] * 10 + v[10:]:
                    u.extend([.1 * x, .1 * x])
                w.append([x + y for x, y in zip(v, u)])
            histogram.values = w

    plot = create_histogram_plot(histogram.bins, histogram.values,
                                 type.has_multiple_datasets,
                                 type.bin_axis_title,
                                 type.value_axis_title, log)

    width, height = 500, 333
    if type.slug == 'eventtime':
        height = 150
    render_and_save_plot(plot, name, width, height)

    return settings.MEDIA_URL + name

def create_histogram_plot(bins, values, has_multiple_datasets,
                          bin_axis_title, value_axis_title, log):
    """Convenience function for creating histogram plots"""

    if has_multiple_datasets:
        datasets = values
        color = colors()
    else:
        # simulate multiple datasets
        datasets = [values]
        color = monochrome()

    view = chaco.DataView()
    index = chaco.ArrayDataSource(bins)
    view.index_range.add(index)
    index_mapper = chaco.LinearMapper(range=view.index_range)

    for values in datasets:
        values.append(values[-1])
    
        value = chaco.ArrayDataSource(values)
        view.value_range.add(value)

        if log:
            value_mapper = chaco.LogMapper(range=view.value_range)
        else:
            value_mapper = chaco.LinearMapper(range=view.value_range)

        plot = chaco.LinePlot(index=index, value=value,
                              index_mapper=index_mapper,
                              value_mapper=value_mapper,
                              render_style='connectedhold',
                              color=color.next(),
                              line_width=1.5)
        view.add(plot)

    if log:
        view.value_mapper = chaco.LogMapper()
        view.value_range.low_setting = 1
    else:
        view.value_range.low_setting = 0

    #FIXME
    if datasets:
        view.value_range.high_setting = max([max(x) for x in datasets]) * 1.1

    view.x_axis.title = bin_axis_title
    view.y_axis.title = value_axis_title
    view.x_axis.title_font = 'modern bold 16'
    view.y_axis.title_font = 'modern bold 16'
    view.x_axis.title_spacing = 20

    return view

def render_and_save_plot(plot, name, width, height):
    plot.bounds = [width, height]
    plot.padding = (60, 10, 10, 50)
    gc = chaco.PlotGraphicsContext(plot.outer_bounds)
    gc.render_component(plot)
    path = os.path.join(settings.MEDIA_ROOT, name)
    gc.save(path)

def colors():
    """Generator function which returns color names"""

    colors = [[1., 0., 0., .7,],
              [0., 1., 0., .7,],
              [0., 0., 1., .7,],
              [1., 0., 1., .7,],
             ]

    for color in colors:
        yield color

def monochrome():
    """Generator function which returns monochrome color names"""

    color = 'black'

    while True:
        yield color

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
                    summary = Summary.objects.get(station=station,
                                                  date=day)
                    link = (station.number, theyear, themonth, day.day)
                except Summary.DoesNotExist:
                    link = None
                days.append({'day': '%2d' % day.day, 'link': link})
            else:
                days.append('')
        weeks.append(days)

    return {'month': month_name, 'days': days_names, 'weeks': weeks}

def nav_months(station, theyear):
    """Create list of months with links"""

    date_list = (Summary.objects.filter(station=station,
                                       date__year=theyear).
                 dates('date', 'month'))

    month_list = []
    for date in date_list:
        name = calendar.month_name[date.month][:3]
        first_day = (Summary.objects.filter(station=station,
                                            date__year=date.year,
                                            date__month=date.month).
                     dates('date', 'day')[0])
        link = (station.number, date.year, date.month, first_day.day)
        month_list.append({'month': name, 'link': link})

    return month_list

def nav_years(station):
    """Create list of previous years"""

    date_list = Summary.objects.filter(station=station).dates('date',
                                                              'year')

    year_list = []
    for date in date_list:
        first_day = (Summary.objects.filter(station=station,
                                            date__year=date.year).
                      dates('date', 'day')[0])
        link = (station.number, date.year, first_day.month, first_day.day)
        year_list.append({'year': date.year, 'link': link})

    return year_list
