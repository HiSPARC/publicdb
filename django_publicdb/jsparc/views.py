from django.http import HttpResponse

import calendar
import datetime
import json
from random import randrange

from django_publicdb.coincidences.models import Coincidence


def coin_cors(request):
    """Return a random coincidence for jsparc client test"""

    l = len(Coincidence.objects.all())
    idx = randrange(l)

    c = Coincidence.objects.all()[idx]

    events = []
    for e in c.events.all():
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

    data = dict(timestamp=calendar.timegm(datetime.datetime.combine(c.date, c.time).utctimetuple()),
                nanoseconds=c.nanoseconds, events=events)

    response = HttpResponse(json.dumps(data), mimetype='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
