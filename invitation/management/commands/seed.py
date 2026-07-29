from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from invitation.models import Wedding

class Command(BaseCommand):
    help = 'Заполняет приглашение данными мероприятия'

    def handle(self, *args, **options):
        w = Wedding.load()
        w.event_title = 'Беташар тойға шақыру'
        w.groom = 'Бексултан'
        w.bride = 'Дамира'
        w.event_datetime = timezone.make_aware(datetime(2026, 8, 2, 16, 0))
        w.rsvp_deadline = date(2026, 7, 31)

        w.venue_name = 'Rixos President Astana'
        w.venue_address = 'г. Астана, летняя площадка'
        w.map_url = 'https://2gis.kz/astana/geo/70000001018072481/71.421419,51.134270'

        w.intro = (
            'Дорогие родные и друзья! С трепетом и радостью приглашаем вас '
            'на наш беташар — разделите с нами этот особенный день.'
        )
        w.save()

        self.stdout.write(self.style.SUCCESS('Данные приглашения загружены'))
