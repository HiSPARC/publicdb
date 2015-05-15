# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    """Load initial data for generator state from the fixture"""

    call_command('loaddata', 'initial_generator_state.json',
                 app_label='histograms')


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
