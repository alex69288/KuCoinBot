/**
 * АВТО-ИНИЦИАЛИЗАЦИЯ ИКОНок v0.1.15
 * Надежное подключение SVG-спрайта в средах с ограничениями (Telegram WebView)
 * 1) Один раз загружает /static/icons.svg и встраивает в DOM (inline)
 * 2) Конвертирует .icon.icon-* элементы в <svg><use href="#..."/></svg>
 * 3) Имеет фолбэк на текстовую метку data-icon-text при сбое загрузки
 */

(function () {
  'use strict';

  let spriteInjected = false;
  let spriteInjectPromise = null;

  function injectSpriteOnce() {
    if (spriteInjected) return Promise.resolve();
    if (spriteInjectPromise) return spriteInjectPromise;

    // Загружаем иконки и встраиваем в DOM для стабильной работы <use href="#id">
    spriteInjectPromise = fetch('/static/icons.svg', { cache: 'no-store' })
      .then(async (res) => {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const svgText = await res.text();

        const container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.width = '0';
        container.style.height = '0';
        container.style.overflow = 'hidden';
        container.style.visibility = 'hidden';
        container.setAttribute('aria-hidden', 'true');
        container.innerHTML = svgText;

        // Встраиваем в начало body, чтобы use ссылался только на #id
        document.body.insertBefore(container, document.body.firstChild);
        spriteInjected = true;
        console.log('[Icons] ✓ SVG спрайт встроен inline');
      })
      .catch((err) => {
        console.warn('[Icons] Не удалось загрузить спрайт:', err);
        spriteInjected = false;
      });

    return spriteInjectPromise;
  }

  const textFallbackMap = {
    'icon-check': '✓',
    'icon-close': '✗',
    'icon-warning': '⚠',
    'icon-info': 'i',
    'icon-trend-up': '↑',
    'icon-trend-down': '↓',
    'icon-refresh': '⟳',
    'icon-play': '▶',
    'icon-pause': '⏸',
    'icon-stop': '■'
  };

  function convertIconElement(iconElement) {
    // Уже содержит SVG — пропускаем
    if (iconElement.querySelector('svg')) return true;

    const classes = Array.from(iconElement.classList);
    const iconClass = classes.find((cls) => cls.startsWith('icon-') && cls !== 'icon');
    if (!iconClass) return false;

    const iconName = iconClass; // например 'icon-robot'

    // Очищаем возможные эмодзи/текст
    iconElement.textContent = '';

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');

    // Ссылаемся только на локальный #id — работает при inline-спрайте
    use.setAttribute('href', `#${iconName}`);
    use.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', `#${iconName}`);

    svg.appendChild(use);
    iconElement.appendChild(svg);
    return true;
  }

  function applyTextFallback(iconElement) {
    const classes = Array.from(iconElement.classList);
    const iconClass = classes.find((cls) => cls.startsWith('icon-') && cls !== 'icon');
    const fallback = iconElement.getAttribute('data-icon-text') || (iconClass ? textFallbackMap[iconClass] : '') || '•';
    iconElement.textContent = fallback;
  }

  function initializeIcons() {
    const icons = document.querySelectorAll('.icon[class*="icon-"]');
    if (!icons.length) {
      console.warn('[Icons] Не найдено элементов .icon');
      return;
    }

    injectSpriteOnce().finally(() => {
      let converted = 0;
      icons.forEach((el) => {
        const ok = convertIconElement(el);
        if (!ok) return;
        // Если спрайт не был встроен (ошибка загрузки), используем текстовые фолбэки
        if (!spriteInjected) applyTextFallback(el);
        else converted += 1;
      });
      if (spriteInjected && converted) console.log(`[Icons] ✓ Инициализировано ${converted} иконок`);
      if (!spriteInjected) console.warn('[Icons] Использованы текстовые фолбэки для иконок');
    });
  }

  // Автостарт
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeIcons);
  } else {
    initializeIcons();
  }

  // Переинициализация при динамическом добавлении
  window.reinitializeIcons = initializeIcons;
})();
