from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0006_increase_country_name_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stations_contact', to='inforecords.Contact'),
        ),
        migrations.AlterField(
            model_name='station',
            name='ict_contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stations_ict_contact', to='inforecords.Contact'),
        ),
    ]
