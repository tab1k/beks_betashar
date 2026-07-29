from zoneinfo import ZoneInfo

from django.db import migrations


EVENT_TIME_ZONE = ZoneInfo('Asia/Almaty')


def set_event_time_to_4pm_local(apps, schema_editor):
    Wedding = apps.get_model('invitation', 'Wedding')
    wedding = Wedding.objects.filter(pk=1).first()
    if wedding is None:
        return

    local_event = wedding.event_datetime.astimezone(EVENT_TIME_ZONE)
    wedding.event_datetime = local_event.replace(
        hour=16,
        minute=0,
        second=0,
        microsecond=0,
    )
    wedding.save(update_fields=('event_datetime',))


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0005_rsvp_with_children_and_event_time'),
    ]

    operations = [
        migrations.RunPython(set_event_time_to_4pm_local, migrations.RunPython.noop),
    ]
