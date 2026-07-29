from datetime import date, datetime

from django.db import models
from django.utils import timezone


def default_event_datetime():
    """Дата мероприятия. Нужна как умолчание: на пустой базе запись
    создаётся сама, и без этого сайт показывал сегодняшнее число."""
    return timezone.make_aware(datetime(2026, 8, 2, 16, 0))


def default_rsvp_deadline():
    return date(2026, 7, 31)


class SingletonModel(models.Model):
    """Модель, у которой всегда одна-единственная запись."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # защита от случайного удаления
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Wedding(SingletonModel):
    """Все тексты приглашения — редактируются в админке."""

    event_title = models.CharField(
        'Название мероприятия',
        max_length=120,
        default='Беташар тойға шақыру',
        help_text='Надпись над именами на обложке',
    )
    groom = models.CharField('Имя жениха', max_length=60, default='Бексултан')
    bride = models.CharField('Имя невесты', max_length=60, default='Дамира')

    event_datetime = models.DateTimeField(
        'Дата и время торжества',
        default=default_event_datetime,
        help_text='К этому времени идёт обратный отсчёт',
    )

    intro = models.TextField(
        'Текст приглашения (в конверте)',
        default=(
            'Дорогие родные и друзья! С трепетом и радостью приглашаем вас '
            'на наш беташар — разделите с нами этот особенный день.'
        ),
    )

    venue_name = models.CharField('Название заведения', max_length=120, default='Rixos President Astana')
    venue_address = models.CharField(
        'Адрес', max_length=200, default='г. Астана, летняя площадка'
    )
    map_url = models.URLField(
        'Ссылка на карту',
        blank=True,
        default='https://2gis.kz/astana/geo/70000001018072481/71.421419,51.134270',
    )

    dress_code = models.CharField('Дресс-код', max_length=120, default='Вечерний / Black tie')
    dress_code_note = models.CharField(
        'Пояснение к дресс-коду',
        max_length=250,
        blank=True,
        default='Будем признательны, если вы поддержите палитру торжества: оливковый, беж, шампань.',
    )
    dress_colors = models.CharField(
        'Цвета палитры (HEX через запятую)',
        max_length=200,
        default='#4A5240,#6B7355,#8C9475,#C9BFA6,#EDE5D4',
    )

    phone_1_label = models.CharField('Контакт 1 — имя', max_length=60, blank=True, default='Бексултан')
    phone_1 = models.CharField('Контакт 1 — телефон', max_length=32, blank=True)
    phone_2_label = models.CharField('Контакт 2 — имя', max_length=60, blank=True, default='Дамира')
    phone_2 = models.CharField('Контакт 2 — телефон', max_length=32, blank=True)

    rsvp_deadline = models.DateField('Ответить до', null=True, blank=True, default=default_rsvp_deadline)
    farewell = models.CharField(
        'Прощальная строка', max_length=200, default='С любовью и трепетом ждём вас'
    )

    hero_image = models.ImageField('Фото на обложку', upload_to='wedding/', blank=True)
    music = models.FileField('Фоновая музыка (mp3)', upload_to='wedding/', blank=True)

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашение'

    def __str__(self):
        return f'{self.groom} & {self.bride}'

    @property
    def palette(self):
        return [c.strip() for c in self.dress_colors.split(',') if c.strip()]


class ScheduleItem(models.Model):
    """Строка программы вечера."""

    time = models.CharField('Время', max_length=20, help_text='например 17:00')
    title = models.CharField('Событие', max_length=120)
    description = models.CharField('Описание', max_length=200, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Пункт программы'
        verbose_name_plural = 'Программа вечера'
        ordering = ('order', 'id')

    def __str__(self):
        return f'{self.time} — {self.title}'


class Rsvp(models.Model):
    """Ответ гостя."""

    ALONE = 'alone'
    COUPLE = 'couple'
    DECLINE = 'decline'
    ATTENDANCE_CHOICES = [
        (ALONE, 'Да, я приду один (одна)'),
        (COUPLE, 'Да, я приду с супругой (-ом)'),
        (DECLINE, 'Нет, я не смогу прийти'),
    ]

    name = models.CharField('Имя Фамилия', max_length=120)
    attendance = models.CharField('Ответ', max_length=16, choices=ATTENDANCE_CHOICES)
    with_children = models.BooleanField('С детьми', default=False)
    phone = models.CharField('Телефон', max_length=32, blank=True)
    wish = models.TextField('Пожелание', blank=True)
    created_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Ответ гостя'
        verbose_name_plural = 'Ответы гостей'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.name} — {self.get_attendance_display()}'

    @property
    def guests_count(self):
        return {self.ALONE: 1, self.COUPLE: 2}.get(self.attendance, 0)
