# Generated by Django 3.2.14 on 2022-07-11 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('station_layout', '0005_related_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationlayoutquarantine',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
