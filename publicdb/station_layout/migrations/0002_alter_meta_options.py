from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station_layout', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stationlayout',
            options={'ordering': ('station', 'active_date'), 'get_latest_by': 'active_date'},
        ),
    ]
