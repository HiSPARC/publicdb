from pyamf.remoting.gateway.django import DjangoGateway
from django.core.exceptions import ObjectDoesNotExist

from coincidences.models import *
from models import *

from numpy import average

def get_services(request):
    return services.keys()

def get_coincidence(request, student_name):
    if not student_name:
        return None, None

    try:
        student = Student.objects.get(name=student_name)
    except ObjectDoesNotExist:
        student = Student(name=student_name)
        student.save()

    coincidence = AnalyzedCoincidence.objects.filter(student=None)[0]
    coincidence.student = student
    coincidence.save()

    events = []
    for e in coincidence.coincidence.events.all():
        signal = [e.pulseheight1, e.pulseheight2, e.pulseheight3,
                  e.pulseheight4]
        # remove signals which are -999 (=> 569.43) baseline error
        signal = [x for x in signal if x < 500]
        signal = average(signal)
        # dirty way to estimate muon equivalent
        signal /= -227
        print e.detector, e.event_id, e.pulseheight1, e.pulseheight2, e.pulseheight3, e.pulseheight4
        event = {'latitude': e.latitude, 'longitude': e.longitude,
                 'signal': signal}
        events.append(event)
    return coincidence.pk, events

def send_results(request, pk, core_position, log_energy, error_estimate):
    print "Results have come in"
    coincidence = AnalyzedCoincidence.objects.get(pk=pk)
    coincidence.core_position_x, coincidence.core_position_y = \
        core_position
    coincidence.log_energy = log_energy
    coincidence.error_estimate = error_estimate
    coincidence.is_analyzed = True
    coincidence.save()


services = { 'hisparc.get_services': get_services,
             'hisparc.get_coincidence': get_coincidence,
             'hisparc.send_results': send_results,
           }
publicgateway = DjangoGateway(services)
