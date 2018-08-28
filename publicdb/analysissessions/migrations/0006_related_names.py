# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-20 00:57
from __future__ import unicode_literals

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysissessions', '0005_meta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyzedcoincidence',
            name='coincidence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyzed_coincidences', to='coincidences.Coincidence'),
        ),
        migrations.AlterField(
            model_name='analyzedcoincidence',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyzed_coincidences', to='analysissessions.AnalysisSession'),
        ),
        migrations.AlterField(
            model_name='analyzedcoincidence',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analyzed_coincidences', to='analysissessions.Student'),
        ),
        migrations.AlterField(
            model_name='sessionrequest',
            name='cluster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_requests', to='inforecords.Cluster'),
        ),
        migrations.AlterField(
            model_name='student',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='analysissessions.AnalysisSession'),
        ),
    ]
