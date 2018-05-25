import django.contrib.postgres.fields
import django.db.models.deletion

from django.db import migrations, models

from sapphire.utils import pbar


def serialiseddatafield_to_arrayfield(apps, schema_editor):
    """Forwards migrations"""
    model = apps.get_model('histograms', 'DailyDataset')
    multi_model = apps.get_model('histograms', 'MultiDailyDataset')
    print('')
    for dataset in pbar(model.objects.all().iterator(), length=model.objects.all().count()):
        if dataset.type.slug in ['barometer', 'temperature']:
            dataset.x = dataset.old_x
            dataset.y = dataset.old_y
            dataset.save()
        else:
            multi_model.objects.create(
                source=dataset.source,
                type=dataset.type,
                x=dataset.old_x,
                y=dataset.old_y)
            dataset.delete()


def arrayfield_to_serialiseddatafield(apps, schema_editor):
    """Backwards migrations"""
    raise NotImplementedError


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0011_arrayfields_for_dailyhistogram'),
    ]

    operations = [
        # Add new model for multi dimensional datasets
        migrations.CreateModel(
            name='MultiDailyDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None)),
                ('y', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=None)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='histograms.Summary')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='histograms.DatasetType')),
            ],
            options={
                'ordering': ('source', 'type'),
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='multidailydataset',
            unique_together=set([('source', 'type')]),
        ),
        # Move old fields out of the way
        migrations.RenameField(
            model_name='dailydataset',
            old_name='x',
            new_name='old_x',
        ),
        migrations.RenameField(
            model_name='dailydataset',
            old_name='y',
            new_name='old_y',
        ),
        # Add new fields, with null=True
        migrations.AddField(
            model_name='dailydataset',
            name='x',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), null=True, size=None),
        ),
        migrations.AddField(
            model_name='dailydataset',
            name='y',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), null=True, size=None),
        ),
        # Move data into new fields and to other models
        migrations.RunPython(
            serialiseddatafield_to_arrayfield,
            arrayfield_to_serialiseddatafield
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='dailydataset',
            name='old_x',
        ),
        migrations.RemoveField(
            model_name='dailydataset',
            name='old_y',
        ),
        # Make new fields non-nullable
        migrations.AlterField(
            model_name='dailydataset',
            name='x',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None),
        ),
        migrations.AlterField(
            model_name='dailydataset',
            name='y',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None),
        ),
    ]
