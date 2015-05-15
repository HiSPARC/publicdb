# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    """Load initial data for histogram and dataset types from the fixture"""

    call_command('loaddata', 'initial_types.json', app_label='histograms')


def unload_fixture(apps, schema_editor):
    """Delete all entries from the histogram/dataset types

    This will also delete all related histograms/datasets!

    """
    HistogramType = apps.get_model('histograms', 'HistogramType')
    HistogramType.objects.all().delete()
    DatasetType = apps.get_model('histograms', 'DatasetType')
    DatasetType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture)  # reverse_code=unload_fixture
    ]
