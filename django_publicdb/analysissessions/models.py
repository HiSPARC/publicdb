from django.db import models
from django_publicdb.coincidences.models import *
from django_publicdb.inforecords.models import *
from django.core.mail import send_mail
from random import choice ,randint
import string

import datetime
import hashlib

class AnalysisSession(models.Model):
    title = models.CharField(max_length=40, blank=False, unique=True)
    slug = models.SlugField(unique=True)
    hash = models.CharField(max_length=32)
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
   session_created = models.BooleanField()
   url = models.CharField(max_length=20)
   sid = models.CharField(max_length=50,blank=True,null=True)    
   pin = models.IntegerField(blank=True,null=True)

   def create_session(self):
        self.sid = self.school+str(self.id)
        self.pin = randint(1000,9999)
        #create session her
        self.session_created = True         
        self.save()
        return [self.sid,self.pin]        

   def GenerateUrl():
	url = ''.join([choice(chars) for i in range(20)])
        while SessionRequest.objects.filter(url=url).length>0:
		url = ''.join([choice(chars) for i in range(20)])
        return url

   def SendMail(self):
        subject = 'HiSparc Analysissession request'
        message = 'please follow the following link to create your analysissession: http://127.0.0.1:8000/analysis-session/request/'+self.url
        sender = 'info@hisparc.nl'
        mail = self.email
        send_mail(subject,message,sender,[self.email,],fail_silently=False)
        self.mail_send = True
	self.save()


def GenerateUrl():
    chars=string.letters + string.digits
    url = ''.join([choice(chars) for i in range(20)])
    while SessionRequest.objects.filter(url=url).count()>0:
            url = ''.join([choice(chars) for i in range(20)])
    return url

