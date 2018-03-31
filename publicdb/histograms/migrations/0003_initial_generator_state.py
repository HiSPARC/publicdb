# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core import serializers
from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    """Load initial data for generator state from the fixture"""
    original_apps = serializers.python.apps
    serializers.python.apps = apps

    fixture_file = os.path.join(os.path.dirname(__file__), '../fixtures/initial_generator_state.json')
    with open(fixture_file) as fixture:
        objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
        for obj in objects:
            obj.save()

    serializers.python.apps = original_apps


def unload_fixture(apps, schema_editor):
    """Delete all entries from the geenrator state"""

    GeneratorState = apps.get_model('histograms', 'GeneratorState')
    GeneratorState.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0002_initial_types'),
    ]

    operations = [
        migrations.RunPython(load_fixture)  # reverse_code=unload_fixture
    ]
