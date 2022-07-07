from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detectorhisparc',
            name='station',
        ),
        migrations.DeleteModel(
            name='DetectorHisparc',
        ),
    ]
