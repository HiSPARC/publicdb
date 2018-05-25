from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0006_stationtimingoffset'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stationtimingoffset',
            unique_together=set([('ref_source', 'source')]),
        ),
    ]
