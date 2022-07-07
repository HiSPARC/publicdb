from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0006_stationtimingoffset'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stationtimingoffset',
            unique_together={('ref_source', 'source')},
        ),
    ]
