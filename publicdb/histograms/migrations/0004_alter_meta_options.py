from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0003_initial_generator_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='configuration',
            options={'get_latest_by': 'timestamp', 'verbose_name_plural': 'configurations'},
        ),
        migrations.AlterModelOptions(
            name='networksummary',
            options={'ordering': ('date',), 'get_latest_by': 'date', 'verbose_name_plural': 'network summaries'},
        ),
        migrations.AlterModelOptions(
            name='summary',
            options={'ordering': ('date', 'station'), 'get_latest_by': 'date', 'verbose_name_plural': 'summaries'},
        ),
    ]
