# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0006_stationtimingoffset'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stationtimingoffset',
            unique_together=set([('ref_source', 'source')]),
        ),
    ]
