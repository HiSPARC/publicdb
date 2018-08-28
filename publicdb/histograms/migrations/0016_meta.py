# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-06 11:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0015_datasettype_has_multiple_datasets'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='configuration',
            options={'get_latest_by': 'timestamp', 'ordering': ['source'], 'verbose_name': 'Configuration', 'verbose_name_plural': 'Configurations'},
        ),
        migrations.AlterModelOptions(
            name='dailydataset',
            options={'ordering': ['source', 'type']},
        ),
        migrations.AlterModelOptions(
            name='dailyhistogram',
            options={'ordering': ['source', 'type']},
        ),
        migrations.AlterModelOptions(
            name='datasettype',
            options={'verbose_name': 'Dataset type', 'verbose_name_plural': 'Dataset types'},
        ),
        migrations.AlterModelOptions(
            name='detectortimingoffset',
            options={'ordering': ['source'], 'verbose_name': 'Detector timing offset', 'verbose_name_plural': 'Detector timing offsets'},
        ),
        migrations.AlterModelOptions(
            name='histogramtype',
            options={'verbose_name': 'Histogram type', 'verbose_name_plural': 'Histogram types'},
        ),
        migrations.AlterModelOptions(
            name='multidailydataset',
            options={'ordering': ['source', 'type']},
        ),
        migrations.AlterModelOptions(
            name='multidailyhistogram',
            options={'ordering': ['source', 'type']},
        ),
        migrations.AlterModelOptions(
            name='networkhistogram',
            options={'ordering': ['source', 'type'], 'verbose_name': 'Network histogram', 'verbose_name_plural': 'Network histograms'},
        ),
        migrations.AlterModelOptions(
            name='networksummary',
            options={'get_latest_by': 'date', 'ordering': ['date'], 'verbose_name': 'Network summary', 'verbose_name_plural': 'Network summaries'},
        ),
        migrations.AlterModelOptions(
            name='pulseheightfit',
            options={'ordering': ['source', 'plate'], 'verbose_name': 'Pulseheight fit', 'verbose_name_plural': 'Pulseheight fits'},
        ),
        migrations.AlterModelOptions(
            name='stationtimingoffset',
            options={'ordering': ['ref_source'], 'verbose_name': 'Station timing offset', 'verbose_name_plural': 'Station timing offsets'},
        ),
        migrations.AlterModelOptions(
            name='summary',
            options={'get_latest_by': 'date', 'ordering': ['date', 'station'], 'verbose_name': 'Summary', 'verbose_name_plural': 'Summaries'},
        ),
    ]
