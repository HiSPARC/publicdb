from django.db import models
from django_publicdb.coincidences.models import *
from django_publicdb.inforecords.models import *
from django.core.mail import send_mail
from hisparc.analysis import coincidences
from hisparc import publicdb
from random import choice ,randint

import string
import datetime
import hashlib
import tables
import datetime
import sys
import os
import re

class AnalysisSession(models.Model):
    title = models.CharField(max_length=40, blank=False, unique=True)
    slug = models.SlugField(unique=True)
    hash = models.CharField(max_length=32)
    pin = models.CharField(max_length=4)
    starts = models.DateTimeField()
    ends = models.DateTimeField()

    def in_progress(self):
        return self.starts <= datetime.datetime.now() < self.ends
    in_progress.boolean = True

    def save(self, *args, **kwargs):
        self.hash = hashlib.md5(self.slug).hexdigest()
        super(AnalysisSession, self).save(*args, **kwargs)
        Student(session=self, name='Test student').save()

    def __unicode__(self):
        return self.title

class AnalyzedCoincidence(models.Model):
    session = models.ForeignKey(AnalysisSession)
    coincidence = models.ForeignKey(Coincidence)
    student = models.ForeignKey('Student', null=True, blank=True)
    is_analyzed = models.BooleanField(default=False)
    core_position_x = models.FloatField(null=True, blank=True)
    core_position_y = models.FloatField(null=True, blank=True)
    log_energy = models.FloatField(null=True, blank=True)
    theta = models.FloatField(null=True, blank=True)
    phi = models.FloatField(null=True, blank=True)
    error_estimate = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.coincidence, self.student)

    class Meta:
        ordering = ('coincidence',)

class Student(models.Model):
    session = models.ForeignKey(AnalysisSession)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return '%s - %s' % (self.session, self.name)

class SessionRequest(models.Model):
   first_name = models.CharField(max_length=50)
   sur_name = models.CharField(max_length=50)
   email = models.EmailField()
   school = models.CharField(max_length=50)
   cluster = models.ForeignKey('inforecords.Cluster')
   start_date = models.DateField()
   mail_send = models.BooleanField()
   session_confirmed = models.BooleanField()
   session_created = models.BooleanField()
   url = models.CharField(max_length=20)
   sid = models.CharField(max_length=50,blank=True,null=True)    
   pin = models.IntegerField(blank=True,null=True)

   def create_session(self):
#        self.sid = self.school+str(self.id)
#        self.pin = randint(1000,9999)
        starts=datetime.datetime.now()
        ends=datetime.datetime.now()
        session = AnalysisSession(starts = starts,
                                  ends = ends,
                                  pin = str(self.pin),
                                  slug = self.url,
                                  title = self.sid
                                 )
        session.save()
#        create_session.create_session(100,self.cluster,self.start_date,session)
        eventsdone = 0
        date=self.start_date
        while((eventsdone<100) and (date<datetime.date.today())):
            eventsdone += self.find_coincidence(date,session)
            date = date + datetime.timedelta(days=1)
        self.session_created = True         
        self.save()
        return [self.sid,self.pin]        

   def find_coincidence(self,date,session):
        file = str(date.year)+'_'+str(date.month)+'_'+str(date.day)+'.h5'
        datastore_path = os.path.join(settings.DATASTORE_PATH,str(date.year),str(date.month),file)
        data = tables.openFile(datastore_path, 'r')
        stations = data.listNodes('/hisparc/cluster_'+self.cluster.name)
        c_list, timestamps = coincidences.search_coincidences(data, stations)
        ndups = 0
        nvalid = 0
        for coincidence in c_list:
            if len(coincidence) >= 3:
                event_list = coincidences.get_events(data, stations,
                                                     coincidence, timestamps)
                station_list = [x[0] for x in event_list]
                if len(set(station_list)) == len(station_list):
                    self.save_coincidence(event_list,session)
                    nvalid += 1
                else:
                    ndups += 1

        if ndups:
            print '%d duplicate stations dropped' % ndups
        print "Succesfully stored %d coincidences" % nvalid
        data.close()
        return nvalid

   def save_coincidence(self,event_list,session):
        timestamps = []
        events = []

        for station, event, traces in event_list:
           station = int(re.match('station_(\d+)', station._v_name).group(1))
           date_time = datetime.datetime.utcfromtimestamp(event['timestamp'])
           timestamps.append((date_time, event['nanoseconds']))

           pulseheights = [x * .57 if x != -999 else -999 for x in
                        event['pulseheights']]
           integrals = [x * .57 if x != -999 else -999 for x in
                     event['integrals']]

           dt = self.analyze_traces(traces)
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
        analyzed_coincidence = AnalyzedCoincidence(session=session,coincidence=coincidence)
        analyzed_coincidence.save()

   def analyze_traces(self,traces):
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

   def GenerateUrl(self):
        chars=string.letters + string.digits
	newurl = ''.join([choice(chars) for i in range(20)])
        if SessionRequest.objects.filter(url=newurl):
		newurl = ''.join([choice(chars) for i in range(20)])
        self.url=newurl

   def SendMail(self):
        subject = 'HiSparc Analysissession request'
        message = 'please follow the following link to create your analysissession: http://127.0.0.1:8000/analysis-session/request/'+self.url
        sender = 'info@hisparc.nl'
        mail = self.email
        send_mail(subject,message,sender,[self.email,],fail_silently=False)
        self.mail_send = True
	self.save()


