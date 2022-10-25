from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histograms', '0008_rename_rchi2_to_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='summary',
            name='needs_update_singles',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='summary',
            name='num_singles',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
