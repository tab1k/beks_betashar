import csv

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html

from .models import Rsvp, Wedding

admin.site.site_header = 'Свадебное приглашение'
admin.site.site_title = 'Приглашение'
admin.site.index_title = 'Разделы'


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Мероприятие', {'fields': ('event_title', 'groom', 'bride', 'event_datetime', 'hero_image', 'music')}),
        ('Тексты', {'fields': ('intro', 'farewell')}),
        ('Место проведения', {'fields': ('venue_name', 'venue_address', 'map_url')}),
        ('Дресс-код', {'fields': ('dress_code', 'dress_code_note', 'dress_colors')}),
        ('Контакты и RSVP', {
            'fields': ('phone_1_label', 'phone_1', 'phone_2_label', 'phone_2', 'rsvp_deadline'),
        }),
    )

    def has_add_permission(self, request):
        return not Wedding.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


def rsvp_stats():
    stats = Rsvp.objects.aggregate(
        total=Count('id'),
        alone=Count('id', filter=Q(attendance=Rsvp.ALONE)),
        couple=Count('id', filter=Q(attendance=Rsvp.COUPLE)),
        decline=Count('id', filter=Q(attendance=Rsvp.DECLINE)),
    )
    stats['guests'] = stats['alone'] + stats['couple'] * 2
    return stats


@admin.register(Rsvp)
class RsvpAdmin(admin.ModelAdmin):
    """Список гостей. Заказчикам выдаётся только право просмотра."""

    change_list_template = 'admin/invitation/rsvp/change_list.html'

    list_display = ('name', 'answer', 'guests', 'phone_link', 'short_wish', 'when')
    list_filter = ('attendance',)
    search_fields = ('name', 'phone', 'wish')
    readonly_fields = ('created_at',)
    list_per_page = 100

    @admin.display(description='Ответ', ordering='attendance')
    def answer(self, obj):
        if obj.attendance == obj.DECLINE:
            return format_html('<span style="color:#A15C5C">{}</span>', '✕ не сможет')
        text = 'придёт один (одна)' if obj.attendance == obj.ALONE else ('придёт с парой и детьми' if obj.with_children else 'придёт с парой')
        return format_html('<span style="color:#3F6B3F">✓ {}</span>', text)

    @admin.display(description='Гостей')
    def guests(self, obj):
        return obj.guests_count or '—'

    @admin.display(description='Телефон')
    def phone_link(self, obj):
        if not obj.phone:
            return '—'
        return format_html('<a href="tel:{}">{}</a>', obj.phone.replace(' ', ''), obj.phone)

    @admin.display(description='Пожелание')
    def short_wish(self, obj):
        if not obj.wish:
            return '—'
        return (obj.wish[:70] + '…') if len(obj.wish) > 70 else obj.wish

    @admin.display(description='Ответил', ordering='created_at')
    def when(self, obj):
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y  %H:%M')

    def has_add_permission(self, request):
        # анкеты приходят только с сайта, руками их не заводят
        return False

    def get_urls(self):
        return [
            path(
                'export/',
                self.admin_site.admin_view(self.export_csv),
                name='invitation_rsvp_export',
            ),
        ] + super().get_urls()

    def export_csv(self, request):
        """Выгрузка списка гостей — доступна и тем, у кого только просмотр."""
        if not self.has_view_permission(request):
            raise PermissionDenied

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="gosti.csv"'
        response.write('﻿')  # BOM, иначе Excel ломает кириллицу

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Имя Фамилия', 'Ответ', 'Гостей', 'Телефон', 'Пожелание', 'Когда ответил'])
        for r in Rsvp.objects.all():
            writer.writerow([
                r.name,
                r.get_attendance_display(),
                r.guests_count,
                r.phone,
                r.wish,
                timezone.localtime(r.created_at).strftime('%d.%m.%Y %H:%M'),
            ])
        return response

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), 'stats': rsvp_stats(), 'title': 'Кто придёт'}
        return super().changelist_view(request, extra_context)
