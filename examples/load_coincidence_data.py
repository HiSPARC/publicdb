""" Load coincidences into the public database for analysis

    This script searches for coincidences in a HiSPARC data file and loads
    triple and higher coincidences into the public database for analysis.

    NOTE: at the moment this script is hardly configurable.  But it's a
    start.

"""
import os
import sys

sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import tables
import datetime
import re

from hisparc.analysis import coincidences

from django_publicdb.coincidences.models import *
from django_publicdb.inforecords.models import *


def save_coincidence(event_list):
    timestamps = []
    events = []

    for station, event, traces in event_list:
        station = int(re.match('s(\d+)', station._v_name).group(1))
        date_time = datetime.datetime.utcfromtimestamp(event['timestamp'])
        timestamps.append((date_time, event['nanoseconds']))

        pulseheights = [x * .57 if x != -999 else -999 for x in
                        event['pulseheights']]
        integrals = [x * .57 if x != -999 else -999 for x in
                     event['integrals']]

        event = Event(date=date_time.date(), time=date_time.time(),
                      nanoseconds=event['nanoseconds'],
                      station=Station.objects.get(number=station),
                      pulseheights=pulseheights, integrals=integrals,
                      traces=traces)
        event.save()
        events.append(event)

    first_timestamp = sorted(timestamps)[0]
    coincidence = Coincidence(date=first_timestamp[0].date(),
                              time=first_timestamp[0].time(),
                              nanoseconds=first_timestamp[1])
    coincidence.save()
    coincidence.events.add(*events)


if __name__ == '__main__':
    data = tables.openFile('/home/david/work/HiSPARC/data/100412/data.h5', 'r')
    stations = data.listNodes('/')
    c_list, timestamps = coincidences.search_coincidences(data, stations)

    for coincidence in c_list:
        if len(coincidence) >= 3:
            event_list = coincidences.get_events(data, stations,
                                                 coincidence, timestamps)
            station_list = [x[0] for x in event_list]
            if len(set(station_list)) == len(station_list):
                save_coincidence(event_list)
            else:
                print 'Duplicate stations; dropped.'
    data.close()
