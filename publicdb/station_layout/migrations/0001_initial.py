from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StationLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active_date', models.DateTimeField()),
                ('detector_1_radius', models.FloatField()),
                ('detector_1_alpha', models.FloatField()),
                ('detector_1_beta', models.FloatField()),
                ('detector_1_height', models.FloatField()),
                ('detector_2_radius', models.FloatField()),
                ('detector_2_alpha', models.FloatField()),
                ('detector_2_beta', models.FloatField()),
                ('detector_2_height', models.FloatField()),
                ('detector_3_radius', models.FloatField(null=True, blank=True)),
                ('detector_3_alpha', models.FloatField(null=True, blank=True)),
                ('detector_3_beta', models.FloatField(null=True, blank=True)),
                ('detector_3_height', models.FloatField(null=True, blank=True)),
                ('detector_4_radius', models.FloatField(null=True, blank=True)),
                ('detector_4_alpha', models.FloatField(null=True, blank=True)),
                ('detector_4_beta', models.FloatField(null=True, blank=True)),
                ('detector_4_height', models.FloatField(null=True, blank=True)),
                ('station', models.ForeignKey(to='inforecords.Station')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StationLayoutQuarantine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=75)),
                ('submit_date', models.DateTimeField(auto_now_add=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('reviewed', models.BooleanField(default=False)),
                ('hash_submit', models.CharField(max_length=32)),
                ('hash_review', models.CharField(max_length=32)),
                ('active_date', models.DateTimeField()),
                ('detector_1_radius', models.FloatField()),
                ('detector_1_alpha', models.FloatField()),
                ('detector_1_beta', models.FloatField()),
                ('detector_1_height', models.FloatField()),
                ('detector_2_radius', models.FloatField()),
                ('detector_2_alpha', models.FloatField()),
                ('detector_2_beta', models.FloatField()),
                ('detector_2_height', models.FloatField()),
                ('detector_3_radius', models.FloatField(null=True, blank=True)),
                ('detector_3_alpha', models.FloatField(null=True, blank=True)),
                ('detector_3_beta', models.FloatField(null=True, blank=True)),
                ('detector_3_height', models.FloatField(null=True, blank=True)),
                ('detector_4_radius', models.FloatField(null=True, blank=True)),
                ('detector_4_alpha', models.FloatField(null=True, blank=True)),
                ('detector_4_beta', models.FloatField(null=True, blank=True)),
                ('detector_4_height', models.FloatField(null=True, blank=True)),
                ('station', models.ForeignKey(to='inforecords.Station')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='stationlayout',
            unique_together=set([('station', 'active_date')]),
        ),
    ]
