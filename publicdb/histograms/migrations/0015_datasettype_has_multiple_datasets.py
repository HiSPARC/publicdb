from django.db import migrations, models


def set_datasettype_has_multiple_datasets(apps, schema_editor):
    """Forwards migrations"""
    model = apps.get_model('histograms', 'DatasetType')
    for datasettype in model.objects.filter(slug__in=['singlesratelow', 'singlesratehigh']):
        datasettype.has_multiple_datasets = True
        datasettype.save()


def noop(apps, schema_editor):
    """Backwards migrations"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0014_limit_nested_arrayfield_outer_dimension_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasettype',
            name='has_multiple_datasets',
            field=models.BooleanField(default=False),
        ),
        # Set has_multiple_datasets to True for relevant objects
        migrations.RunPython(
            set_datasettype_has_multiple_datasets,
            noop,
            hints={'model_name': 'DatasetType'}
        ),
    ]
