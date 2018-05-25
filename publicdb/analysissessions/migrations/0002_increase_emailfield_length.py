from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysissessions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionrequest',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
