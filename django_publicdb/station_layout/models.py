from django.db import models
from django.core.mail import send_mail

import os
from textwrap import dedent

from ..inforecords.models import Station


class StationLayout(models.Model):
    station = models.ForeignKey(Station)
    active_date = models.DateTimeField()
    detector_1_radius = models.FloatField()
    detector_1_alpha = models.FloatField()
    detector_1_beta = models.FloatField()
    detector_1_height = models.FloatField()
    detector_2_radius = models.FloatField()
    detector_2_alpha = models.FloatField()
    detector_2_beta = models.FloatField()
    detector_2_height = models.FloatField()
    detector_3_radius = models.FloatField(null=True, blank=True)
    detector_3_alpha = models.FloatField(null=True, blank=True)
    detector_3_beta = models.FloatField(null=True, blank=True)
    detector_3_height = models.FloatField(null=True, blank=True)
    detector_4_radius = models.FloatField(null=True, blank=True)
    detector_4_alpha = models.FloatField(null=True, blank=True)
    detector_4_beta = models.FloatField(null=True, blank=True)
    detector_4_height = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = [('station', 'active_date')]


class StationLayoutQuarantine(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    submit_date = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    hash_submit = models.CharField(max_length=32)
    hash_review = models.CharField(max_length=32)

    station = models.ForeignKey(Station)
    active_date = models.DateTimeField()
    detector_1_radius = models.FloatField()
    detector_1_alpha = models.FloatField()
    detector_1_beta = models.FloatField()
    detector_1_height = models.FloatField()
    detector_2_radius = models.FloatField()
    detector_2_alpha = models.FloatField()
    detector_2_beta = models.FloatField()
    detector_2_height = models.FloatField()
    detector_3_radius = models.FloatField(null=True, blank=True)
    detector_3_alpha = models.FloatField(null=True, blank=True)
    detector_3_beta = models.FloatField(null=True, blank=True)
    detector_3_height = models.FloatField(null=True, blank=True)
    detector_4_radius = models.FloatField(null=True, blank=True)
    detector_4_alpha = models.FloatField(null=True, blank=True)
    detector_4_beta = models.FloatField(null=True, blank=True)
    detector_4_height = models.FloatField(null=True, blank=True)

    def generate_hashes(self):
        hashs = os.urandom(16).encode('hex')
        hashr = os.urandom(16).encode('hex')
        if (StationLayoutQuarantine.objects.filter(hash_submit=hashs) or
                StationLayoutQuarantine.objects.filter(hash_review=hashr)):
            self.generate_hashes()
        else:
            self.hash_submit = hashs
            self.hash_review = hashr

    def sendmail_submit(self):
        subject = 'HiSPARC station layout submission'
        message = dedent(
            '''\
            Hello %s,

            Please click on this link to confirm your submission
            of a new layout for station %s.
            http://data.hisparc.nl/layout/confirm/%s/

            Greetings,
            The HiSPARC Team''' %
            (self.name, self.station, self.hash_submit))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)

    def sendmail_review(self):
        subject = 'HiSPARC station layout review'
        message = dedent(
            '''\
            Hello,

            A new station layout has been submitted for station %s.
            Before it is stored in the database we request that you
            review the validity of the submission.
            Use the following link to view and either approve or
            decline the submission:
            http://data.hisparc.nl/layout/review/%s/

            Greetings,
            The HiSPARC Team''' %
            (self.station, self.hash_review))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, ['beheer@hisparc.nl'],
                  fail_silently=False)

    def sendmail_accepted(self):
        subject = 'HiSPARC station layout accepted'
        message = dedent(
            '''\
            Hello %s,

            The station layout which you submitted for station %s
            has been approved by the reviewer.

            Greetings,
            The HiSPARC Team''' %
            (self.name, self.station))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)

    def sendmail_declined(self):
        subject = 'HiSPARC station layout declined'
        message = dedent(
            '''\
            Hello %s,

            The station layout which you submitted for station %s
            has been declined by the reviewer.

            Greetings,
            The HiSPARC Team''' %
            (self.name, self.station))
        sender = 'info@hisparc.nl'
        send_mail(subject, message, sender, [self.email], fail_silently=False)
