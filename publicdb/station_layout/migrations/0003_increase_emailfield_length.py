from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('station_layout', '0002_alter_meta_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationlayoutquarantine',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
