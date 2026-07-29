from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RsvpForm
from .models import Wedding

MONTHS_RU = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]
WEEKDAYS_RU = [
    'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье',
]


#  Песня по умолчанию. Если в админку загрузят свой файл — играет он.
DEFAULT_MUSIC = 'audio/Ed_Sheeran_-_Perfect_(SkySound.cc).mp3'


def index(request):
    wedding = Wedding.load()
    event = timezone.localtime(wedding.event_datetime)

    context = {
        'music_url': wedding.music.url if wedding.music else static(DEFAULT_MUSIC),
        'w': wedding,
        'form': RsvpForm(),
        'event': event,
        'day': event.day,
        'month': MONTHS_RU[event.month - 1],
        'weekday': WEEKDAYS_RU[event.weekday()],
        'time': event.strftime('%H:%M'),
        'countdown_iso': event.isoformat(),
    }
    return render(request, 'invitation/index.html', context)


@require_POST
def rsvp(request):
    form = RsvpForm(request.POST)
    if form.is_valid():
        obj = form.save()
        declined = obj.attendance == obj.DECLINE
        return JsonResponse({
            'ok': True,
            'title': 'Спасибо!' if not declined else 'Спасибо за ответ',
            'message': (
                'Ваш ответ принят. Будем очень рады видеть вас на нашем празднике!'
                if not declined
                else 'Нам жаль, что вы не сможете быть с нами. Спасибо, что дали знать.'
            ),
        })
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
