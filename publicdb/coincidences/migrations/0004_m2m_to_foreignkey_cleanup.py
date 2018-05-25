import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coincidences', '0003_m2m_to_foreignkey'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coincidence',
            name='events',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='coinc',
            new_name='coincidence',
        ),
        migrations.AlterField(
            model_name='event',
            name='coincidence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='coincidences.Coincidence'),
            preserve_default=False,
        ),
    ]
