import os

from datetime import date
from textwrap import dedent

from django.core.mail import send_mail
from django.db import models

from ..histograms.models import Summary
from ..inforecords.models import Station


class StationLayout(models.Model):
    station = models.ForeignKey(Station, models.CASCADE, related_name='layouts')
    active_date = models.DateTimeField()
    detector_1_radius = models.FloatField()
    detector_1_alpha = models.FloatField()
    detector_1_height = models.FloatField()
    detector_1_beta = models.FloatField()
    detector_2_radius = models.FloatField()
    detector_2_alpha = models.FloatField()
    detector_2_height = models.FloatField()
    detector_2_beta = models.FloatField()
    detector_3_radius = models.FloatField(null=True, blank=True)
    detector_3_alpha = models.FloatField(null=True, blank=True)
    detector_3_height = models.FloatField(null=True, blank=True)
    detector_3_beta = models.FloatField(null=True, blank=True)
    detector_4_radius = models.FloatField(null=True, blank=True)
    detector_4_alpha = models.FloatField(null=True, blank=True)
    detector_4_height = models.FloatField(null=True, blank=True)
    detector_4_beta = models.FloatField(null=True, blank=True)

    @property
    def has_four_detectors(self):
        return (self.detector_3_radius is not None and
                self.detector_4_radius is not None)

    class Meta:
        verbose_name = 'Station layout'
        verbose_name_plural = 'Station layouts'
        unique_together = ('station', 'active_date')
        ordering = ['station', 'active_date']
        get_latest_by = 'active_date'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            next_layout = StationLayout.objects.filter(
                station=self.station,
                active_date__gt=self.active_date).earliest()
            next_date = next_layout.active_date
        except StationLayout.DoesNotExist:
            next_date = date.today()
        if self.has_four_detectors:
            # Only for 4 detector stations
            summaries = Summary.objects.filter(station=self.station,
                                               date__gte=self.active_date,
                                               date__lt=next_date)
            for summary in summaries:
                if summary.num_events:
                    summary.needs_update_events = True
                    summary.save()


class StationLayoutQuarantine(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    submit_date = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    hash_submit = models.CharField(max_length=32)
    hash_review = models.CharField(max_length=32)

    station = models.ForeignKey(Station, models.CASCADE, related_name='quarantined_layouts')
    active_date = models.DateTimeField()
    detector_1_radius = models.FloatField()
    detector_1_alpha = models.FloatField()
    detector_1_height = models.FloatField()
    detector_1_beta = models.FloatField()
    detector_2_radius = models.FloatField()
    detector_2_alpha = models.FloatField()
    detector_2_height = models.FloatField()
    detector_2_beta = models.FloatField()
    detector_3_radius = models.FloatField(null=True, blank=True)
    detector_3_alpha = models.FloatField(null=True, blank=True)
    detector_3_height = models.FloatField(null=True, blank=True)
    detector_3_beta = models.FloatField(null=True, blank=True)
    detector_4_radius = models.FloatField(null=True, blank=True)
    detector_4_alpha = models.FloatField(null=True, blank=True)
    detector_4_height = models.FloatField(null=True, blank=True)
    detector_4_beta = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'Station layout quarantine'
        verbose_name_plural = 'Station layouts quarantine'

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
            f'''\
            Hello {self.name},

            Please click on this link to confirm your submission
            of a new layout for station {self.station}.
            https://data.hisparc.nl/layout/confirm/{self.hash_submit}/

            Greetings,
            The HiSPARC Team'''
        )
        sender = 'Beheer HiSPARC <bhrhispa@nikhef.nl>'
        send_mail(subject, message, sender, [self.email], fail_silently=False)

    def sendmail_review(self):
        subject = 'HiSPARC station layout review'
        message = dedent(
            f'''\
            Hello,

            A new station layout has been submitted for station {self.station}.
            Before it is stored in the database we request that you
            review the validity of the submission.
            Use the following link to view and either approve or
            decline the submission:
            https://data.hisparc.nl/layout/review/{self.hash_review}/

            Greetings,
            The HiSPARC Team'''
        )
        sender = 'Beheer HiSPARC <bhrhispa@nikhef.nl>'
        send_mail(subject, message, sender, ['beheer@hisparc.nl'],
                  fail_silently=False)

    def sendmail_accepted(self):
        subject = 'HiSPARC station layout accepted'
        message = dedent(
            f'''\
            Hello {self.name},

            The station layout which you submitted for station {self.station}
            has been approved by the reviewer.

            Greetings,
            The HiSPARC Team'''
        )
        sender = 'Beheer HiSPARC <bhrhispa@nikhef.nl>'
        send_mail(subject, message, sender, [self.email], fail_silently=False)

    def sendmail_declined(self):
        subject = 'HiSPARC station layout declined'
        message = dedent(
            f'''\
            Hello {self.name},

            The station layout which you submitted for station {self.station}
            has been declined by the reviewer.

            Greetings,
            The HiSPARC Team'''
        )
        sender = 'Beheer HiSPARC <bhrhispa@nikhef.nl>'
        send_mail(subject, message, sender, [self.email], fail_silently=False)
