# Generated by Django 1.11.12 on 2018-07-06 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysissessions', '0004_analysissession_session_request'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysissession',
            options={'verbose_name': 'Analysis session', 'verbose_name_plural': 'Analysis sessions'},
        ),
        migrations.AlterModelOptions(
            name='analyzedcoincidence',
            options={'ordering': ['coincidence'], 'verbose_name': 'Analyzed coincidence', 'verbose_name_plural': 'Analyzed coincidences'},
        ),
        migrations.AlterModelOptions(
            name='sessionrequest',
            options={'verbose_name': 'Session request', 'verbose_name_plural': 'Session requests'},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'verbose_name': 'Student', 'verbose_name_plural': 'Students'},
        ),
    ]
