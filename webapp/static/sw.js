/**
 * Service Worker для KuCoin Trading Bot Web App
 * Обеспечивает кэширование ресурсов и работу в офлайн-режиме
 */

const CACHE_NAME = 'kucoin-bot-v1.0.0';
const RUNTIME_CACHE = 'kucoin-bot-runtime';

// Критичные ресурсы для кэширования
const PRECACHE_URLS = [
  '/static/',
  '/static/index.html',
  '/static/icons.css',
  'https://telegram.org/js/telegram-web-app.js'
];

// Установка Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Установка Service Worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Кэширование критичных ресурсов');
        return cache.addAll(PRECACHE_URLS.map(url => new Request(url, { cache: 'reload' })));
      })
      .then(() => self.skipWaiting())
      .catch(err => console.error('[SW] Ошибка при кэшировании:', err))
  );
});

// Активация Service Worker
self.addEventListener('activate', event => {
  console.log('[SW] Активация Service Worker...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          // Удаляем старые кэши
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('[SW] Удаление старого кэша:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Обработка запросов
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Игнорируем не-GET запросы
  if (request.method !== 'GET') {
    return;
  }

  // Игнорируем WebSocket и API запросы для реального времени
  if (url.protocol === 'ws:' || url.protocol === 'wss:' || url.pathname.startsWith('/api/')) {
    return;
  }

  // Стратегия: Network First для HTML (всегда свежий контент)
  if (request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Кэшируем успешный ответ
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // При ошибке сети возвращаем из кэша
          return caches.match(request);
        })
    );
    return;
  }

  // Стратегия: Cache First для статических ресурсов (CSS, JS, изображения)
  if (url.pathname.includes('/static/') || url.hostname === 'telegram.org') {
    event.respondWith(
      caches.match(request)
        .then(cachedResponse => {
          if (cachedResponse) {
            // Возвращаем из кэша и обновляем в фоне
            fetch(request)
              .then(response => {
                if (response.ok) {
                  caches.open(CACHE_NAME).then(cache => {
                    cache.put(request, response);
                  });
                }
              })
              .catch(() => { });
            return cachedResponse;
          }

          // Если в кэше нет, запрашиваем из сети
          return fetch(request)
            .then(response => {
              // Кэшируем успешный ответ
              if (response.ok) {
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                  cache.put(request, responseClone);
                });
              }
              return response;
            });
        })
    );
    return;
  }

  // Для остальных запросов - стандартная стратегия
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});

// Обработка сообщений от клиента
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
