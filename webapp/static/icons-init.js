/**
 * АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ ИКОНОК v0.1.15
 * Преобразует все иконки в формат SVG спрайтов
 * Загружается сразу после загрузки DOM
 */

(function() {
  'use strict';

  // Функция инициализации иконок
  function initializeIcons() {
    console.log('[Icons] Запуск инициализации иконок...');
    
    // Находим все элементы с классом icon
    const icons = document.querySelectorAll('.icon[class*="icon-"]');
    console.log(`[Icons] Найдено элементов: ${icons.length}`);
    
    let convertedCount = 0;
    
    icons.forEach(iconElement => {
      // Проверяем, не содержит ли уже SVG
      if (iconElement.querySelector('svg')) {
        return; // Уже обработано
      }
      
      // Получаем все классы иконки
      const classes = Array.from(iconElement.classList);
      
      // Находим класс с именем иконки (icon-*)
      const iconClass = classes.find(cls => cls.startsWith('icon-') && cls !== 'icon');
      
      if (!iconClass) {
        return; // Нет специфичного класса иконки
      }
      
      // Извлекаем имя иконки
      const iconName = iconClass; // например 'icon-robot'
      
      // Очищаем содержимое (удаляем старые текстовые эмодзи если есть)
      iconElement.innerHTML = '';
      
      // Создаем SVG элемент
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
      
      // Устанавливаем ссылку на спрайт (двойная установка для совместимости)
      use.setAttribute('href', `/static/icons.svg#${iconName}`);
      use.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', `/static/icons.svg#${iconName}`);
      
      // Собираем SVG
      svg.appendChild(use);
      iconElement.appendChild(svg);
      
      convertedCount++;
    });
    
    if (convertedCount > 0) {
      console.log(`[Icons] ✓ Инициализировано ${convertedCount} иконок`);
    } else {
      console.warn('[Icons] ⚠ Не найдено иконок для инициализации');
    }
  }

  // Запускаем при загрузке DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeIcons);
  } else {
    // DOM уже загружен
    initializeIcons();
  }

  // Экспортируем функцию для переинициализации при динамическом добавлении элементов
  window.reinitializeIcons = initializeIcons;

})();
