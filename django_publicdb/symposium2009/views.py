from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

import numpy as np
import operator

from models import *
from django_publicdb.status_display.views import create_histogram_plot, \
                                                 render_and_save_plot
import enthought.chaco.api as chaco

def data_display(request):
    """Simple data display for symposium results"""

    energy_histogram = create_energy_histogram()
    core_plot = create_core_plot()
    scores = top_lijst()

    return render_to_response('symposium-data.html',
        {'energy_histogram': energy_histogram,
         'core_plot': core_plot,
         'scores': scores,
        }, context_instance=RequestContext(request))

def create_energy_histogram():
    """Create an energy histogram"""

    name = 'symposium-energy.png'

    energies = [x.log_energy for x in
                AnalyzedCoincidence.objects.filter(is_analyzed=True)]
    good_energies = [x.log_energy for x in
                     AnalyzedCoincidence.objects.filter(is_analyzed=True,
                     error_estimate__lte=100.)]

    v1, bins = np.histogram(energies, bins=np.arange(14, 23, 1))
    v2, bins = np.histogram(good_energies, bins=np.arange(14, 23, 1))
    values = [v1.tolist(), v2.tolist()]

    plot = create_histogram_plot(bins, values, True,
                                 'Log energy (eV)', 'Count', log=False)
    render_and_save_plot(plot, name, 400, 266)

    return settings.MEDIA_URL + name

def create_core_plot():
    """Create a plot showing analyzed shower cores"""

    name = 'symposium-cores.png'

    data = chaco.ArrayPlotData()
    plot = chaco.Plot(data)

    x, y, logenergy = get_core_positions()
    data.set_data('x', x)
    data.set_data('y', y)
    data.set_data('logenergy', logenergy)

    image = chaco.ImageData.fromfile('/var/www/django_publicdb/symposium2009/map-flipped.png')
    data.set_data('map', image.get_data())

    xbounds = (4.93772, 4.96952)
    ybounds = (52.34542, 52.36592)
    plot.img_plot('map', xbounds=xbounds, ybounds=ybounds)
    plot.plot(('x', 'y', 'logenergy'), type='cmap_scatter',
              marker='circle', marker_size=3, color_mapper=chaco.autumn)

    i = plot.index_range
    i.low_setting, i.high_setting = xbounds
    v = plot.value_range
    v.low_setting, v.hvgh_setting = ybounds

    render_and_save_plot(plot, name, 400, 400)
    return settings.MEDIA_URL + name

def top_lijst():
    scores = []
    for s in Student.objects.all():
        error = []
        num_events = 0
        for ac in AnalyzedCoincidence.objects.filter(student=s):
            if ac.error_estimate:
                error.append(ac.error_estimate)
                num_events += 1
        if error:
            avg_error = np.average(error)
            wgh_error = avg_error / num_events
            min_error = min(error)
            scores.append({'name': s.name, 'avg_error': avg_error,
                           'wgh_error': wgh_error, 'min_error': min_error,
                           'num_events': num_events})

    return sorted(scores, key=operator.itemgetter('wgh_error'))

def get_core_positions():
    x, y, logenergy = [], [], []
    for c in AnalyzedCoincidence.objects.filter(is_analyzed=True):
        x.append(c.core_position_x)
        y.append(c.core_position_y)
        logenergy.append(c.log_energy)

    return x, y, logenergy
