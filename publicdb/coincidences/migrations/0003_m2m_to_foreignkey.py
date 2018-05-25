import django.db.models.deletion

from django.db import migrations, models
from django.db.models import Count

from sapphire.utils import pbar


def m2m_to_foreignkey(apps, schema_editor):
    """Forwards migrations"""
    m2m_model = apps.get_model('coincidences', 'Coincidence')
    print('')
    coincidences = m2m_model.objects.all().annotate(n_events=Count('events')).exclude(n_events=0)
    for coincidence in pbar(coincidences.iterator(), length=coincidences.count()):
        for event in coincidence.events.all():
            event.coinc = coincidence
            event.save()


def foreignkey_to_m2m(apps, schema_editor):
    """Backwards migrations"""
    fk_model = apps.get_model('coincidences', 'Event')
    print('')
    for event in pbar(fk_model.objects.all().iterator(), length=fk_model.objects.all().count()):
        event.coincidence.events.add(event)


class Migration(migrations.Migration):

    dependencies = [
        ('coincidences', '0002_arrayfields_for_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='coinc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fk_events', to='coincidences.Coincidence'),
        ),
        # Convert m2m from coincidences relations to foreign keys on events
        migrations.RunPython(
            m2m_to_foreignkey,
            foreignkey_to_m2m,
        ),
    ]
