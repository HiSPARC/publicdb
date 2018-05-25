import django.contrib.postgres.fields

from django.db import migrations, models

from sapphire.utils import pbar


def mvns_to_adcsample(values):
    return [int(x / 0.57 / 2.5) if x >= 0 else -1 for x in values]


def mv_to_adc(values):
    return [int(x / 0.57) if x >= 0 else -1 for x in values]


def traces_mv_to_adc(traces):
    return [[int(x / -0.57) for x in trace] for trace in traces]


def serialiseddatafield_to_arrayfield(apps, schema_editor):
    """Forwards migrations"""
    model = apps.get_model('coincidences', 'Event')
    print('')
    for event in pbar(model.objects.all().iterator(), length=model.objects.all().count()):
        event.pulseheights = mv_to_adc(event.old_pulseheights)
        event.integrals = mvns_to_adcsample(event.old_integrals)
        event.traces = traces_mv_to_adc(event.old_traces)
        if not (len(event.traces[0]) == len(event.traces[-1])):
            event.traces = event.traces[:2]
        event.save()


def arrayfield_to_serialiseddatafield(apps, schema_editor):
    """Backwards migrations"""
    raise NotImplementedError


class Migration(migrations.Migration):

    dependencies = [
        ('coincidences', '0001_initial'),
    ]

    operations = [
        # Move old fields out of the way
        migrations.RenameField(
            model_name='event',
            old_name='pulseheights',
            new_name='old_pulseheights',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='integrals',
            new_name='old_integrals',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='traces',
            new_name='old_traces',
        ),
        # Add new fields, with null=True
        migrations.AddField(
            model_name='event',
            name='pulseheights',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=4),
        ),
        migrations.AddField(
            model_name='event',
            name='integrals',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=4),
        ),
        migrations.AddField(
            model_name='event',
            name='traces',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None), null=True, size=4),
        ),
        # Move data into new fields
        migrations.RunPython(
            serialiseddatafield_to_arrayfield,
            arrayfield_to_serialiseddatafield,
            hints={'model_name': 'Event'}
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='event',
            name='old_pulseheights',
        ),
        migrations.RemoveField(
            model_name='event',
            name='old_integrals',
        ),
        migrations.RemoveField(
            model_name='event',
            name='old_traces',
        ),
        # Make new fields non-nullable
        migrations.AlterField(
            model_name='event',
            name='pulseheights',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=4),
        ),
        migrations.AlterField(
            model_name='event',
            name='integrals',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=4),
        ),
        migrations.AlterField(
            model_name='event',
            name='traces',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None), size=4),
        ),
    ]
