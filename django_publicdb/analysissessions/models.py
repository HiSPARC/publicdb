from django.db import models
from django_publicdb.coincidences.models import *

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
