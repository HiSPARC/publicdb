from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coincidences', '0001_initial'),
        ('inforecords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=40)),
                ('slug', models.SlugField(unique=True)),
                ('hash', models.CharField(max_length=32)),
                ('pin', models.CharField(max_length=4)),
                ('starts', models.DateTimeField()),
                ('ends', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnalyzedCoincidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_analyzed', models.BooleanField(default=False)),
                ('core_position_x', models.FloatField(null=True, blank=True)),
                ('core_position_y', models.FloatField(null=True, blank=True)),
                ('log_energy', models.FloatField(null=True, blank=True)),
                ('theta', models.FloatField(null=True, blank=True)),
                ('phi', models.FloatField(null=True, blank=True)),
                ('error_estimate', models.FloatField(null=True, blank=True)),
                ('coincidence', models.ForeignKey(to='coincidences.Coincidence')),
                ('session', models.ForeignKey(to='analysissessions.AnalysisSession')),
            ],
            options={
                'ordering': ('coincidence',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SessionRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('sur_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=75)),
                ('school', models.CharField(max_length=50)),
                ('events_to_create', models.IntegerField()),
                ('events_created', models.IntegerField()),
                ('start_date', models.DateField()),
                ('mail_send', models.BooleanField(default=False)),
                ('session_confirmed', models.BooleanField(default=False)),
                ('session_created', models.BooleanField(default=False)),
                ('session_pending', models.BooleanField(default=False)),
                ('url', models.CharField(max_length=20)),
                ('sid', models.CharField(max_length=50, null=True, blank=True)),
                ('pin', models.IntegerField(null=True, blank=True)),
                ('cluster', models.ForeignKey(to='inforecords.Cluster')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('session', models.ForeignKey(to='analysissessions.AnalysisSession')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='analyzedcoincidence',
            name='student',
            field=models.ForeignKey(blank=True, to='analysissessions.Student', null=True),
            preserve_default=True,
        ),
    ]
