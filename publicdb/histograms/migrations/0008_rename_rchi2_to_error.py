# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0007_unique_stationtimingoffset'),
    ]

    operations = [
        migrations.RenameField('StationTimingOffset', 'rchi2', 'error'),
    ]
