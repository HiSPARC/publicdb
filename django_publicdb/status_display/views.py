from django.shortcuts import render_to_response, get_object_or_404
from django_publicdb.histograms.models import *
from django.conf import settings

from django_publicdb.histograms.models import *

import enthought.chaco.api as chaco
import os
from numpy import arange, pi, sin
import datetime

def status(request):
    """Show eventwarehouse status"""

    return

def station_histograms(request, station_id, year, month, day):
    """Show daily histograms for a particular station"""

    station_id = int(station_id)
    year = int(year)
    month = int(month)
    day = int(day)

    eventhistogram = create_histogram('eventtime', station_id, year, month,
                                      day)
    pulseheighthistogram = create_histogram('pulseheight', station_id,
                                            year, month, day, log=True)
    pulseintegralhistogram = create_histogram('pulseintegral', station_id,
                                              year, month, day, log=True)

    return render_to_response('station_histograms.html',
        { 'eventhistogram': eventhistogram,
          'pulseheighthistogram': pulseheighthistogram,
          'pulseintegralhistogram': pulseintegralhistogram,
        })

def station_yesterday(request, station_id):
    """Show yesterday's histograms for a particular station"""

    return

def create_histogram(type, station_id, year, month, day, log=False):
    """Create a histogram and save it to disk"""

    name = 'histogram-%s-%d-%d-%02d-%02d.png' % (type, station_id, year,
                                                 month, day)
    date = datetime.date(year, month, day)
    source = get_object_or_404(Summary, station_id=station_id, date=date)
    type = HistogramType.objects.get(slug__exact=type)
    histogram = get_object_or_404(DailyHistogram, source=source, type=type)
    
    plot = create_histogram_plot(histogram.bins, histogram.values,
                                 type.has_multiple_datasets, log)
    render_and_save_plot(plot, name)

    return settings.MEDIA_URL + name

def create_histogram_plot(bins, values, has_multiple_datasets, log):
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

    return view

def render_and_save_plot(plot, name):
    plot.bounds = [500, 333]
    plot.padding = 50
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
