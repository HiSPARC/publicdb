from django.shortcuts import render_to_response
from django.conf import settings

import numpy as np

from models import *
from django_publicdb.status_display.views import create_histogram_plot, \
                                                 render_and_save_plot

def data_display(request):
    """Simple data display for symposium results"""

    energy_histogram = create_energy_histogram()

    return render_to_response('symposium-data.html',
        {'energy_histogram': energy_histogram,
        })

def create_energy_histogram():
    """Create an energy histogram"""

    name = 'symposium-energy.png'

    energies = [x.log_energy for x in
                AnalyzedCoincidence.objects.filter(is_analyzed=True)]

    values, bins = np.histogram(energies, bins=np.arange(14, 23, 1))

    plot = create_histogram_plot(bins, values.tolist(), False,
                                 'Log energy (eV)', 'Count', log=False)
    render_and_save_plot(plot, name, 500, 333)

    return settings.MEDIA_URL + name
