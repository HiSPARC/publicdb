<<<<<<< HEAD
from django.shortcuts               import render_to_response, get_object_or_404, redirect
from django.template                import RequestContext
from django.core.context_processors import csrf
from django.conf                    import settings
from django.core.mail               import send_mail
from django.http                    import HttpResponseRedirect, HttpResponse
=======
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect
>>>>>>> master

import numpy as np
from numpy import pi, arccos, arcsin, arctan2, sin, cos
import operator
import os
import datetime
import calendar

from models import *
from forms import *
from recaptcha.client import captcha


def data_display(request, slug):
    """Simple data display for symposium results"""

    session = get_object_or_404(AnalysisSession, slug=slug)
    coincidences = AnalyzedCoincidence.objects.filter(session=session,
                                                      is_analyzed=True)
    energy_histogram = create_energy_histogram(slug, coincidences)
    core_plot = None # create_core_plot(slug, coincidences)
    star_map = None # create_star_map(slug, coincidences)
    scores = top_lijst(slug)
    title = session.title
    pin = session.pin

    return render_to_response('results.html',
        {'energy_histogram': energy_histogram,
         'core_plot': core_plot,
         'star_map': star_map,
         'scores': scores,
         'slug': slug,
         'session': session},
        context_instance=RequestContext(request))


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


def create_core_plot(slug, coincidences):
    """Create a plot showing analyzed shower cores"""

    if 'middelharnis' in slug:
        xbounds = (4.15268, 4.16838)
        ybounds = (51.75011, 51.76069)
        filename = 'map-middelharnis.png'
    else:
        xbounds = (4.93772, 4.96952)
        ybounds = (52.34542, 52.36592)
        filename = 'map-flipped.png'

    x, y, logenergy = get_core_positions(coincidences)
    data.set_data('x', x)
    data.set_data('y', y)
    data.set_data('logenergy', logenergy)

    image_file = os.path.join(settings.MEDIA_ROOT, 'static', filename)
    image = chaco.ImageData.fromfile(image_file)
    data.set_data('map', image.get_data())

    plot.img_plot('map', xbounds=xbounds, ybounds=ybounds)
    plot.plot(('x', 'y', 'logenergy'), type='cmap_scatter', marker='circle',
              marker_size=3, color_mapper=chaco.autumn)

    i = plot.index_range
    i.low_setting, i.high_setting = xbounds
    v = plot.value_range
    v.low_setting, v.high_setting = ybounds

    render_and_save_plot(plot, name, 300, 326)
    return plot_object


def create_star_map(slug, coincidences):
    """Create a star map showing analyzed shower origins"""

    name = 'symposium-starmap-%s.png' % slug

    data = chaco.ArrayPlotData()
    plot = chaco.Plot(data)

    lat = np.radians(52.3559179545)
    lon = 4.95114534876
    J2000 = calendar.timegm(datetime.datetime(2000, 1, 1, 12).utctimetuple())
    logenergy = []
    x = []
    y = []
    for c in coincidences:
        D = (calendar.timegm(datetime.datetime.combine(c.coincidence.date,
             c.coincidence.time).utctimetuple()) - J2000) / 86400
        GMST = 18.697374558 + 24.06570982441908 * D
        lst = GMST + lon / 15
        lst = lst / 24 * 2 * pi

        alt = pi / 2 - c.theta
        az = pi / 2 - c.phi

        dec = arcsin(sin(lat) * sin(alt) - cos(lat) * cos(alt) * cos(az))
        H = arctan2(sin(az) * cos(alt),
                    cos(lat) * sin(alt) + sin(lat) * cos(alt) * cos(az))
        ra = lst - H

        r = 1 - 2 * dec / pi
        if r > 1.:
            r *= .5
        x.append(r * sin(ra))
        y.append(r * cos(ra))
        logenergy.append(c.log_energy)

    data.set_data('x', x)
    data.set_data('y', y)
    data.set_data('logenergy', logenergy)

    image_file = os.path.join(settings.MEDIA_ROOT, 'static', 'starmap.gif')
    image = chaco.ImageData.fromfile(image_file)
    data.set_data('map', image.get_data())

    xbounds = (-1, 1)
    ybounds = (-1, 1)
    plot.img_plot('map', xbounds=xbounds, ybounds=ybounds)
    plot.plot(('x', 'y', 'logenergy'), type='cmap_scatter', marker='circle',
              marker_size=3, color_mapper=chaco.autumn)

    i = plot.index_range
    i.low_setting, i.high_setting = xbounds
    v = plot.value_range
    v.low_setting, v.hvgh_setting = ybounds

    render_and_save_plot(plot, name, 300, 300)
    return settings.MEDIA_URL + name


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

def request_form( request ):

    if request.method == 'POST':
        form = SessionRequestForm( request.POST )
    else:
        form = SessionRequestForm()

    #----------------
    # Render response
    #----------------

    html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)

    return render_to_response('request.html',
                              {'form': form, 'html_captcha': html_captcha},
                              context_instance = RequestContext(request))

def validate_request_form( request ):

    if request.method != 'POST':
        return redirect( request_form )

    #----------------------
    # Check reCaptcha input
    #----------------------

    if not settings.RECAPTCHA_DISABLE_CHECK:

        check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'],
                                       request.POST['recaptcha_response_field'],
                                       settings.RECAPTCHA_PRIVATE_KEY,
                                       request.META['REMOTE_ADDR'])

        if not check_captcha.is_valid:
            return request_form(request)

        #html_captcha = captcha.displayhtml(
        #    settings.RECAPTCHA_PUB_KEY,
        #    error=check_captcha.error_code
        #)

    #-----------------
    # Check form input
    #-----------------

    form = SessionRequestForm(request.POST)

    if not form.is_valid():
        return request_form(request)

    #-----------
    # Send email
    #-----------

    data = {}
    data.update(form.cleaned_data)

    new_request=SessionRequest(
        first_name = data['first_name'],
        sur_name = data['sur_name'],
        email = data['email'],
        school = data['school'],
        cluster = data['cluster'],
        start_date = data['start_date'],
        mail_send = False,
        session_created = False,
        session_pending = True,
        events_to_create = data['number_of_events'],
        events_created = 0
    )

    new_request.GenerateUrl()
    new_request.save()
    new_request.SendMail()

    #----------------
    # Return response
    #----------------

    return render_to_response('thankyou.html')

def confirm_request(request, url):
    sessionrequest = get_object_or_404(SessionRequest, url=url)
    if sessionrequest.session_confirmed == False:
       sessionrequest.sid = sessionrequest.school + str(sessionrequest.id)
       sessionrequest.pin = randint(1000, 9999)
       starts = datetime.datetime.now()
       ends = datetime.datetime.now()
       session = AnalysisSession(starts=starts,
                                 ends=ends,
                                 pin=str(sessionrequest.id),
                                 title=sessionrequest.sid)

       sessionrequest.session_confirmed = True
       sessionrequest.save()
    return render_to_response('confirm.html',
            {'id': sessionrequest.sid, 'pin': sessionrequest.pin},
            context_instance=RequestContext(request))


def create_request(request):
    sessionlist = (SessionRequest.objects.filter(session_confirmed=True)
                                         .filter(session_pending=True))
    for sessionrequest in sessionlist:
        sessionrequest.session_confirmed=False
        sessionrequest.save()

    for sessionrequest in sessionlist:
        sessionrequest.create_session()
    return HttpResponse('')
