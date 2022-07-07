from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0005_order_configs_offsets'),
    ]

    operations = [
        migrations.CreateModel(
            name='StationTimingOffset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('offset', models.FloatField(null=True, blank=True)),
                ('rchi2', models.FloatField(null=True, blank=True)),
                ('ref_source', models.ForeignKey(on_delete=models.CASCADE, related_name='ref_source', to='histograms.Summary')),
                ('source', models.ForeignKey(on_delete=models.CASCADE, related_name='source', to='histograms.Summary')),
            ],
            options={
                'ordering': ('ref_source',),
            },
            bases=(models.Model,),
        ),
    ]
