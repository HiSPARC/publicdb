from django.http import HttpResponse

import calendar
import datetime
import json
from random import randrange
import numpy as np
import operator

from django_publicdb.coincidences.models import *
from django_publicdb.analysissessions.models import *
from django_publicdb.inforecords.models import *


def get_coincidence(request):
    """Return a coincidence for jSparc client"""
    print("got jSparc coincidence request")
    session_title = request.GET.get('session_title', None)
    session_pin = request.GET.get('session_pin', None)
    student_name = request.GET.get('student_name', None)

    if session_title.lower() == 'example':
        count = AnalyzedCoincidence.objects.count()
        random_index = randint(0, count - 1)
        coincidence = AnalyzedCoincidence.objects.all()[random_index]
        events = get_events(coincidence)
        response = data_json(coincidence, events)
        return response

    try:
        session = AnalysisSession.objects.get(title=session_title)
        if session.pin != session_pin:
            raise ValueError('Wrong pin for this session')
    except AnalysisSession.DoesNotExist:
        raise Exception('No such analysis session!')
    except ValueError:
        raise
    else:
        if not session.in_progress():
            raise Exception("Analysis session hasn't started yet or "
                            "is already closed!")

    if not student_name:
        student = Student.objects.get(session=session,
                                      name='Test student')
    else:
        student, is_created = Student.objects.get_or_create(
                                    session=session, name=student_name)

    ranking = top_lijst(session.slug)
    try:
        rank = [x['name'] for x in ranking].index(student_name) + 1
    except ValueError:
        rank = None

    coincidences = AnalyzedCoincidence.objects.filter(session=session)
    try:
        coincidence = coincidences.filter(student=student,
                                          is_analyzed=False)[0]
    except IndexError:
        coincidence = coincidences.filter(student=None, is_analyzed=False)[0]
        coincidence.student = student
        coincidence.save()

    events = get_events(coincidence)
    response = data_json(coincidence, events)
    return response


def get_events(coincidence):
    events = []
    for e in coincidence.coincidence.events.all():
        s = e.station
        d = s.detectorhisparc_set.all().reverse()[0]

        event = dict(timestamp=calendar.timegm(datetime.datetime
                                               .combine(e.date, e.time)
                                               .utctimetuple()),
                     nanoseconds=e.nanoseconds,
                     number=s.number,
                     lat=d.latitude,
                     lon=d.longitude,
                     alt=d.height,
                     status='on',
                     detectors=len(e.traces),
                     traces=e.traces,
                     pulseheights=[np.asscalar(u) for u in e.pulseheights],
                     integrals=[np.asscalar(u) for u in e.integrals],
                     mips=[x / 200. for x in e.pulseheights])
        events.append(event)
    return events


def data_json(coincidence, events):
    data = dict(pk=coincidence.pk,
            timestamp=calendar.timegm(datetime.datetime
                    .combine(coincidence.coincidence.date,
                             coincidence.coincidence.time).utctimetuple()),
            nanoseconds=coincidence.coincidence.nanoseconds,
            events=events)
    response = HttpResponse(json.dumps(data), mimetype='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


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
        if error:
            avg_error = np.average(error)
            wgh_error = avg_error / num_events
            min_error = min(error)
            scores.append({'name': s.name, 'avg_error': avg_error,
                           'wgh_error': wgh_error, 'min_error': min_error,
                           'num_events': num_events})

    return sorted(scores, key=operator.itemgetter('wgh_error'))


def result(request):
    session_title = request.GET['session_title']
    student_name = request.GET['student_name']
    pk = request.GET['pk']
    lat = request.GET['lat']
    lon = request.GET['lon']
    log_energy = request.GET['logEnergy']
    error_estimate = request.GET['error']

    # Possible break
    if session_title.lower() == 'example':
        return test_result()

    coincidence = AnalyzedCoincidence.objects.get(pk=pk)
    assert coincidence.session.title.lower() == session_title.lower()
    assert coincidence.student.name.lower() == student_name.lower()

    # Possible break
    if coincidence.student.name == 'Test student':
        return test_result()

    coincidence.core_position_x = lon
    coincidence.core_position_y = lat
    coincidence.log_energy = log_energy
    coincidence.error_estimate = error_estimate
    coincidence.is_analyzed = True
    #FIXME
    coincidence.theta = 0
    coincidence.phi = 0
    coincidence.save()

    ranking = top_lijst(coincidence.session.slug)
    try:
        rank = [x['name'] for x in ranking].index(student_name) + 1
    except ValueError:
        rank = None
    msg = "OK [result stored]"
    response = HttpResponse(json.dumps(dict(msg=msg, rank=rank)),
                            mimetype='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def test_result():
    msg = "Test session, result not stored"
    rank = randint(0, 10)
    response = HttpResponse(json.dumps(dict(msg=msg, rank=rank)),
                            mimetype='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
