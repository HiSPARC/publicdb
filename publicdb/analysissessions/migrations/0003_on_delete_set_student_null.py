# Generated by Django 1.10.8 on 2018-02-20 22:51

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysissessions', '0002_increase_emailfield_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyzedcoincidence',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysissessions.Student'),
        ),
    ]
