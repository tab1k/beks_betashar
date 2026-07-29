# Свадебное приглашение

Django-лендинг с приглашением на свадьбу и анкетой гостя (RSVP).
Мобильная вёрстка — основная: страница всегда рисуется колонкой шириной до 520 px
и по центру на десктопе.

## Запуск

```bash
.venv/bin/python manage.py runserver
```

- Приглашение — http://127.0.0.1:8000/
- Админка — http://127.0.0.1:8000/admin/

Два входа:

| Кто | Логин | Что видит |
|---|---|---|
| Вы | `admin` | всё: тексты, дату, место, программу, ответы гостей |
| Заказчики | `guests` | только «Кто придёт» — список гостей и выгрузку в Excel |

Пересоздать аккаунты и получить новые пароли:

```bash
.venv/bin/python manage.py make_users
```

Первичная установка на чистой машине:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed          # демо-данные приглашения
.venv/bin/python manage.py createsuperuser
```

## Что где

| Файл | Назначение |
|---|---|
| [invitation/models.py](invitation/models.py) | `Wedding` (все тексты, одна запись), `ScheduleItem` (программа), `Rsvp` (ответы гостей) |
| [invitation/views.py](invitation/views.py) | главная страница и AJAX-приём анкеты |
| [invitation/forms.py](invitation/forms.py) | форма RSVP |
| [invitation/admin.py](invitation/admin.py) | админка, в шапке списка ответов — сводка «придут N человек» |
| [templates/invitation/index.html](templates/invitation/index.html) | вся страница |
| [static/css/style.css](static/css/style.css) | оформление |
| [static/js/main.js](static/js/main.js) | обложка, отсчёт, анимации, отправка анкеты |

## Редактирование контента

Всё меняется в админке, без правки кода:

- **Приглашение** — имена, дата и время (к ней идёт обратный отсчёт), тексты,
  место проведения, ссылка на карту, дресс-код и его палитра, телефоны,
  фото на обложку, фоновая музыка (mp3).
- **Программа вечера** — список пунктов «время → событие».
- **Ответы гостей** — анкеты с фильтром по варианту ответа и поиском.

Палитра дресс-кода задаётся строкой HEX-цветов через запятую, например
`#454D3B,#6B7355,#8C9475,#C9BFA6,#EDE5D4`.

## Устройство страницы

1. Обложка с кнопкой «Открыть» (при нажатии включается музыка, если загружена)
2. Hero — имена, дата
3. Конверт с цитатой
4. Обращение к гостям
5. Дата + обратный отсчёт (склонения «45 дней / 4 часа / 1 минута»)
6. Место проведения и кнопка карты
7. Программа вечера
8. Дресс-код и палитра
9. Анкета гостя — отправляется без перезагрузки, ответ сразу виден в админке
10. Контакты и финальный блок

Ссылка с якорем (например `…/#rsvp`) открывает приглашение сразу, минуя обложку —
удобно рассылать гостям прямую ссылку на анкету.

## Перед публикацией

В [config/settings.py](config/settings.py):

- `DEBUG = False`
- `SECRET_KEY` — вынести в переменную окружения
- `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` — указать реальный домен
- `python manage.py collectstatic` и раздача `static/` + `media/` веб-сервером

## Выкладка на PythonAnywhere

Домен `betashar.pythonanywhere.com` уже прописан в `ALLOWED_HOSTS` и
`CSRF_TRUSTED_ORIGINS`.

После каждой заливки кода — в bash-консоли PythonAnywhere:

```bash
cd ~/betashar
python manage.py migrate
python manage.py collectstatic --noinput
```

и **Web → Reload**.

Первый раз дополнительно:

```bash
python manage.py seed        # данные мероприятия
python manage.py make_users  # логины admin и guests, пароли покажет
```

`db.sqlite3` намеренно не попадает в репозиторий — у сервера своя база.
Поэтому тексты и дату там задаёт либо `seed`, либо админка.

Во вкладке **Web → Static files** должно быть:

| URL | Directory |
|---|---|
| `/static/` | `/home/<логин>/betashar/staticfiles` |
| `/media/` | `/home/<логин>/betashar/media` |

Без этого при `DEBUG = False` отвалятся стили, шрифты и музыка.
