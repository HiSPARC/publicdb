from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0002_remove_detectorhisparc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electronics',
            name='batch',
        ),
        migrations.RemoveField(
            model_name='electronics',
            name='station',
        ),
        migrations.RemoveField(
            model_name='electronics',
            name='status',
        ),
        migrations.RemoveField(
            model_name='electronics',
            name='type',
        ),
        migrations.DeleteModel(
            name='Electronics',
        ),
        migrations.RemoveField(
            model_name='electronicsbatch',
            name='type',
        ),
        migrations.DeleteModel(
            name='ElectronicsBatch',
        ),
        migrations.DeleteModel(
            name='ElectronicsStatus',
        ),
        migrations.DeleteModel(
            name='ElectronicsType',
        ),
    ]
