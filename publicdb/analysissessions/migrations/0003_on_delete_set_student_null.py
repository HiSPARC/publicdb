from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analysissessions', '0002_increase_emailfield_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyzedcoincidence',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysissessions.Student'),
        ),
    ]
