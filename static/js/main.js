/* Свадебное приглашение — обложка, отсчёт, анимации, RSVP */
(function () {
  'use strict';

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ───────── обложка ───────── */
  var cover = $('#cover');
  var page  = $('#page');
  var openBtn = $('#openBtn');
  var ripple = $('#ripple');
  var rippleLayer = $('#rippleLayer');

  var GROW = 750;   // круг разрастается
  var WASH = 620;   // и растворяется, открывая приглашение

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.body.classList.add('locked');

  // браузер восстанавливает прокрутку после перезагрузки — нам это мешает,
  // приглашение всегда должно открываться с первого экрана
  if ('scrollRestoration' in window.history) {
    window.history.scrollRestoration = 'manual';
  }

  function jumpTop() {
    var html = document.documentElement;
    // scroll-behavior: smooth действует и на scrollTo, и на scrollTop —
    // на время прыжка его надо снять, вернуть можно только следующей задачей
    html.style.scrollBehavior = 'auto';
    window.scrollTo(0, 0);
    html.scrollTop = 0;
    document.body.scrollTop = 0;
    window.setTimeout(function () { html.style.scrollBehavior = ''; }, 60);
  }

  jumpTop();

  function reveal(withMusic) {
    document.body.classList.remove('locked');
    page.classList.add('is-visible');
    if (withMusic !== false) { startMusic(); }
    startReveals();
  }

  /* круг расходится из кнопки на весь экран, затем растворяется */
  function growCircle() {
    rippleLayer.hidden = false;
    var box = rippleLayer.getBoundingClientRect();
    var btn = openBtn.getBoundingClientRect();
    var cx = btn.left + btn.width / 2 - box.left;
    var cy = btn.top + btn.height / 2 - box.top;

    // радиус до самого дальнего угла обложки
    var far = Math.max(
      Math.sqrt(cx * cx + cy * cy),
      Math.sqrt((box.width - cx) * (box.width - cx) + cy * cy),
      Math.sqrt(cx * cx + (box.height - cy) * (box.height - cy)),
      Math.sqrt((box.width - cx) * (box.width - cx) + (box.height - cy) * (box.height - cy))
    );

    ripple.style.left = cx + 'px';
    ripple.style.top = cy + 'px';
    void ripple.offsetWidth;                       // применяем стартовое состояние
    ripple.style.transform = 'translate(-50%, -50%) scale(' + (far / 50 + 0.2) + ')';

    window.setTimeout(function () {
      cover.style.display = 'none';                // прячем под кругом
      jumpTop();                                   // прыжок наверх не виден под кругом
      reveal(false);                               // музыка уже играет с момента нажатия
      ripple.classList.add('is-washing');          // круг растворяется
    }, GROW);

    window.setTimeout(function () { rippleLayer.hidden = true; }, GROW + WASH + 60);
  }

  function openInvitation(withMusic) {
    if (calm || !rippleLayer) {                    // без анимации — просто гасим обложку
      cover.classList.add('is-open');
      jumpTop();
      reveal(withMusic);
      window.setTimeout(function () { cover.style.display = 'none'; }, 1000);
      return;
    }
    growCircle();
  }

  if (openBtn) {
    openBtn.addEventListener('click', function () {
      startMusic();                                // строго здесь: браузеры
      openBtn.disabled = true;                     // разрешают звук только
      openBtn.classList.add('is-pressed');         // по действию пользователя
      openInvitation(false);
    });
  }

  // прямая ссылка на раздел (например …/#rsvp) — открываем сразу, без обложки
  if (window.location.hash.length > 1) {
    cover.classList.add('is-open');
    cover.style.display = 'none';
    reveal(false);
    var anchor = document.getElementById(window.location.hash.slice(1));
    if (anchor) {
      window.setTimeout(function () { anchor.scrollIntoView(); }, 60);
    }
  }

  /* ───────── музыка ───────── */
  var audio = $('#audio');
  var musicBtn = $('#musicBtn');

  function setPressed(on) {
    if (musicBtn) { musicBtn.setAttribute('aria-pressed', on ? 'true' : 'false'); }
  }

  var VOLUME = 0.7;
  var fadeTimer = null;

  function fadeIn() {
    window.clearInterval(fadeTimer);
    audio.volume = 0;
    fadeTimer = window.setInterval(function () {
      var next = audio.volume + VOLUME / 16;
      if (next >= VOLUME) {
        audio.volume = VOLUME;
        window.clearInterval(fadeTimer);
      } else {
        audio.volume = next;
      }
    }, 90);
  }

  function startMusic() {
    if (!audio) { return; }
    var p = audio.play();
    if (p && p.then) {
      p.then(function () { setPressed(true); fadeIn(); })
       .catch(function () { setPressed(false); });   // браузер не пустил — сработает кнопка
    } else {
      setPressed(true);
      fadeIn();
    }
  }

  if (musicBtn && audio) {
    musicBtn.addEventListener('click', function () {
      if (audio.paused) {
        startMusic();
      } else {
        window.clearInterval(fadeTimer);
        audio.pause();
        setPressed(false);
      }
    });
  }

  /* ───────── шапка над тёмным hero ───────── */
  var topbar = $('.topbar');
  var hero = $('.hero');

  if (topbar && hero) {
    var syncTopbar = function () {
      var overHero = hero.getBoundingClientRect().bottom > 56;
      topbar.classList.toggle('on-dark', overHero);
    };
    syncTopbar();
    window.addEventListener('scroll', syncTopbar, { passive: true });
    window.addEventListener('resize', syncTopbar);
  }

  /* ───────── появление секций ───────── */
  var revealsStarted = false;

  function startReveals() {
    if (revealsStarted) { return; }
    revealsStarted = true;

    var reveals = $$('.reveal');

    if (!('IntersectionObserver' in window)) {
      reveals.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

    reveals.forEach(function (el) { io.observe(el); });

    // то, что уже в кадре (hero), показываем сразу — не ждём первого
    // уведомления наблюдателя, иначе после обложки будет заметная пауза
    var vh = window.innerHeight;
    reveals.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < vh * 0.9 && r.bottom > 0) {
        el.classList.add('is-in');
        io.unobserve(el);
      }
    });
  }

  /* ───────── обратный отсчёт ───────── */
  var cd = $('#countdown');
  if (cd) {
    var target = new Date(cd.dataset.target).getTime();
    var out = {
      d: cd.querySelector('[data-cd="d"]'),
      h: cd.querySelector('[data-cd="h"]'),
      m: cd.querySelector('[data-cd="m"]'),
      s: cd.querySelector('[data-cd="s"]')
    };
    var pad = function (n) { return n < 10 ? '0' + n : String(n); };

    // русские склонения: 1 день / 2 дня / 5 дней
    var FORMS = {
      d: ['день', 'дня', 'дней'],
      h: ['час', 'часа', 'часов'],
      m: ['минута', 'минуты', 'минут'],
      s: ['секунда', 'секунды', 'секунд']
    };
    var plural = function (n, forms) {
      var n10 = n % 10;
      var n100 = n % 100;
      if (n10 === 1 && n100 !== 11) { return forms[0]; }
      if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) { return forms[1]; }
      return forms[2];
    };
    var setCell = function (key, value, padded) {
      out[key].textContent = padded ? pad(value) : String(value);
      out[key].nextElementSibling.textContent = plural(value, FORMS[key]);
    };

    var tick = function () {
      var left = target - Date.now();
      if (left < 0) { left = 0; }
      var sec = Math.floor(left / 1000);
      setCell('d', Math.floor(sec / 86400), false);
      setCell('h', Math.floor(sec / 3600) % 24, true);
      setCell('m', Math.floor(sec / 60) % 60, true);
      setCell('s', sec % 60, true);
    };

    tick();
    window.setInterval(tick, 1000);
  }

  /* ───────── RSVP ───────── */
  var form = $('#rsvpForm');
  if (form) {
    var submitBtn = $('#submitBtn');
    var thanks = $('#thanks');
    var childrenOption = $('#childrenOption');

    var syncChildrenOption = function () {
      if (!childrenOption) { return; }
      var couple = form.querySelector('[name="attendance"][value="couple"]');
      var show = couple && couple.checked;
      childrenOption.hidden = !show;
      if (!show) { childrenOption.querySelector('input').checked = false; }
    };
    $$('.option input[name="attendance"]', form).forEach(function (input) {
      input.addEventListener('change', syncChildrenOption);
    });
    syncChildrenOption();

    var clearErrors = function () {
      $$('.field__error', form).forEach(function (el) { el.textContent = ''; });
      $$('.is-invalid', form).forEach(function (el) { el.classList.remove('is-invalid'); });
    };

    var showErrors = function (errors) {
      Object.keys(errors).forEach(function (field) {
        var box = form.querySelector('[data-error="' + field + '"]');
        if (box) { box.textContent = errors[field].join(' '); }
        var input = form.querySelector('[name="' + field + '"]');
        if (input && input.type !== 'radio') { input.classList.add('is-invalid'); }
      });
      var first = form.querySelector('.field__error:not(:empty)');
      if (first) { first.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearErrors();

      var name = form.querySelector('[name="name"]');
      var picked = form.querySelector('[name="attendance"]:checked');
      var local = {};
      if (!name.value.trim() || name.value.trim().length < 2) {
        local.name = ['Пожалуйста, укажите имя и фамилию'];
      }
      if (!picked) {
        local.attendance = ['Выберите один из вариантов'];
      }
      if (Object.keys(local).length) { showErrors(local); return; }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Отправляем…';

      fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form)
      })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
          if (res.ok && res.data.ok) {
            $('#thanksTitle').textContent = res.data.title;
            $('#thanksText').textContent = res.data.message;
            form.hidden = true;
            thanks.hidden = false;
            thanks.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } else {
            showErrors(res.data.errors || { name: ['Не удалось отправить. Попробуйте ещё раз.'] });
            submitBtn.disabled = false;
            submitBtn.textContent = 'Отправить';
          }
        })
        .catch(function () {
          showErrors({ name: ['Нет связи с сервером. Попробуйте ещё раз.'] });
          submitBtn.disabled = false;
          submitBtn.textContent = 'Отправить';
        });
    });
  }
})();
