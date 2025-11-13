# Редизайн иконок v0.1.15

Данное изменение полностью обновляет систему иконок веб‑приложения и устраняет проблему отсутствия отображения в средах с ограничениями (например, Telegram WebView).

## Что изменилось

- Новый единый спрайт `webapp/static/icons.svg` в современном минималистичном стиле (stroke 1.75).
- Инициализация иконок через inline-встраивание спрайта: файл `webapp/static/icons-init.js` загружает SVG один раз и вставляет в DOM, а затем подключает иконки по ссылке `#icon-*` (устойчивее, чем внешние ссылки `/static/icons.svg#...`).
- Фолбэк на текстовые символы: если загрузить спрайт не удалось, элементы `.icon` получают содержимое из `data-icon-text` или из стандартной карты фолбэков (например, `✓`, `✗`, `⚠`, `↑`, `↓`).
- Синхронизированная толщина линий в `webapp/static/icons.css` с новым спрайтом (1.75).
- Сохранены прежние идентификаторы символов (`icon-robot`, `icon-chart`, `icon-trend-up`, и т.д.), так что существующие классы в разметке продолжают работать.

## Как использовать иконки в разметке

- Добавьте элемент:
  ```html
  <span class="icon icon-robot"></span>
  ```
  После загрузки страницы иконка автоматически превратится в SVG: `<svg><use href="#icon-robot"/></svg>`.

- Задайте размер (опционально):
  ```html
  <span class="icon icon-lg icon-robot"></span>
  ```

- Задайте цвет классом или CSS-переменными (иконки используют `currentColor`):
  ```html
  <span class="icon icon-success icon-check"></span>
  ```

- Добавьте текстовый фолбэк (опционально):
  ```html
  <span class="icon icon-warning icon-refresh" data-icon-text="↻"></span>
  ```
  Если по какой-либо причине загрузить спрайт не удалось, будет показан `↻`.

## Почему это исправляет проблему

Ранее некоторые webview блокировали внешние ссылки внутри `<use href="/static/icons.svg#...">`. Теперь спрайт внедряется в DOM, и `<use href="#...">` ссылается на локальные символы, что работает стабильно даже при ограничениях.

## Список основных символов

- Статусы: `icon-check`, `icon-close`, `icon-warning`, `icon-circle-*` (цветные круги)
- Торговля/графики: `icon-chart`, `icon-trend-up`, `icon-trend-down`, `icon-ema`, `icon-money`
- Действия: `icon-play`, `icon-pause`, `icon-stop`, `icon-refresh`, `icon-save`, `icon-trash`
- Интерфейс: `icon-settings`, `icon-list`, `icon-home`, `icon-document`, `icon-pin`, `icon-bell`, `icon-wallet`, `icon-card`, `icon-phone`, `icon-wrench`, `icon-inbox`, `icon-target`

## Примечания

- Цвет иконок управляется через `color: ...` (они используют `currentColor`). Классы вида `.icon-success`, `.icon-danger` уже настроены в `icons.css`.
- Круги статусов (`icon-circle-...`) используют `fill: currentColor` — их цвет настраивается через класс, например `.icon-circle-green`.
- При добавлении новых иконок просто добавьте `<symbol id="icon-new" ...>` в `icons.svg` и используйте класс `icon-new` на элементе.
