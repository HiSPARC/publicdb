# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import publicdb.updates.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.PositiveSmallIntegerField()),
                ('update', models.FileField(upload_to=publicdb.updates.models.upload_queue)),
            ],
            options={
                'ordering': ('version',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallerUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=5)),
                ('installer', models.FileField(upload_to=publicdb.updates.models.upload_queue)),
            ],
            options={
                'ordering': ('version',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UpdateQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.PositiveSmallIntegerField()),
                ('update', models.FileField(upload_to=publicdb.updates.models.upload_queue)),
                ('queue', models.ForeignKey(to='updates.UpdateQueue')),
            ],
            options={
                'ordering': ('version',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='userupdate',
            unique_together=set([('queue', 'version')]),
        ),
        migrations.AddField(
            model_name='installerupdate',
            name='queue',
            field=models.ForeignKey(to='updates.UpdateQueue'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='installerupdate',
            unique_together=set([('queue', 'version')]),
        ),
        migrations.AddField(
            model_name='adminupdate',
            name='queue',
            field=models.ForeignKey(to='updates.UpdateQueue'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='adminupdate',
            unique_together=set([('queue', 'version')]),
        ),
    ]
