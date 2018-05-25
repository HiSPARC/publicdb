import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0013_change_station_offsets_related_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multidailydataset',
            name='y',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None), size=4),
        ),
        migrations.AlterField(
            model_name='multidailyhistogram',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None), size=4),
        ),
    ]
