from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0004_alter_meta_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='configuration',
            options={'ordering': ('source',), 'get_latest_by': 'timestamp', 'verbose_name_plural': 'configurations'},
        ),
        migrations.AlterModelOptions(
            name='detectortimingoffset',
            options={'ordering': ('source',)},
        ),
    ]
