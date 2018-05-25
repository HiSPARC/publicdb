import django.contrib.postgres.fields

from django.db import migrations, models

from sapphire.utils import pbar


def serialiseddatafield_to_arrayfield(apps, schema_editor):
    """Forwards migrations"""
    model = apps.get_model('histograms', 'NetworkHistogram')
    print('')
    for histogram in pbar(model.objects.all().iterator(), length=model.objects.all().count()):
        histogram.bins = histogram.old_bins
        histogram.values = histogram.old_values
        histogram.save()


def arrayfield_to_serialiseddatafield(apps, schema_editor):
    """Backwards migrations"""
    raise NotImplementedError


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0009_add_singles'),
    ]

    operations = [
        # Move old fields out of the way
        migrations.RenameField(
            model_name='networkhistogram',
            old_name='bins',
            new_name='old_bins',
        ),
        migrations.RenameField(
            model_name='networkhistogram',
            old_name='values',
            new_name='old_values',
        ),
        # Add new fields, with null=True
        migrations.AddField(
            model_name='networkhistogram',
            name='bins',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), null=True, size=None),
        ),
        migrations.AddField(
            model_name='networkhistogram',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), null=True, size=None),
        ),
        # Move data into new fields
        migrations.RunPython(
            serialiseddatafield_to_arrayfield,
            arrayfield_to_serialiseddatafield,
            hints={'model_name': 'NetworkHistogram'}
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='networkhistogram',
            name='old_bins',
        ),
        migrations.RemoveField(
            model_name='networkhistogram',
            name='old_values',
        ),
        # Make new fields non-nullable
        migrations.AlterField(
            model_name='networkhistogram',
            name='bins',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None),
        ),
        migrations.AlterField(
            model_name='networkhistogram',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None),
        ),
    ]
