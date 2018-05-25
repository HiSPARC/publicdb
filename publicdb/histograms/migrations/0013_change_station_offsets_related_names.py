from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0012_arrayfields_for_dailydataset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationtimingoffset',
            name='ref_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ref_station_offsets', to='histograms.Summary'),
        ),
        migrations.AlterField(
            model_name='stationtimingoffset',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='station_offsets', to='histograms.Summary'),
        ),
    ]
