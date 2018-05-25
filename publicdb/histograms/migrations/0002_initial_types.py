import os

from django.core import serializers
from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    """Load initial data for histogram and dataset types from the fixture"""
    original_apps = serializers.python.apps
    serializers.python.apps = apps

    fixture_file = os.path.join(os.path.dirname(__file__), '../fixtures/initial_types.json')
    with open(fixture_file) as fixture:
        objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
        for obj in objects:
            obj.save()

    serializers.python.apps = original_apps


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
