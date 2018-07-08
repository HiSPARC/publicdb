import datetime
import hashlib
import os
import re
import textwrap

import tables

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.defaultfilters import slugify

from sapphire import CoincidenceQuery

from ..api.datastore import ext_timestamp_to_datetime, get_event_traces
from ..coincidences.models import Coincidence, Event
from ..histograms.esd import get_esd_data_path
from ..inforecords.models import Station


class AnalysisSession(models.Model):
    session_request = models.OneToOneField('SessionRequest', models.CASCADE)
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

    class Meta:
        verbose_name = 'Analysis session'
        verbose_name_plural = 'Analysis sessions'


class Student(models.Model):
    session = models.ForeignKey(AnalysisSession, models.CASCADE)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return '%s - %s' % (self.session, self.name)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


class AnalyzedCoincidence(models.Model):
    session = models.ForeignKey(AnalysisSession, models.CASCADE)
    coincidence = models.ForeignKey(Coincidence, models.CASCADE)
    student = models.ForeignKey(Student, models.SET_NULL, null=True, blank=True)
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
        verbose_name = 'Analyzed coincidence'
        verbose_name_plural = 'Analyzed coincidences'
        ordering = ['coincidence']


class SessionRequest(models.Model):
    first_name = models.CharField(max_length=50)
    sur_name = models.CharField(max_length=50)
    email = models.EmailField()
    school = models.CharField(max_length=50)
    cluster = models.ForeignKey('inforecords.Cluster', models.CASCADE)
    events_to_create = models.IntegerField()
    events_created = models.IntegerField()
    start_date = models.DateField()
    mail_send = models.BooleanField(default=False)
    session_confirmed = models.BooleanField(default=False)
    session_pending = models.BooleanField(default=False)
    session_created = models.BooleanField(default=False)
    url = models.CharField(max_length=20)
    sid = models.CharField(max_length=50, blank=True, null=True)
    pin = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Session request'
        verbose_name_plural = 'Session requests'

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.sur_name)

    def create_session(self):
        self.session_pending = False
        self.save()
        starts = datetime.datetime.now()
        session_length = datetime.timedelta(weeks=4)
        ends = starts + session_length
        session = AnalysisSession(
            session_request=self,
            starts=starts,
            ends=ends,
            pin=str(self.pin),
            slug=slugify(self.sid),
            title=self.sid)
        session.save()
        date = self.start_date
        search_length = datetime.timedelta(weeks=3)
        enddate = min([self.start_date + search_length, datetime.date.today()])
        while (self.events_created < self.events_to_create and date < enddate):
            self.events_created += self.find_coincidence(date, session)
            date += datetime.timedelta(days=1)
        if self.events_created <= 0:
            self.sendmail_zero()
        elif self.events_created <= self.events_to_create:
            self.sendmail_created_less()
            self.session_created = True
        else:
            self.sendmail_created()
            self.session_created = True
        self.save()

    def find_coincidence(self, date, session):
        """Find coincidences for the given cluster on the given date

        Store the found coincidences and events in the database.
        Then return the number of found coincidences.

        """
        stations = Station.objects.filter(cluster=self.cluster, pc__is_test=False).distinct().values_list('number')
        path = get_esd_data_path(date)

        if not os.path.isfile(path):
            # No data file, so no coincidences
            return 0

        number_of_coincidences = 0

        # Get all coincidences containing stations in the requested cluster
        with tables.open_file(path, 'r') as data:
            cq = CoincidenceQuery(data)
            coincidences = cq.any(stations)
            events = cq.events_from_stations(coincidences, stations, n=3)
            # Todo: Double check for multiple events from same station,
            self.save_coincidence(events, session)
            number_of_coincidences += 1

        return number_of_coincidences

    def save_coincidence(self, events, session):
        event_timestamps = []
        event_objects = []

        for station_number, event in events:
            station = Station.objects.get(number=station_number)
            traces = get_event_traces(station, event['ext_timestamp'])

            trace_start_ext_timestamp = int(event['ext_timestamp']) - event['t_trigger']
            trace_start_nanoseconds = int(trace_start_ext_timestamp % int(1e9))
            event_datetime = ext_timestamp_to_datetime(trace_start_ext_timestamp)
            event_timestamps.append((event_datetime, trace_start_nanoseconds))

            event = Event(date=event_datetime.date(),
                          time=event_datetime.time(),
                          nanoseconds=trace_start_nanoseconds,
                          station=station,
                          pulseheights=event['pulseheights'].tolist(),
                          integrals=event['integrals'].tolist(),
                          traces=traces)

        first_timestamp = min(event_timestamps)
        coincidence = Coincidence(date=first_timestamp[0].date(),
                                  time=first_timestamp[0].time(),
                                  nanoseconds=first_timestamp[1])
        coincidence.save()

        for event in event_objects:
            event.coincidence = coincidence
            event.save()

        analyzed_coincidence = AnalyzedCoincidence(session=session, coincidence=coincidence)
        analyzed_coincidence.save()

    def generate_url(self):
        newurl = os.urandom(10).encode('hex')
        if SessionRequest.objects.filter(url=newurl).exists():
            self.generate_url()
        else:
            self.url = newurl

    def sendmail_request(self):
        subject = 'HiSPARC analysis session request'
        message = textwrap.dedent(
            '''\
            Hello %s,

            Please click on this link to confirm your request for an analysis session with jSparc:
            http://data.hisparc.nl/analysis-session/request/%s/

            Greetings,
            The HiSPARC Team''' %
            (self.name, self.url))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)
        self.mail_send = True
        self.save()

    def sendmail_created(self):
        subject = 'HiSPARC analysis session created'
        message = textwrap.dedent(
            '''\
            Hello %s,

            Your analysis session for jSparc has been created.
            Title = %s
            Pin = %d
            Events created = %d

            Go here to start analysing events:
            http://data.hisparc.nl/media/jsparc/jsparc.html

            During the session you can view the results at:
            http://data.hisparc.nl/analysis-session/%s/data/

            Greetings,
            The HiSPARC Team''' %
            (self.name, self.sid, self.pin, self.events_created, slugify(self.sid)))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)

    def sendmail_created_less(self):
        subject = 'HiSPARC analysis session created with less events'
        message = textwrap.dedent(
            '''\
            Hello %s,'

            Your analysis session for jSparc has been created.
            Title = %s
            Pin = %d

            However, we were unable to find the amount of events you requested.
            Events created = %d

            Go here to start analysing events:
            http://data.hisparc.nl/media/jsparc/jsparc.html

            During the session you can view the results at:
            http://data.hisparc.nl/analysis-session/%s/data/

            Greetings,
            The HiSPARC Team''' %
            (self.name, self.sid, self.pin, self.events_created, slugify(self.sid)))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)

    def sendmail_zero(self):
        subject = 'HiSPARC analysis session creation failed'
        message = textwrap.dedent(
            '''\
            Hello %s,

            Your analysis session for jSparc could not be created.
            Perhaps there was no data for the date and/or stations you selected.
            Please try selecting a different cluster or date.

            Greetings,
            The HiSPARC Team''' %
            self.name)
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)
