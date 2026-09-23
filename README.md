# MM Carousels

Пайплайн Instagram-каруселей для @mm.machine.ru: **JSON-спека → HTML → PNG 1080×1350**.
Три дизайн-системы на одной разметке — любую спеку можно собрать в любой из них:

| Система | Язык | Шрифт | Иконки |
|---|---|---|---|
| **mm-apple** (основная) | Apple HIG + Liquid Glass | Inter | Tabler |
| **mm-expressive** | Material 3 Expressive (Google) | Google Sans | Material Symbols Rounded |
| **mm-signal** | по мотивам айдентики МТС 2023 | Roboto Flex (wdth 140) + Onest | Tabler |

![Сравнение обложек](releases/compare-covers.png)

Лёгкий формат «одна мысль на слайд» во всех трёх.

Утверждено Умаром 23.09.2026. Всё, что было раньше (Neeraj Proof Guide, синий бенто, «тяжёлые» карусели с цифрами), отклонено и в репозиторий не входит.

## Быстрый старт

```bash
npm run setup                                   # Playwright + Chromium (один раз)
python3 scripts/build.py specs/mm-5-phrases-chatgpt.json
node scripts/render.mjs releases/mm-5-phrases-chatgpt
open releases/mm-5-phrases-chatgpt/contact-sheet.png
```

Нужны Node 20+ и Python 3 (только стандартная библиотека).

## Как создаётся карусель

1. **Тема и механика.** Берём приём из разбора сильных постов авторов (список, чек-лист признаков, интрига с разгадкой на 2-м слайде). Чужие тексты не копируем — только механику; все формулировки свои.
2. **Спека** `specs/<id>.json` — весь текст карусели (см. ниже). Кликбейтный, но честный заголовок: обещание раскрывается к 2-му слайду. 6–8 слайдов.
3. **Рендер обложки.** Качественный 3D-рендер на нейтральном фоне с Unsplash (только бесплатные, с подтверждения Умара) → `releases/<id>/assets/cover-render.jpg` + `cover-render.json` (источник, автор, лицензия, дата).
4. **Сборка** `scripts/build.py` → `releases/<id>/source.html` + `mm-apple.css`, `liquid.js`, шрифты, ассеты.
5. **Рендер** `scripts/render.mjs` → `01.png…NN.png`, `contact-sheet.png`, `index.html`. `liquid.js` строит преломление стекла прямо в Chromium.
6. **Проверка глазами** каждого PNG: нет обрезанного текста, контраст, объект обложки читается.
7. **Публикация** — только после «ок» Умара; подпись берётся из `caption.txt`.

## Спека карусели

```jsonc
{
  "handle": "@mm.machine.ru",
  "title": "5 фраз для ChatGPT",                      // для подписи внизу слайдов
  "cover": {
    "title_html": "5 фраз, после которых <b>ChatGPT</b> перестаёт лить воду",  // <b> = синий акцент
    "sub": "Копируй в любой запрос.",
    "chip_lbl": "сохрани", "chip": "Пригодится в каждом чате",                  // стеклянная плашка на рендере
    "render": { "w": 2200, "left": -90, "top": 640 }                             // рендер шире кадра, уходит за правый нижний край
  },
  "items": [                                            // слайды-пункты, один из видов:
    { "h": "Пусть сначала <b>спросит</b>", "p": "…",    // заголовок + одна строка
      "ctx": "…", "quote": "…", "reply": "…" },         //   чат: серый контекст → синяя фраза → серый пример ответа
    { "h": "…", "p": "…", "demo": "<div class=\"m-btn\">Начать</div>", "bad_lbl": "признак",
      "lbl": "вместо", "quote": "…" },                  //   мини-макет «было» + синяя карточка «вместо»
    { "h": "…", "p": "…", "lbl": "…", "quote": "…" }    //   просто крупная фраза
  ],
  "final": { "title_html": "Шпаргалка: <b>5 фраз</b>", "list": ["…"], "save_lbl": "…", "save": "Сохрани себе" },
  "caption": "подпись к посту"
}
```

В `demo` можно вставлять иконки: `{{icon:player-play}}` (имя файла из `assets/icons/tabler`).
Готовые мини-макеты: `.m-grad` (градиент), `.m-emoji`, `.m-cards`, `.m-btn`, `.m-text`, `.m-photo`, `.m-ui` + `.m-url` + `.m-cta` (шаг интерфейса), `.m-thumbs`, `.m-cite`.

## Как выбрать систему

```bash
python3 scripts/build.py specs/<id>.json                 # система из спеки ("design"), по умолчанию mm-apple
python3 scripts/build.py specs/<id>.json mm-expressive   # та же спека в другой системе → releases/<id>--mm-expressive
node scripts/render.mjs releases/<id>--mm-expressive
```

Система — папка `design-system/<name>/`: `system.json` (стили, скрипты, шрифты, набор иконок, таблица замены имён иконок), `style.css`, скрипты.
Разметка слайдов общая (`scripts/build.py`), системы только перекрашивают и перекраивают её классы.

## Дизайн-система mm-apple

Файлы `design-system/mm-apple/style.css` (4 секции, порядок важен) + `liquid.js`.

**Принципы** (Apple HIG: clarity, deference, depth; Liquid Glass): контент ведёт, стекло не мешает читать, иерархия размером и отступами, а не цветом.

| | |
|---|---|
| Фон | `#F3F6FC → #EEF1F8`, мягкий голубой и лиловый свет по углам. Никаких декоративных кругов и сеток |
| Акцент | systemBlue `#007AFF`; тёмная карточка `#1C1C1E`; вторичный текст `rgba(60,60,67,.62)` |
| Карточки | сгруппированные, радиус 38 px, сетка 6 колонок, зазор 18 px |
| Стекло | полупрозрачная белая тонировка, блик сверху, светящийся ободок, тень; `liquid.js` — преломление фона по краям (SVG-фильтр в `backdrop-filter`) |
| Шрифт | **Inter** (OFL), вес 400–800. Межбуквенное расстояние никогда не отрицательное; заголовки 72–98 px, межстрочный 1.04–1.1; текст 26–32 px, 1.42 |
| Иконки | **Tabler** (MIT) в синих скруглённых квадратах, как в «Настройках» iOS (`.sym`); галочки — заливной `circle-check-filled` (`.ok`) |
| Обложка | 3D-рендер крупнее кадра, объект уходит за правый нижний край, верх растворяется маской; заголовок сверху, стеклянная плашка поверх объекта |
| Пункты | номер в синей плашке, крупный заголовок, одна строка; середина никогда не пустая: чат как в «Сообщениях», мини-макет или шаг интерфейса |
| Финал | шпаргалка с галочками на всю высоту + синяя карточка «Сохрани» |

## Дизайн-система mm-expressive (язык Material 3 Expressive)

Берём открытую систему Google: Material Design открыт всем, токены и компоненты Apache-2.0.

| | |
|---|---|
| Цвет | тональные роли M3, baseline seed `#6750A4`: primary `#6750A4`, primary-container `#EADDFF`, secondary-container `#E8DEF8`, tertiary-container `#FFD8E4`, surface `#FEF7FF`, контейнеры `#F7F2FA…#E6E0E9`, on-surface `#1D1B20` |
| Глубина | тоном контейнера, без теней |
| Шрифт | Google Sans (OFL, кириллица; Display/Headline emphasized 600), трекинг 0 |
| Формы | радиусы шкалы M3 ×2 (24/32/56/96); формы Expressive — «печенье» 9 и 12 лепестков, «клевер» — сгенерированы формулой r(θ)=R(1+a·cos nθ), не файлы Google |
| Обложка | рендер в маске «печенья» поверх второго «печенья» tertiary-container, уходит за правый нижний край |
| Компоненты | pill-чипы, номер в «клевере», filled-карточки, пузыри чата primary / surface-container-highest, список с leading-иконкой, tertiary-карточка вместо Extended FAB |
| Иконки | Material Symbols Rounded, FILL 1 |

**Не используем:** логотип и четырёхцветку Google (#4285F4/#EA4335/#FBBC05/#34A853 вместе), иконки продуктов, Product Sans, слова Google / Material / Android в названиях и подписях (см. `licenses/GoogleSans-TRADEMARKS.md`).

## Дизайн-система mm-signal (по мотивам айдентики МТС)

Берём логику системы, не знаки бренда.

| | |
|---|---|
| Цвет | одна горячая краска `#FF4A1C` на тёплой бумаге `#F4F1EB`; холодная деталь `#2E5BFF` — одна на слайд; текст `#131416`; финал на `#0E0F11` |
| Шрифт | заголовки Roboto Flex `font-stretch:140%`, 650, КАПС, интервал 1.0, трекинг 0; текст Onest |
| Формы | радиусы 16/28/48, pill-кнопки, белые карточки с тонкой линией `#DDD8CF` |
| Обложка | рендер в большой скруглённой раме за правым нижним краем, акцентная полоса, холодный круг, плашка-акцент |
| Пункты | номер — холодная pill, акцентные блоки «вместо», чат акцент / белый / чёрный |
| Финал | тёмный слайд, акцентная кнопка-пилюля |

**Не используем:** логотип-квадрат и буквы М/Т/С по углам кадра, красный `#FF0032` (зарегистрирован как товарный знак), шрифты MTS Sans / Normalidad, их 3D, фото, иконки, название компании. Углы кадра всегда свободны.

## Ассеты и лицензии

| Что | Откуда | Лицензия | Где |
|---|---|---|---|
| Шрифт Inter | rsms/inter (из marketing-kit) | SIL OFL 1.1 | `assets/fonts/Inter`, `licenses/Inter-OFL.txt` |
| Шрифт Google Sans | google/fonts `ofl/googlesans`, урезан до кириллицы+латиницы | SIL OFL 1.1, без RFN; «Google Sans» — товарный знак | `assets/fonts/GoogleSans`, `licenses/GoogleSans-*.txt/md` |
| Шрифт Roboto Flex | google/fonts `ofl/robotoflex`, урезан | SIL OFL 1.1 | `assets/fonts/RobotoFlex`, `licenses/RobotoFlex-OFL.txt` |
| Шрифт Onest | из marketing-kit | SIL OFL 1.1 | `assets/fonts/Onest`, `licenses/Onest-OFL.txt` |
| Иконки Material Symbols Rounded (31 шт., fill) | google/material-design-icons | Apache-2.0 | `assets/icons/material-rounded`, `licenses/MaterialSymbols-Apache-2.0.txt` |
| Иконки | Tabler Icons (подмножество, 159 шт.) | MIT | `assets/icons/tabler`, `licenses/Tabler-MIT.txt` |
| 3D-иконки для макета «эмодзи» | Microsoft Fluent Emoji 3D | MIT | `assets/3d/fluent`, `licenses/FluentEmoji-MIT.txt` |
| Рендеры обложек | Unsplash (бесплатные) | Unsplash License | `releases/<id>/assets/cover-render.*`, `licenses/Unsplash.md` |

**Не используем никогда:** шрифты SF Pro / SF Compact / New York, SF Symbols, эмодзи Apple — по лицензии Apple они только для интерфейсов приложений на платформах Apple. Twemoji — только с атрибуцией, поэтому не берём. Открытые наборы в формате SF Symbols (OrchardKit/open-symbols) — это те же Tabler/Lucide/Heroicons, лицензия исходного набора.

**Контент:** не вкладываем выдуманные цитаты в уста реальных людей; цифры в постах — только проверенные.

## Выпуски

| id | Тема | Механика |
|---|---|---|
| `mm-5-phrases-chatgpt` | 5 фраз, после которых ChatGPT перестаёт лить воду | список фраз, чат-примеры |
| `mm-ai-site-tells` | Сайт, который сделала нейросеть, видно за 3 секунды | чек-лист признаков, мини-макеты |
| `mm-ask-hormozi` | Задай вопрос Хормози. Он ответит. Бесплатно (NotebookLM) | интрига → разгадка, шаги интерфейса |

Статус всех трёх: ждут публикации (основная система mm-apple). Для сравнения собраны `mm-5-phrases-chatgpt` и `mm-ai-site-tells` в mm-expressive и mm-signal (`releases/<id>--<system>`). Перед выпуском `mm-ask-hormozi` пройти шаги NotebookLM руками и сверить названия кнопок.
