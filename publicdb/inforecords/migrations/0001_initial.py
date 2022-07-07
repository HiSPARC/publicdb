from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=70)),
                ('number', models.IntegerField(unique=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=20, null=True, blank=True)),
                ('first_name', models.CharField(max_length=40)),
                ('prefix_surname', models.CharField(max_length=10, blank=True)),
                ('surname', models.CharField(max_length=40)),
            ],
            options={
                'ordering': ('surname', 'first_name'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street_1', models.CharField(max_length=40)),
                ('street_2', models.CharField(max_length=40, null=True, blank=True)),
                ('postalcode', models.CharField(max_length=12)),
                ('city', models.CharField(max_length=40)),
                ('pobox', models.CharField(max_length=12, null=True, blank=True)),
                ('pobox_postalcode', models.CharField(max_length=12, null=True, blank=True)),
                ('pobox_city', models.CharField(max_length=40, null=True, blank=True)),
                ('phone_work', models.CharField(max_length=20)),
                ('phone_home', models.CharField(max_length=20, null=True, blank=True)),
                ('fax', models.CharField(max_length=20, null=True, blank=True)),
                ('email_work', models.EmailField(max_length=75)),
                ('email_private', models.EmailField(max_length=75, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
            ],
            options={
                'ordering': ['city', 'street_1', 'email_work'],
                'verbose_name': 'Contact Information',
                'verbose_name_plural': 'Contact Information',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=40)),
                ('number', models.IntegerField(unique=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DetectorHisparc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startdate', models.DateField()),
                ('enddate', models.DateField(null=True, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('height', models.FloatField(null=True, blank=True)),
                ('direction', models.FloatField(null=True, blank=True)),
                ('translation_perp', models.FloatField(null=True, blank=True)),
                ('translation_long', models.FloatField(null=True, blank=True)),
                ('scintillator_1_alpha', models.FloatField(null=True, blank=True)),
                ('scintillator_1_beta', models.FloatField(null=True, blank=True)),
                ('scintillator_1_radius', models.FloatField(null=True, blank=True)),
                ('scintillator_1_height', models.FloatField(null=True, blank=True)),
                ('scintillator_2_alpha', models.FloatField(null=True, blank=True)),
                ('scintillator_2_beta', models.FloatField(null=True, blank=True)),
                ('scintillator_2_radius', models.FloatField(null=True, blank=True)),
                ('scintillator_2_height', models.FloatField(null=True, blank=True)),
                ('scintillator_3_alpha', models.FloatField(null=True, blank=True)),
                ('scintillator_3_beta', models.FloatField(null=True, blank=True)),
                ('scintillator_3_radius', models.FloatField(null=True, blank=True)),
                ('scintillator_3_height', models.FloatField(null=True, blank=True)),
                ('scintillator_4_alpha', models.FloatField(null=True, blank=True)),
                ('scintillator_4_beta', models.FloatField(null=True, blank=True)),
                ('scintillator_4_radius', models.FloatField(null=True, blank=True)),
                ('scintillator_4_height', models.FloatField(null=True, blank=True)),
            ],
            options={
                'ordering': ('station__number',),
                'verbose_name_plural': 'Detector HiSPARC',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Electronics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startdate', models.DateField()),
                ('enddate', models.DateField(null=True, blank=True)),
                ('serial', models.IntegerField()),
                ('is_master', models.BooleanField()),
                ('has_gps', models.BooleanField()),
                ('notes', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('batch', 'serial'),
                'verbose_name_plural': 'Electronics',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ElectronicsBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(unique=True)),
                ('notes', models.TextField()),
            ],
            options={
                'ordering': ('type', 'number'),
                'verbose_name_plural': 'Electronics Batch',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ElectronicsStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=40)),
            ],
            options={
                'verbose_name_plural': 'Electronics Status',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ElectronicsType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=40)),
            ],
            options={
                'ordering': ('description',),
                'verbose_name_plural': 'Electronics Type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnabledService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_critical', models.FloatField(null=True, blank=True)),
                ('max_critical', models.FloatField(null=True, blank=True)),
                ('min_warning', models.FloatField(null=True, blank=True)),
                ('max_warning', models.FloatField(null=True, blank=True)),
            ],
            options={
                'ordering': ('pc', 'monitor_service'),
                'verbose_name_plural': 'Enabled Services',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MonitorPulseheightThresholds',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plate', models.IntegerField()),
                ('mpv_mean', models.FloatField()),
                ('mpv_sigma', models.FloatField()),
                ('mpv_max_allowed_drift', models.FloatField()),
                ('mpv_min_allowed_drift', models.FloatField()),
            ],
            options={
                'verbose_name_plural': 'Pulseheight thresholds for Nagios monitoring',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MonitorService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=40)),
                ('nagios_command', models.CharField(max_length=70)),
                ('is_default_service', models.BooleanField(default=False)),
                ('enable_active_checks', models.BooleanField(default=True)),
                ('min_critical', models.FloatField(null=True, blank=True)),
                ('max_critical', models.FloatField(null=True, blank=True)),
                ('min_warning', models.FloatField(null=True, blank=True)),
                ('max_warning', models.FloatField(null=True, blank=True)),
            ],
            options={
                'ordering': ('description',),
                'verbose_name_plural': 'Monitor Services',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=40)),
                ('is_active', models.BooleanField(default=False)),
                ('is_test', models.BooleanField(default=False)),
                ('ip', models.IPAddressField(unique=True, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('services', models.ManyToManyField(to='inforecords.MonitorService', through='inforecords.EnabledService')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'PC and Certificates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PcType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=40)),
                ('slug', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'PC Type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=70)),
                ('number', models.IntegerField(unique=True, blank=True)),
                ('password', models.CharField(max_length=40)),
                ('info_page', models.TextField(blank=True)),
                ('cluster', models.ForeignKey(related_name='stations', to='inforecords.Cluster')),
                ('contact', models.ForeignKey(related_name='stations_contact', to='inforecords.Contact', null=True)),
                ('contactinformation', models.ForeignKey(related_name='stations', to='inforecords.ContactInformation')),
                ('ict_contact', models.ForeignKey(related_name='stations_ict_contact', to='inforecords.Contact', null=True)),
            ],
            options={
                'ordering': ('number',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pc',
            name='station',
            field=models.ForeignKey(to='inforecords.Station'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pc',
            name='type',
            field=models.ForeignKey(to='inforecords.PcType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitorpulseheightthresholds',
            name='station',
            field=models.ForeignKey(to='inforecords.Station'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enabledservice',
            name='monitor_service',
            field=models.ForeignKey(to='inforecords.MonitorService'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enabledservice',
            name='pc',
            field=models.ForeignKey(to='inforecords.Pc'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='electronicsbatch',
            name='type',
            field=models.ForeignKey(to='inforecords.ElectronicsType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='electronics',
            name='batch',
            field=models.ForeignKey(to='inforecords.ElectronicsBatch'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='electronics',
            name='station',
            field=models.ForeignKey(to='inforecords.Station'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='electronics',
            name='status',
            field=models.ForeignKey(to='inforecords.ElectronicsStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='electronics',
            name='type',
            field=models.ForeignKey(to='inforecords.ElectronicsType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='detectorhisparc',
            name='station',
            field=models.ForeignKey(to='inforecords.Station'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='detectorhisparc',
            unique_together={('station', 'startdate')},
        ),
        migrations.AddField(
            model_name='contact',
            name='contactinformation',
            field=models.ForeignKey(related_name='contacts', to='inforecords.ContactInformation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='profession',
            field=models.ForeignKey(to='inforecords.Profession'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together={('first_name', 'prefix_surname', 'surname')},
        ),
        migrations.AddField(
            model_name='cluster',
            name='country',
            field=models.ForeignKey(related_name='clusters', to='inforecords.Country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cluster',
            name='parent',
            field=models.ForeignKey(related_name='subclusters', blank=True, to='inforecords.Cluster', null=True),
            preserve_default=True,
        ),
    ]
