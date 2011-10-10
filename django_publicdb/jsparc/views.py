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
    """Return a coincidence for jsparc client test"""

    session_title = request.GET.get('session_title', None)
    session_pin = request.GET.get('session_pin', None)
    student_name = request.GET.get('student_name', None)

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
        coincidence = coincidences.filter(student=None,
                                          is_analyzed=False)[0]
        coincidence.student = student
        coincidence.save()

    c = coincidence
    events = []
    for e in c.coincidence.events.all():
        s = e.station
        d = s.detectorhisparc_set.all().reverse()[0]


        event = dict(timestamp=calendar.timegm(datetime.datetime.combine(e.date, e.time).utctimetuple()),
                     nanoseconds=e.nanoseconds, number=s.number,
                     lat=d.latitude, lon=d.longitude, alt=d.height,
                     status='on', detectors=len(e.traces),
                     traces=e.traces, pulseheights=e.pulseheights,
                     integrals=e.integrals,
                     mips=[x / 200. for x in e.pulseheights])
        events.append(event)

    data = dict(pk=c.pk, timestamp=calendar.timegm(datetime.datetime
                                                  .combine(c.coincidence.date,
                                                           c.coincidence.time)
                                                  .utctimetuple()),
                nanoseconds=c.coincidence.nanoseconds, events=events)

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
    session_hash = request.GET['session_hash']
    student_name = request.GET['student_name']
    pk = request.GET['pk']
    lat = request.GET['lat']
    lon = request.GET['lon']
    log_energy = request.GET['logEnergy']
    error_estimate = request.GET['error']
    
    coincidence = AnalyzedCoincidence.objects.get(pk=pk)
    assert coincidence.session.hash == session_hash
    assert coincidence.student.name == student_name

    if coincidence.student.name == 'Test student':
        return
    else:
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

    response = HttpResponse(json.dumps(dict(msg="OK [result stored]",rank=rank)),
                            mimetype='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
