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
import progressbar as pb

from hisparc.analysis import coincidences

from django_publicdb.coincidences.models import *
from django_publicdb.inforecords.models import *


def save_coincidence(event_list):
    timestamps = []
    events = []

    for station, event, traces in event_list:
        station = int(re.match('station_(\d+)', station._v_name).group(1))
        date_time = datetime.datetime.utcfromtimestamp(event['timestamp'])
        timestamps.append((date_time, event['nanoseconds']))

        pulseheights = [x * .57 if x not in [-999, -1] else x for x in
                        event['pulseheights']]
        integrals = [x * .57 * 2.5 if x not in [-999, -1] else x for x in
                     event['integrals']]

        dt = analyze_traces(traces)

        event = Event(date=date_time.date(), time=date_time.time(),
                      nanoseconds=event['nanoseconds'] - dt,
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

def analyze_traces(traces):
    """Analyze traces and determine time of first particle"""

    t = []
    for trace in traces:
        m = min(trace)
        # No significant pulse (not lower than -20 mV)
        if not m < -20:
            continue
        for i, v in enumerate(trace):
            if v < .2 * m:
                break
        t.append(i * 2.5)
    trace_timing = min(t)
    return trace_timing

if __name__ == '__main__':
    data = tables.openFile('../datastore/2011/5/2011_5_13.h5', 'r')
    stations = data.listNodes('/hisparc/cluster_amsterdam')
    c_list, timestamps = coincidences.search_coincidences(data, stations)

    ndups = 0
    nvalid = 0
    progress = pb.ProgressBar(widgets=[pb.Percentage(), pb.Bar(),
                                       pb.ETA()])
    for coincidence in progress(c_list):
        if len(coincidence) >= 3:
            event_list = coincidences.get_events(data, stations,
                                                 coincidence, timestamps)
            station_list = [x[0] for x in event_list]
            if len(set(station_list)) == len(station_list):
                save_coincidence(event_list)
                nvalid += 1
            else:
                ndups += 1

    if ndups:
        print '%d duplicate stations dropped' % ndups
    print "Succesfully stored %d coincidences" % nvalid
    data.close()
