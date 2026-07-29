from django.db import migrations, models


def set_event_time(apps, schema_editor):
    Wedding = apps.get_model('invitation', 'Wedding')
    wedding = Wedding.objects.filter(pk=1).first()
    if wedding:
        wedding.event_datetime = wedding.event_datetime.replace(hour=16, minute=0, second=0, microsecond=0)
        wedding.save(update_fields=('event_datetime',))


class Migration(migrations.Migration):
    dependencies = [
        ('invitation', '0004_alter_wedding_event_datetime_alter_wedding_intro_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsvp',
            name='with_children',
            field=models.BooleanField(default=False, verbose_name='С детьми'),
        ),
        migrations.RunPython(set_event_time, migrations.RunPython.noop),
    ]
