# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0003_remove_electronics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactinformation',
            name='email_private',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinformation',
            name='email_work',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='pc',
            name='ip',
            field=models.GenericIPAddressField(unique=True, null=True, protocol=b'IPV4', blank=True),
        ),
    ]
