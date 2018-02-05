# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import publicdb.coincidences.models


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coincidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('nanoseconds', models.IntegerField()),
            ],
            options={
                'ordering': ('date', 'time', 'nanoseconds'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('nanoseconds', models.IntegerField()),
                ('pulseheights', publicdb.coincidences.models.SerializedDataField()),
                ('integrals', publicdb.coincidences.models.SerializedDataField()),
                ('traces', publicdb.coincidences.models.SerializedDataField()),
                ('station', models.ForeignKey(to='inforecords.Station')),
            ],
            options={
                'ordering': ('date', 'time', 'nanoseconds', 'station'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coincidence',
            name='events',
            field=models.ManyToManyField(to='coincidences.Event'),
            preserve_default=True,
        ),
    ]
