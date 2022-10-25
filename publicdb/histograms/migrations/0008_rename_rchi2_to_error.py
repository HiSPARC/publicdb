from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0007_unique_stationtimingoffset'),
    ]

    operations = [
        migrations.RenameField('StationTimingOffset', 'rchi2', 'error'),
    ]
