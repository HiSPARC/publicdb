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

    session_hash = request.GET.get('session_hash', None)
    student_name = request.GET.get('student_name', None)

    try:
        session = AnalysisSession.objects.get(hash=session_hash)
    except AnalysisSession.DoesNotExist:
        raise Exception('No such analysis session!')
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
                     integrals=e.integrals)
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

def send_results(request, pk, core_position, log_energy, error_estimate):
    coincidence = AnalyzedCoincidence.objects.get(pk=pk)

    if coincidence.student.name == 'Test student':
        return
    else:
        coincidence.core_position_x, coincidence.core_position_y = \
            core_position
        coincidence.log_energy = log_energy
        #FIXME
        coincidence.theta = random.normalvariate(22, 10)
        coincidence.phi = random.uniform(0., 360.)
        coincidence.error_estimate = error_estimate
        coincidence.is_analyzed = True
        coincidence.save()
