# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-20 13:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0003_related_names'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adminupdate',
            options={'ordering': ['-version'], 'verbose_name': 'Admin update', 'verbose_name_plural': 'Admin updates'},
        ),
        migrations.AlterModelOptions(
            name='installerupdate',
            options={'ordering': ['-version'], 'verbose_name': 'Installer update', 'verbose_name_plural': 'Installer updates'},
        ),
        migrations.AlterModelOptions(
            name='userupdate',
            options={'ordering': ['-version'], 'verbose_name': 'User update', 'verbose_name_plural': 'User updates'},
        ),
    ]
