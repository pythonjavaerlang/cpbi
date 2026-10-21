# ЧПБІ — вебсайт (GitHub Pages)

Статичний сайт Чернівецького православного богословського інституту
(`cpbi.info`). Генерується з контенту та шаблонів у цьому репозиторії й
публікується на GitHub Pages.

## Як це працює

- `build.py` рендерить увесь сайт у теку `dist/` (чисті URL, SEO/Open Graph,
  згенеровані OG-зображення українською, `sitemap.xml`, `robots.txt`,
  `.nojekyll`, `CNAME`).
- GitHub Actions (`.github/workflows/pages.yml`) на кожен push у `master`
  встановлює залежності, збирає сайт і публікує **вміст** `dist/` у корені
  Pages. Тека `dist/` **не зʼявляється** в URL і **не комітиться** — її щоразу
  збирає CI.
- Усі внутрішні посилання та шляхи до ресурсів **відносні** (`../`, `./`), тож
  сайт працює з кореня домену, з підкаталогу або навіть із `file://`. Лише
  canonical / Open Graph лишаються абсолютними (`https://cpbi.info/...`), як і
  вимагають пошукові системи та соцмережі.

## Локальна збірка

```bash
pip install -r requirements.txt
python build.py        # -> dist/
python verify.py       # структурна перевірка
python serve_test.py   # (необовʼязково) локальний HTTP-тест
```

Залежності: `jinja2`, `markupsafe`, `pillow`, `staticmap`.

## Структура

```
build.py            головний генератор
config.py           домен, SEO-налаштування, мапа «гарних» URL (slug)
slugs.py            транслітерація укр. → латиниця для URL
seo.py              <head>: title/description/canonical/OG/Twitter/JSON-LD
og_image.py         генерація OG-зображень (Pillow, кирилиця)
book_descriptions.py короткі описи книг для діалогу «Про книгу»
make_maps.py        генерація історичних біблійних карт (staticmap + Nominatim)
biblical_places.py  довідник біблійних місць з координатами (давні → сучасні)
geocode.py          геокодер Nominatim з кешем і обмеженням частоти
verify.py           перевірка зібраного сайту
serve_test.py       локальний HTTP-smoke-тест
templates/          шаблони Jinja2
content/export.json знімок контенту (flatpages, книги, розділи, журнал, новини)
tally/              JSON форм для імпорту в Tally.so
assets/media/       усі медіа, що потрібні сайту (CSS, JS, зображення, шрифти, відео)
assets/maps/        згенеровані біблійні карти (комітяться; стабільні)
assets/fonts/       шрифти з кирилицею для OG-зображень і карт
.github/workflows/  CI: збірка і публікація на Pages
```

## Форми (Tally.so)

Динамічні форми замінено на Tally.so. Вбудовані форми:
контакти (`/kontakty/`), вступ (`/vstup/`), початкова школа
(`/pochatkova-shkola/`), передплата журналу (`/peredplata-zhurnalu/`).
Вихідний JSON для імпорту — у теці `tally/`.

## Карти

`make_maps.py` будує історичні карти: сучасна OSM-підкладка (staticmap) +
підписи давніх назв українською та маршрути (Pillow). Координати давніх місць
беруться з `biblical_places.py` (напр., Тахпанхес = Tell Defenneh, Ноф =
Memphis), інші — через Nominatim (`geocode.py`, з кешем). Згенеровані PNG
зберігаються в `assets/maps/` і комітяться, тож CI не потребує мережі для карт.

Щоб оновити карти:

```bash
python make_maps.py    # -> assets/maps/*.png
```

## Оновлення контенту

`content/export.json` — знімок бази. Щоб оновити, повторно експортуйте дані й
замініть файл, потім перезберіть сайт.

## Налаштування GitHub Pages

У налаштуваннях репозиторію: **Settings → Pages → Build and deployment →
Source: GitHub Actions**. Кастомний домен `cpbi.info` задається файлом `CNAME`,
який генерує збірка.
