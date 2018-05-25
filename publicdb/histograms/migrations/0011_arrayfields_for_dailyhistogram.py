import django.contrib.postgres.fields
import django.db.models.deletion

from django.db import migrations, models

from sapphire.utils import pbar


def mvns_to_adcsample(values):
    return [int(value / 0.57 / 2.5) for value in values]


def mv_to_adc(values):
    return [int(value / 0.57) for value in values]


def serialiseddatafield_to_arrayfield(apps, schema_editor):
    """Forwards migrations"""
    model = apps.get_model('histograms', 'DailyHistogram')
    multi_model = apps.get_model('histograms', 'MultiDailyHistogram')
    print('')
    for histogram in pbar(model.objects.all().iterator(), length=model.objects.all().count()):
        if not histogram.type.has_multiple_datasets:
            histogram.bins = histogram.old_bins
            histogram.values = histogram.old_values
            histogram.save()
        else:
            if histogram.type.slug == 'pulseheight':
                new_bins = mv_to_adc(histogram.old_bins)
            elif histogram.type.slug == 'pulseintegral':
                new_bins = mvns_to_adcsample(histogram.old_bins)
            else:
                new_bins = histogram.old_bins
            multi_model.objects.create(
                source=histogram.source,
                type=histogram.type,
                bins=new_bins,
                values=histogram.old_values)
            histogram.delete()


def arrayfield_to_serialiseddatafield(apps, schema_editor):
    """Backwards migrations"""
    raise NotImplementedError


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0010_arrayfields_for_networkhistogram'),
    ]

    operations = [
        # Add new model for multi dimensional histograms
        migrations.CreateModel(
            name='MultiDailyHistogram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bins', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None)),
                ('values', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None), size=None)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='histograms.Summary')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='histograms.HistogramType')),
            ],
            options={
                'ordering': ('source', 'type'),
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='multidailyhistogram',
            unique_together=set([('source', 'type')]),
        ),
        # Move old fields out of the way
        migrations.RenameField(
            model_name='dailyhistogram',
            old_name='bins',
            new_name='old_bins',
        ),
        migrations.RenameField(
            model_name='dailyhistogram',
            old_name='values',
            new_name='old_values',
        ),
        # Add new fields, with null=True
        migrations.AddField(
            model_name='dailyhistogram',
            name='bins',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), null=True, size=None),
        ),
        migrations.AddField(
            model_name='dailyhistogram',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), null=True, size=None),
        ),
        # Move data into new fields and to other models
        migrations.RunPython(
            serialiseddatafield_to_arrayfield,
            arrayfield_to_serialiseddatafield
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='dailyhistogram',
            name='old_bins',
        ),
        migrations.RemoveField(
            model_name='dailyhistogram',
            name='old_values',
        ),
        # Make new fields non-nullable
        migrations.AlterField(
            model_name='dailyhistogram',
            name='bins',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None),
        ),
        migrations.AlterField(
            model_name='dailyhistogram',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None),
        ),
    ]
