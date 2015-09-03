# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detectorhisparc',
            name='station',
        ),
        migrations.DeleteModel(
            name='DetectorHisparc',
        ),
    ]
