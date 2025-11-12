/**
 * Оптимизированный менеджер производительности WebApp
 * v0.1.9 - Критичные улучшения загрузки и синхронизации данных
 * 
 * Основные улучшения:
 * 1. Ранний запуск WebSocket (до загрузки UI)
 * 2. Адаптивный fallback интервал (60 сек вместо 10)
 * 3. Приоритизированная загрузка данных
 * 4. IndexedDB кэширование для снижения запросов
 * 5. Отключение polling когда WebSocket активен
 */

class PerformanceOptimizer {
  constructor() {
    this.webSocketHealthy = false;
    this.webSocketHealthCheckInterval = null;
    this.fallbackInterval = null;
    this.requestQueue = [];
    this.isProcessingQueue = false;
    this.lastRequestTime = {};
    this.metrics = {
      websocketConnectionTime: null,
      firstDataLoadTime: null,
      initialLoadComplete: false
    };
  }

  /**
   * Инициализирует оптимизированную загрузку
   * Вызывается в самом начале загрузки страницы
   */
  async init() {
    console.log('[Perf] 🚀 Инициализация оптимизированной загрузки');

    // 1️⃣ Параллельно запускаем WebSocket и критичные данные
    await Promise.race([
      this.startWebSocketEarly(),
      new Promise(r => setTimeout(r, 3000)) // timeout 3 сек
    ]);

    // 2️⃣ Загружаем критичные данные
    await this.loadCriticalDataOnly();

    // 3️⃣ Запускаем здоровье-чек WebSocket
    this.startWebSocketHealthCheck();

    // 4️⃣ Загружаем остальное в фоне
    this.loadNonCriticalData();

    console.log('[Perf] ✅ Инициализация завершена');
  }

  /**
   * Запускает WebSocket подключение ЭТО РАНЬШЕ всего
   * Не ждем загрузки UI элементов
   */
  async startWebSocketEarly() {
    console.log('[Perf] 🌐 Начинаю подключение WebSocket (ранний старт)');
    const startTime = Date.now();

    return new Promise((resolve) => {
      // Подключаемся к WebSocket
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        const connectionTime = Date.now() - startTime;
        this.metrics.websocketConnectionTime = connectionTime;
        this.webSocketHealthy = true;
        console.log(`[Perf] ✅ WebSocket подключен за ${connectionTime}мс`);
        resolve(true);
      };

      ws.onerror = () => {
        console.warn('[Perf] ⚠️ WebSocket ошибка при раннем подключении');
        this.webSocketHealthy = false;
        resolve(false);
      };

      ws.onclose = () => {
        this.webSocketHealthy = false;
        console.log('[Perf] ⚠️ WebSocket закрыт');
      };

      ws.onmessage = (event) => {
        // Обработка сообщений из WebSocket
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketData(data);
        } catch (e) {
          console.error('[Perf] Ошибка парсинга WebSocket:', e);
        }
      };

      // Сохраняем глобальную ссылку
      window.wsConnection = ws;
    });
  }

  /**
   * Проверяет здоровье WebSocket и управляет fallback polling
   */
  startWebSocketHealthCheck() {
    console.log('[Perf] 💓 Запускаю проверку здоровья WebSocket');

    this.webSocketHealthCheckInterval = setInterval(() => {
      const isHealthy = window.wsConnection &&
        window.wsConnection.readyState === WebSocket.OPEN;

      if (isHealthy && !this.webSocketHealthy) {
        // WebSocket восстановился - отключаем polling
        console.log('[Perf] ✅ WebSocket восстановлен - отключаю HTTP polling');
        this.webSocketHealthy = true;
        this.stopFallbackUpdates();
      } else if (!isHealthy && this.webSocketHealthy) {
        // WebSocket упал - включаем медленный polling
        console.log('[Perf] ⚠️ WebSocket потерян - включаю медленный HTTP polling');
        this.webSocketHealthy = false;
        this.startSlowFallbackUpdates();
      }
    }, 5000); // Проверка каждые 5 сек
  }

  /**
   * Загружает ТОЛЬКО критичные данные (рынок, статус)
   * Остальное загружается потом в фоне
   */
  async loadCriticalDataOnly() {
    console.log('[Perf] 📊 Загрузка критичных данных');
    const startTime = Date.now();

    try {
      await Promise.all([
        this.loadDataWithCache('status', () => this.fetchStatus()),
        this.loadDataWithCache('market', () => this.fetchMarket())
      ]);

      this.metrics.firstDataLoadTime = Date.now() - startTime;
      console.log(`[Perf] ✅ Критичные данные загружены за ${this.metrics.firstDataLoadTime}мс`);
    } catch (e) {
      console.error('[Perf] Ошибка загрузки критичных данных:', e);
    }
  }

  /**
   * Загружает оставшиеся данные с задержкой
   */
  async loadNonCriticalData() {
    console.log('[Perf] 📋 Загрузка остальных данных в фоне');

    // Загружаем с задержкой 300мс, чтобы не блокировать UI
    await new Promise(resolve => setTimeout(resolve, 300));

    // Загружаем по одному с интервалом
    const tasks = [
      { name: 'positions', fn: () => this.fetchPositions() },
      { name: 'history', fn: () => this.fetchTradeHistory() },
      { name: 'settings', fn: () => this.fetchSettings() },
      { name: 'analytics', fn: () => this.fetchAnalytics() }
    ];

    for (const task of tasks) {
      await this.loadDataWithCache(task.name, task.fn);
      // Интервал между загрузками - не перегружаем сервер
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    console.log('[Perf] ✅ Все данные загружены');
  }

  /**
   * Медленный HTTP polling (только когда WebSocket мёртв)
   * Интервал: 60 сек вместо 10 сек (в 6 раз реже!)
   */
  startSlowFallbackUpdates() {
    if (this.fallbackInterval) return;

    console.log('[Perf] 🔄 Включаю медленный HTTP polling (60 сек)');

    this.fallbackInterval = setInterval(async () => {
      if (this.webSocketHealthy) {
        // WebSocket вернулся - отключаем polling
        this.stopFallbackUpdates();
        return;
      }

      // Обновляем только самые критичные данные
      console.log('[Perf] 📡 HTTP Fallback update');
      try {
        await Promise.all([
          this.loadDataWithCache('status', () => this.fetchStatus()),
          this.loadDataWithCache('market', () => this.fetchMarket())
        ]);
      } catch (e) {
        console.error('[Perf] HTTP Fallback ошибка:', e);
      }
    }, 60000); // ← ГЛАВНОЕ УЛУЧШЕНИЕ: 60 сек вместо 10 сек
  }

  /**
   * Отключает HTTP polling
   */
  stopFallbackUpdates() {
    if (this.fallbackInterval) {
      clearInterval(this.fallbackInterval);
      this.fallbackInterval = null;
      console.log('[Perf] ⏹️ HTTP polling отключен');
    }
  }

  /**
   * Загружает данные с кэшированием (IndexedDB)
   */
  async loadDataWithCache(cacheKey, fetchFn) {
    try {
      // Пытаемся получить из кэша
      const cached = await this.getFromCache(cacheKey);
      if (cached && !this.shouldRefreshCache(cacheKey)) {
        console.log(`[Perf] 📦 ${cacheKey} из кэша (${cached.age}мс)`);
        return cached.data;
      }

      // Загружаем с сервера
      const startTime = Date.now();
      const data = await fetchFn();
      const loadTime = Date.now() - startTime;

      // Сохраняем в кэш
      await this.setToCache(cacheKey, data);

      console.log(`[Perf] 🌐 ${cacheKey} загружено за ${loadTime}мс`);
      return data;
    } catch (e) {
      // Если ошибка - пытаемся вернуть из кэша
      const cached = await this.getFromCache(cacheKey);
      if (cached) {
        console.warn(`[Perf] ⚠️ ${cacheKey} ошибка, использую кэш`);
        return cached.data;
      }
      throw e;
    }
  }

  /**
   * Получить из IndexedDB кэша
   */
  async getFromCache(key) {
    try {
      const db = await this.openDB();
      const tx = db.transaction('cache', 'readonly');
      const store = tx.objectStore('cache');

      return new Promise((resolve) => {
        const req = store.get(key);
        req.onsuccess = () => {
          const item = req.result;
          if (item) {
            resolve({
              data: item.data,
              age: Date.now() - item.timestamp
            });
          } else {
            resolve(null);
          }
        };
        req.onerror = () => resolve(null);
      });
    } catch (e) {
      console.warn(`[Perf] Ошибка получения кэша ${key}:`, e);
      return null;
    }
  }

  /**
   * Сохранить в IndexedDB кэш
   */
  async setToCache(key, data) {
    try {
      const db = await this.openDB();
      const tx = db.transaction('cache', 'readwrite');
      const store = tx.objectStore('cache');

      return new Promise((resolve) => {
        const req = store.put({
          key,
          data,
          timestamp: Date.now()
        });
        req.onsuccess = () => resolve();
        req.onerror = () => resolve();
      });
    } catch (e) {
      console.warn(`[Perf] Ошибка сохранения кэша ${key}:`, e);
    }
  }

  /**
   * Проверить, нужно ли обновить кэш
   */
  shouldRefreshCache(key) {
    const refreshIntervals = {
      status: 30000,      // 30 сек
      market: 30000,      // 30 сек
      positions: 60000,   // 1 мин
      settings: 300000,   // 5 мин
      history: 300000,    // 5 мин
      analytics: 600000   // 10 мин
    };

    const lastUpdate = this.lastRequestTime[key] || 0;
    const interval = refreshIntervals[key] || 60000;

    return Date.now() - lastUpdate > interval;
  }

  /**
   * Открыть IndexedDB базу данных
   */
  openDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open('KuCoinBotDB', 1);

      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains('cache')) {
          db.createObjectStore('cache', { keyPath: 'key' });
        }
      };

      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  /**
   * Обработка данных из WebSocket
   */
  handleWebSocketData(data) {
    if (data.type === 'market_update') {
      // Обновляем рынок
      this.updateMarketDisplay(data.market);
    } else if (data.type === 'position_update') {
      // Обновляем позиции
      this.updatePositionsDisplay(data.positions);
    } else if (data.type === 'status_update') {
      // Обновляем статус
      this.updateStatusDisplay(data.status);
    }
  }

  // ========== API МЕТОДЫ ==========

  async fetchStatus() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const res = await fetch(`/api/status?init_data=${encodeURIComponent(initData)}&compact=1`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async fetchMarket() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const res = await fetch(`/api/market?init_data=${encodeURIComponent(initData)}&compact=1`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async fetchPositions() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const res = await fetch(`/api/positions?init_data=${encodeURIComponent(initData)}&compact=1`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async fetchTradeHistory() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const res = await fetch(`/api/trade-history?init_data=${encodeURIComponent(initData)}&limit=20&compact=1`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async fetchSettings() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const res = await fetch(`/api/settings?init_data=${encodeURIComponent(initData)}&compact=1`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async fetchAnalytics() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const res = await fetch(`/api/analytics?init_data=${encodeURIComponent(initData)}&compact=1`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  // ========== UI ОБНОВЛЕНИЕ (заглушки) ==========

  updateMarketDisplay(market) {
    console.log('[Perf] 📊 Обновление рынка:', market);
    // Вызывается существующей функцией updateMarketData()
  }

  updatePositionsDisplay(positions) {
    console.log('[Perf] 📍 Обновление позиций:', positions);
  }

  updateStatusDisplay(status) {
    console.log('[Perf] ✅ Обновление статуса:', status);
  }

  /**
   * Получить метрики производительности
   */
  getMetrics() {
    return {
      ...this.metrics,
      wsHealthy: this.webSocketHealthy,
      fallbackActive: this.fallbackInterval !== null
    };
  }

  /**
   * Вывести метрики в консоль
   */
  logMetrics() {
    console.log('[Perf] 📈 Метрики производительности:');
    console.table(this.getMetrics());
  }
}

// ========== ЭКСПОРТ ==========
window.perfOptimizer = new PerformanceOptimizer();

// Инициализация при загрузке страницы
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('[Perf] DOM загружен - инициализирую оптимизацию');
    window.perfOptimizer.init().catch(e => {
      console.error('[Perf] Ошибка инициализации:', e);
    });
  });
} else {
  // DOM уже загружен
  console.log('[Perf] DOM уже загружен - инициализирую оптимизацию');
  window.perfOptimizer.init().catch(e => {
    console.error('[Perf] Ошибка инициализации:', e);
  });
}

// Через 5 сек выводим метрики в консоль
setTimeout(() => {
  window.perfOptimizer.logMetrics();
}, 5000);
