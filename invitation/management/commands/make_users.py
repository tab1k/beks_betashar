import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

CLIENT_GROUP = 'Заказчики'


def make_password(length=12):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class Command(BaseCommand):
    help = 'Создаёт суперпользователя и вход для заказчиков (только просмотр списка гостей)'

    def add_arguments(self, parser):
        parser.add_argument('--admin', default='admin', help='логин суперпользователя')
        parser.add_argument('--admin-password', default=None)
        parser.add_argument('--client', default='guests', help='логин для заказчиков')
        parser.add_argument('--client-password', default=None)

    def handle(self, *args, **options):
        User = get_user_model()

        # ── суперпользователь: полный доступ ко всем настройкам приглашения
        admin_password = options['admin_password'] or make_password()
        admin_user, created = User.objects.get_or_create(
            username=options['admin'],
            defaults={'is_staff': True, 'is_superuser': True},
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password(admin_password)
        admin_user.save()

        # ── группа заказчиков: только просмотр ответов гостей
        group, _ = Group.objects.get_or_create(name=CLIENT_GROUP)
        group.permissions.set(
            Permission.objects.filter(codename='view_rsvp', content_type__app_label='invitation')
        )

        client_password = options['client_password'] or make_password()
        client, _ = User.objects.get_or_create(
            username=options['client'],
            defaults={'is_staff': True},
        )
        client.is_staff = True
        client.is_superuser = False
        client.set_password(client_password)
        client.save()
        client.groups.set([group])

        w = self.style.WARNING
        ok = self.style.SUCCESS
        self.stdout.write(ok('\nАккаунты созданы. Пароли показаны один раз — сохраните.\n'))
        self.stdout.write('  Полный доступ (вы):')
        self.stdout.write(f'    логин:  {w(admin_user.username)}')
        self.stdout.write(f'    пароль: {w(admin_password)}\n')
        self.stdout.write('  Заказчики — видят только список гостей:')
        self.stdout.write(f'    логин:  {w(client.username)}')
        self.stdout.write(f'    пароль: {w(client_password)}\n')
        self.stdout.write('  Вход: /admin/\n')
