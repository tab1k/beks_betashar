from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from invitation.models import ScheduleItem, Wedding

SCHEDULE = [
    ('14:00', 'Сбор гостей', 'Встреча на летней площадке'),
    ('14:30', 'Беташар', 'Обряд открытия лица невесты'),
    ('15:15', 'Дастархан', 'Праздничный обед'),
    ('16:30', 'Поздравления', 'Слова родных и близких'),
    ('17:30', 'Музыкальная программа', 'Живая музыка и танцы'),
]


class Command(BaseCommand):
    help = 'Заполняет приглашение данными мероприятия'

    def handle(self, *args, **options):
        w = Wedding.load()
        w.event_title = 'Беташар тойға шақыру'
        w.groom = 'Бексултан'
        w.bride = 'Дамира'
        w.event_datetime = timezone.make_aware(datetime(2026, 8, 2, 14, 0))
        w.rsvp_deadline = date(2026, 7, 31)

        w.venue_name = 'Rixos President Astana'
        w.venue_address = 'г. Астана, летняя площадка'
        w.map_url = 'https://2gis.kz/astana/geo/70000001018072481/71.421419,51.134270'

        w.intro = (
            'Дорогие родные и друзья! С трепетом и радостью приглашаем вас '
            'на наш беташар — разделите с нами этот особенный день.'
        )
        w.save()

        ScheduleItem.objects.all().delete()
        for i, (time, title, desc) in enumerate(SCHEDULE, start=1):
            ScheduleItem.objects.create(time=time, title=title, description=desc, order=i)

        self.stdout.write(self.style.SUCCESS('Данные приглашения загружены'))
