#!/usr/bin/env python
import sys
import os
from time import localtime

sys.path.append('/user/admhispa/http/pique')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

from django_publicdb.coincidences.models import Coincidence, Event
from django_publicdb.coincidences.find_coincidences import get_hourly_coincidences
from django_publicdb.inforecords.models import Cluster, Station

def add_events(all_events, coincidences):
    """
    Add all events from the dictionary to the database
    Also add the coincidences
    """
#     for eventID, details in all_events.iteritems():
#         add_single_event(eventID, details)

    # add coincidences to pique
    for coincidence in coincidences:
        c = Coincidence(date = date)
        c.save()
    
        for eventID in coincidence:
            if c.nevents == 0:
                e = add_single_event(eventID, all_events[eventID])
#                 e = Event.objects.get(pk=eventID)
                e.trace1 = (all_events[eventID])['TR1']
                e.trace2 = (all_events[eventID])['TR2']
                e.trace3 = (all_events[eventID])['TR3']
                e.trace4 = (all_events[eventID])['TR4']
                e.save()
            
                c.time = e.time
                c.nanoseconds = e.nanoseconds
                c.events.add( e )
                c.nevents += 1
            elif eventID == 'DOUBLE':
                c.nodouble = False
            elif eventID == 'TOOLATE':
                c.intime = False
            else:
                e = add_single_event(eventID, all_events[eventID])
#                 e = Event.objects.get(pk=eventID)
                e.trace1 = (all_events[eventID])['TR1']
                e.trace2 = (all_events[eventID])['TR2']
                e.trace3 = (all_events[eventID])['TR3']
                e.trace4 = (all_events[eventID])['TR4']
                e.save()
            
                c.events.add( e )
                c.nevents += 1
            
        c.save()


def add_single_event(eventID, details):
    """
    Add a single event to the database
    """
    e = Event(event_id = eventID, date = details['date'], time = details['time'], \
              nanoseconds = details['nanoseconds'], timestamp = details['timestamp'], \
              detector = details['detector'], latitude = details['latitude'], \
              longitude = details['longitude'], height = details['height'], \
              pulseheight1 = details['PH1'], pulseheight2 = details['PH2'], \
              pulseheight3 = details['PH3'], pulseheight4 = details['PH4'], \
              integral1 = details['IN1'], integral2 = details['IN2'], \
              integral3 = details['IN3'], integral4 = details['IN4'])
    e.save()

    return e


if __name__ == "__main__":
    if len(sys.argv) == 4:
        cluster_id = int(sys.argv[1])
        date = str(sys.argv[2])
        hour = int(sys.argv[3])
        
        cluster = [501, 502, 504, 505]
        #cluster = []
        #for station in Station.objects.filter(location__cluster__id = cluster_id):
            #cluster.append(int(station.number))
        clusters = [cluster]
    else:
        date = str(localtime()[0]) + '-' + str(localtime()[1]) + '-' + str(localtime()[2])
        hour = int(localtime()[3])
    
        # get clutsers
        clusters = []
        for cluster_obj in Cluster.objects.all():
            cluster = []
            for station in Station.objects.filter(location__cluster = cluster_obj):
                cluster.append(int(station.number))
            clusters.append(cluster)
    
    # remove coincidences that are already in the db from $hour
    # TODO implement

    
    # get coincidences and events from peene
    for cluster in clusters:
        print 'Collecting', date, hour, 'of clutser', cluster
        if len(cluster) < 3:
            print 'cluster too small, skipping'
        else:
            all_events, coincidences = get_hourly_coincidences(cluster, date, hour)
            print len(coincidences), 'coincidences found in cluster', cluster
    
    # add events to pique
    add_events(all_events, coincidences)

    