from django.db import models

import os

class StationLayout(models.Model):
    station = models.ForeignKey(Station)
    active_date = models.DateTimeField()
    detector_1_alpha = models.FloatField(null=True, blank=True)
    detector_1_beta = models.FloatField(null=True, blank=True)
    detector_1_radius = models.FloatField(null=True, blank=True)
    detector_1_height = models.FloatField(null=True, blank=True)
    detector_2_alpha = models.FloatField(null=True, blank=True)
    detector_2_beta = models.FloatField(null=True, blank=True)
    detector_2_radius = models.FloatField(null=True, blank=True)
    detector_2_height = models.FloatField(null=True, blank=True)
    detector_3_alpha = models.FloatField(null=True, blank=True)
    detector_3_beta = models.FloatField(null=True, blank=True)
    detector_3_radius = models.FloatField(null=True, blank=True)
    detector_3_height = models.FloatField(null=True, blank=True)
    detector_4_alpha = models.FloatField(null=True, blank=True)
    detector_4_beta = models.FloatField(null=True, blank=True)
    detector_4_radius = models.FloatField(null=True, blank=True)
    detector_4_height = models.FloatField(null=True, blank=True)


class StationLayoutQuarantine(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    submit_date = models.DateTimeField(auto_now_add=True)
    applicant_verified = models.BooleanField(default=False)

    hash_submitter = models.CharField(max_length=32)
    hash_reviewer = models.CharField(max_length=32)

    station = models.ForeignKey(Station)
    active_date = models.DateTimeField()
    detector_1_alpha = models.FloatField(null=True, blank=True)
    detector_1_beta = models.FloatField(null=True, blank=True)
    detector_1_radius = models.FloatField(null=True, blank=True)
    detector_1_height = models.FloatField(null=True, blank=True)
    detector_2_alpha = models.FloatField(null=True, blank=True)
    detector_2_beta = models.FloatField(null=True, blank=True)
    detector_2_radius = models.FloatField(null=True, blank=True)
    detector_2_height = models.FloatField(null=True, blank=True)
    detector_3_alpha = models.FloatField(null=True, blank=True)
    detector_3_beta = models.FloatField(null=True, blank=True)
    detector_3_radius = models.FloatField(null=True, blank=True)
    detector_3_height = models.FloatField(null=True, blank=True)
    detector_4_alpha = models.FloatField(null=True, blank=True)
    detector_4_beta = models.FloatField(null=True, blank=True)
    detector_4_radius = models.FloatField(null=True, blank=True)
    detector_4_height = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.hash_submitter = os.urandom(16).encode('hex')
        self.hash_reviewer = os.urandom(16).encode('hex')
        super(Quarantine, self).save(*args, **kwargs)
