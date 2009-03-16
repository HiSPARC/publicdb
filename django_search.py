#!/usr/bin/env python
from django_app.coincidences.models import Coincidence, Event
from django_app.coincidences.find_coincidences import get_hourly_coincidences


def add_events(all_events, coincidences):
    for eventID, details in all_events.iteritems():
        e = Event(event_id = eventID, date = details['date'], time = details['time'], \
                  nanoseconds = details['nanoseconds'], timestamp = details['timestamp'], \
                  detector = details['detector'], latitude = details['latitude'], \
                  longitude = details['longitude'], height = details['height'], \
                  pulseheight1 = details['PH1'], pulseheight2 = details['PH2'], \
                  pulseheight3 = details['PH3'], pulseheight4 = details['PH4'], \
                  integral1 = details['IN1'], integral2 = details['IN2'], \
                  integral3 = details['IN3'], integral4 = details['IN4'])
        e.save()

    # add coincidences to pique
    for coincidence in coincidences:
        c = Coincidence(date = date)
        c.save()
    
        for eventID in coincidence:
            if c.nevents == 0:
                e = Event.objects.get(pk=eventID)
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
                e = Event.objects.get(pk=eventID)
                e.trace1 = (all_events[eventID])['TR1']
                e.trace2 = (all_events[eventID])['TR2']
                e.trace3 = (all_events[eventID])['TR3']
                e.trace4 = (all_events[eventID])['TR4']
                e.save()
            
                c.events.add( e )
                c.nevents += 1
            
        c.save()


if __name__ == "__main__":
    cluster = [501, 502, 503, 504, 505]
    dates = ['2009-03-03','2009-03-04','2009-03-05','2009-03-06','2009-03-07','2009-03-08','2009-03-09',]
    hours = range(24)
    
    for date in dates:
        for hour in hours:
            print 'Collecting', date, hour
            # remove coincidences that are already in the db from $hour
            # TODO implement

            # get coincidences and events from peene
            all_events, coincidences = get_hourly_coincidences(cluster, date, hour)
            #     coincidences = get_coincidences_per_day(cluster, date)

            # add events to pique
            add_events(all_events, coincidences)
