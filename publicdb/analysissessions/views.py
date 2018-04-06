import datetime
import operator

from random import randint

import numpy as np

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SessionRequestForm
from .models import (AnalysisSession, AnalyzedCoincidence, SessionRequest,
                     Student)


def data_display(request, slug):
    """Simple data display for symposium results"""

    session = get_object_or_404(AnalysisSession, slug=slug)
    coincidences = AnalyzedCoincidence.objects.filter(session=session,
                                                      is_analyzed=True)
    energy_histogram = create_energy_histogram(slug, coincidences)
    core_map = get_cores(slug, coincidences)
    star_map = None  # create_star_map(slug, coincidences)
    scores = top_lijst(slug)

    return render(request, 'analysissessions/results.html',
                  {'energy_histogram': energy_histogram,
                   'core_map': core_map,
                   'star_map': star_map,
                   'scores': scores,
                   'slug': slug,
                   'session': session})


def create_energy_histogram(slug, coincidences):
    """Create an energy histogram"""

    energies = [x.log_energy for x in coincidences]
    good_energies = [x.log_energy for x in
                     coincidences.filter(error_estimate__lte=100.)]

    v1, bins = np.histogram(energies, bins=np.arange(14, 23, 1))
    v2, bins = np.histogram(good_energies, bins=np.arange(14, 23, 1))
    values = [v1.tolist(), v2.tolist()]

    plot_object = create_plot_object(bins[:-1], values, 'Log energy (eV)',
                                     'Count')
    return plot_object


def get_cores(slug, coincidences):
    """Create data to plot on map"""

    cores = [(c.core_position_y, c.core_position_x) for c in coincidences]

    return cores


def create_plot_object(x_values, y_series, x_label, y_label):
    if type(y_series[0]) != list:
        y_series = [y_series]

    data = [[[xv, yv] for xv, yv in zip(x_values, y_values)] for
            y_values in y_series]

    plot_object = {'data': data, 'x_label': x_label, 'y_label': y_label}
    return plot_object


def top_lijst(slug):
    coincidences = AnalyzedCoincidence.objects.filter(session__slug=slug,
                                                      is_analyzed=True)
    scores = []
    for s in Student.objects.all():
        error = []
        num_events = 0
        for ac in coincidences.filter(student=s):
            if ac.error_estimate:
                error.append(ac.error_estimate)
                num_events += 1
        error.sort()
        if error:
            if len(error) > 1 and slug != 'leerlingensymposium-2010':
                error = error[:-1]
            avg_error = np.average(error)
            wgh_error = avg_error / num_events
            min_error = min(error)
            scores.append({'name': s.name, 'avg_error': avg_error,
                           'wgh_error': wgh_error, 'min_error': min_error,
                           'num_events': num_events})

    return sorted(scores, key=operator.itemgetter('wgh_error'))


def get_core_positions(coincidences):
    x, y, logenergy = [], [], []
    for c in coincidences:
        x.append(c.core_position_x)
        y.append(c.core_position_y)
        logenergy.append(c.log_energy)
    return x, y, logenergy


def request_form(request):
    if request.method == 'POST':
        form = SessionRequestForm(request.POST)
    else:
        form = SessionRequestForm()

    return render(request, 'analysissessions/request.html', {'form': form})


def validate_request_form(request):
    if request.method != 'POST':
        return redirect('sessions:request')

    # Check form input
    form = SessionRequestForm(request.POST)

    if not form.is_valid():
        return request_form(request)

    # Send email and show overview
    data = {}
    data.update(form.cleaned_data)

    new_request = SessionRequest(first_name=data['first_name'],
                                 sur_name=data['sur_name'],
                                 email=data['email'],
                                 school=data['school'],
                                 cluster=data['cluster'],
                                 start_date=data['start_date'],
                                 mail_send=False,
                                 session_created=False,
                                 session_pending=True,
                                 events_to_create=data['number_of_events'],
                                 events_created=0)

    new_request.generate_url()
    new_request.save()
    new_request.sendmail_request()

    return render(request, 'analysissessions/thankyou.html', {'data': data})


def confirm_request(request, url):
    sessionrequest = get_object_or_404(SessionRequest, url=url)
    if sessionrequest.session_confirmed is False:
        sessionrequest.sid = sessionrequest.school + str(sessionrequest.id)
        sessionrequest.pin = randint(1000, 9999)
        starts = datetime.datetime.now()
        ends = datetime.datetime.now()
        AnalysisSession(starts=starts, ends=ends,
                        pin=str(sessionrequest.id), title=sessionrequest.sid)
        sessionrequest.session_confirmed = True
        sessionrequest.save()
    return render(request, 'analysissessions/confirm.html',
                  {'id': sessionrequest.sid,
                   'pin': sessionrequest.pin})


def create_session(request):
    sessionlist = SessionRequest.objects.filter(session_confirmed=True,
                                                session_pending=True)
    for sessionrequest in sessionlist:
        sessionrequest.session_confirmed = False
        sessionrequest.save()

    for sessionrequest in sessionlist:
        sessionrequest.create_session()
    return HttpResponse('')
