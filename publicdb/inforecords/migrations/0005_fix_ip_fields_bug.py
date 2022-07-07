from django.db import migrations, models


def copy_ip(apps, schema_editor):
    pc_model = apps.get_model("inforecords", "Pc")

    for pc in pc_model.objects.all():
        pc.new_ip = pc.ip.strip() or None if pc.ip else None
        pc.save(update_fields=['new_ip'])


class Migration(migrations.Migration):

    dependencies = [
        ('inforecords', '0004_update_email_ip_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='pc',
            name='new_ip',
            field=models.GenericIPAddressField(unique=True, blank=True,
                                               null=True, protocol='ipv4'),
        ),
        migrations.RunPython(copy_ip, lambda *args, **kwargs: None),
        migrations.RemoveField(
            model_name='pc',
            name='ip',
        ),
        migrations.RenameField(
            model_name='pc',
            old_name='new_ip',
            new_name='ip',
        ),
    ]
