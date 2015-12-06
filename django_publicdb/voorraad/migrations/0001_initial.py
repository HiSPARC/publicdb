# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inforecords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apparatuur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('naam', models.CharField(max_length=255)),
                ('aantal', models.IntegerField()),
                ('opmerkingen', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Apparatuur',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Artikel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('naam', models.CharField(max_length=255)),
                ('aantal', models.IntegerField()),
                ('artikelnummer', models.CharField(max_length=255)),
                ('datum', models.DateTimeField(auto_now=True)),
                ('opmerkingen', models.TextField(blank=True)),
                ('status', models.CharField(max_length=1, choices=[(b'V', b'V'), (b'?', b'?'), (b'!', b'!')])),
            ],
            options={
                'ordering': ['naam'],
                'verbose_name_plural': 'Artikelen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bestel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aantalbesteld', models.IntegerField()),
                ('datumbesteld', models.DateTimeField(auto_now_add=True)),
                ('offerte', models.FileField(upload_to=b'offerte', blank=True)),
                ('levertijd', models.CharField(max_length=255, blank=True)),
                ('aantalgeleverd', models.IntegerField(default=b'0')),
                ('datumgeleverd', models.DateTimeField(auto_now=True)),
                ('verzendkosten', models.CharField(max_length=255, blank=True)),
                ('voldaan', models.BooleanField()),
                ('opmerkingen', models.TextField(blank=True)),
                ('artikel', models.ForeignKey(to='voorraad.Artikel')),
                ('persoon', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['datumbesteld', 'artikel'],
                'verbose_name_plural': 'Bestellen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gebruikt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aantal', models.IntegerField()),
                ('datum', models.DateTimeField(auto_now_add=True)),
                ('opmerkingen', models.TextField(blank=True)),
                ('artikel', models.ForeignKey(to='voorraad.Artikel')),
                ('cluster', models.ForeignKey(to='inforecords.Cluster')),
                ('persoon', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['datum', 'artikel'],
                'verbose_name_plural': 'Gebruikt',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HisparcII',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serienummer', models.IntegerField()),
                ('is_master', models.BooleanField(default=True)),
                ('stationnummer', models.IntegerField(null=True, blank=True)),
                ('opstelling', models.CharField(max_length=80, null=True, blank=True)),
                ('plaats', models.CharField(max_length=80, null=True, blank=True)),
                ('status', models.CharField(max_length=80, null=True, blank=True)),
                ('opmerkingen', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['serienummer'],
                'verbose_name': 'HiSPARC II',
                'verbose_name_plural': 'HiSPARC II',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Leverancier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('naam', models.CharField(max_length=255)),
                ('adres', models.CharField(max_length=255)),
                ('postcode', models.CharField(max_length=255)),
                ('woonplaats', models.CharField(max_length=255)),
                ('provincie', models.CharField(max_length=255, blank=True)),
                ('land', models.CharField(default=b'Nederland', max_length=255)),
                ('telefoon', models.CharField(max_length=255)),
                ('fax', models.CharField(max_length=255, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('website', models.URLField(blank=True)),
                ('contactpersoon', models.CharField(max_length=255)),
                ('opmerkingen', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['naam'],
                'verbose_name_plural': 'Leveranciers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Opbergplek',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opbergplek', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': ['opbergplek'],
                'verbose_name_plural': 'Opbergplekken',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reservering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aantal', models.IntegerField()),
                ('datum', models.DateTimeField(auto_now_add=True)),
                ('voldaan', models.BooleanField()),
                ('opmerkingen', models.TextField(blank=True)),
                ('artikel', models.ForeignKey(to='voorraad.Artikel')),
                ('cluster', models.ForeignKey(to='inforecords.Cluster')),
            ],
            options={
                'ordering': ['datum', 'artikel'],
                'verbose_name_plural': 'Reserveringen',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='artikel',
            name='leverancier',
            field=models.ForeignKey(to='voorraad.Leverancier'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artikel',
            name='opbergplek',
            field=models.ForeignKey(to='voorraad.Opbergplek'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='apparatuur',
            name='opbergplek',
            field=models.ForeignKey(to='voorraad.Opbergplek'),
            preserve_default=True,
        ),
    ]
