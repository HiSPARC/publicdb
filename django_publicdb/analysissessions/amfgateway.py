from pyamf.remoting.gateway.django import DjangoGateway

from django_publicdb.coincidences.models import *
from django_publicdb.analysissessions.models import *
from django_publicdb.inforecords.models import *

from views import top_lijst

from numpy import average
import datetime
import calendar

#FIXME
import random

def get_services(request):
    return services.keys()

def get_coincidence(request, session_hash, student_name):
    try:
        session = AnalysisSession.objects.get(hash=session_hash)
    except AnalysisSession.DoesNotExist:
        raise Exception('No such analysis session!')
    else:
        if not session.in_progress:
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

    events = []
    for event in coincidence.coincidence.events.all():
        # don't pulseheights which are -999 (baseline error)
        signal = [x for x in event.pulseheights if x != -999]
        # dirty way to estimate muon equivalent, using the aimed-for muon
        # peak position
        mips = average(signal) / 200

        station = event.station
        detector = DetectorHisparc.objects.get(station=station)
        dt = datetime.datetime.combine(event.date, event.time)
        timestamp = calendar.timegm(dt.utctimetuple())
        events.append({'timestamp': timestamp,
                       'nanoseconds': event.nanoseconds,
                       'mips': mips,
                       'station': station.number,
                       'latitude': detector.latitude,
                       'longitude': detector.longitude,
                       'traces': [list(x) for x in event.traces]})
    return coincidence.pk, events, rank

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

def get_energy_data(request):
    energies = []
    coincidences = AnalyzedCoincidence.objects.filter(is_analyzed=True)
    for c in coincidences:
        energies.append(c.log_energy)
    return energies


services = { 'hisparc.get_services': get_services,
             'hisparc.get_coincidence': get_coincidence,
             'hisparc.send_results': send_results,
             'hisparc.get_energy_data': get_energy_data,
           }
public_gateway = DjangoGateway(services)
