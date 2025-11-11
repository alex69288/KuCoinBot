# WebApp API Документация

## Обзор

Полное REST API для управления торговым ботом через веб-интерфейс.

## Базовый URL

```
http://localhost:8000  # Локальная разработка
https://your-domain.com  # Продакшн
```

## Аутентификация

Все защищенные endpoints требуют параметр `init_data` от Telegram WebApp для авторизации.

---

## Endpoints

### 🏥 Здоровье и статус

#### `GET /ping`
Простейший тест доступности сервера.

**Ответ:**
```json
{
  "status": "pong",
  "message": "Server is running!"
}
```

#### `GET /api/health`
Проверка работоспособности API и доступности бота.

**Ответ:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-11T12:00:00",
  "bot_available": true
}
```

#### `GET /api/debug/paths`
Отладочная информация о путях и директориях.

---

### 📊 Статус бота

#### `GET /api/status`
Получить полный статус бота.

**Параметры:**
- `init_data` (required) - Telegram WebApp init data

**Ответ:**
```json
{
  "trading_enabled": true,
  "balance": {
    "USDT": 100.5,
    "total_usdt": 150.75
  },
  "current_position": {
    "status": "long",
    "entry_price": 42000.50,
    "amount": 0.001,
    "pnl": 5.25
  },
  "settings": {
    "active_pair": "BTC/USDT",
    "active_strategy": "ema_ml",
    "trade_amount_percent": 0.01
  }
}
```

---

### ⚙️ Настройки

#### `GET /api/settings`
Получить все настройки бота.

**Параметры:**
- `init_data` (required)

**Ответ:**
```json
{
  "active_pair": "BTC/USDT",
  "active_strategy": "ema_ml",
  "trade_amount_percent": 0.01,
  "strategy_settings": {
    "ema_ml": {
      "ema_fast_period": 9,
      "ema_slow_period": 21,
      "ema_threshold": 0.0025,
      "take_profit_percent": 2.0,
      "stop_loss_percent": 1.5
    }
  },
  "risk_settings": {
    "max_position_size": 100,
    "max_daily_loss": 10
  }
}
```

#### `POST /api/settings/trading`
Обновить торговые настройки.

**Body:**
```json
{
  "init_data": "...",
  "settings": {
    "active_pair": "BTC/USDT",
    "active_strategy": "ema_ml",
    "trade_amount_percent": 0.01
  }
}
```

#### `POST /api/settings/ema`
Обновить настройки EMA.

**Body:**
```json
{
  "init_data": "...",
  "settings": {
    "ema_fast_period": 9,
    "ema_slow_period": 21,
    "ema_threshold": 0.0025
  }
}
```

#### `POST /api/settings/risk`
Обновить настройки риск-менеджмента.

**Body:**
```json
{
  "init_data": "...",
  "settings": {
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.5,
    "max_position_size": 100,
    "max_daily_loss": 10
  }
}
```

#### `POST /api/settings/ml`
Обновить ML настройки.

**Body:**
```json
{
  "init_data": "...",
  "settings": {
    "ml_enabled": true,
    "ml_buy_threshold": 0.7,
    "ml_sell_threshold": 0.3
  }
}
```

#### `POST /api/settings/general`
Обновить общие настройки.

**Body:**
```json
{
  "init_data": "...",
  "settings": {
    "trading_enabled": true,
    "demo_mode": false,
    "enable_price_updates": true,
    "trailing_stop": false
  }
}
```

---

### 🎮 Управление ботом

#### `POST /api/start`
Запустить бота.

**Body:**
```json
{
  "init_data": "..."
}
```

**Ответ:**
```json
{
  "status": "success",
  "message": "Бот запущен"
}
```

#### `POST /api/stop`
Остановить бота.

**Body:**
```json
{
  "init_data": "..."
}
```

---

### 📈 Позиции

#### `GET /api/positions`
Получить открытые позиции.

**Параметры:**
- `init_data` (required)

**Ответ:**
```json
[
  {
    "id": "current_position",
    "pair": "BTC/USDT",
    "status": "long",
    "entry_price": 42000.50,
    "current_price": 42500.00,
    "amount": 0.001,
    "pnl": 5.25,
    "timestamp": "2025-11-11T12:00:00"
  }
]
```

#### `POST /api/position/{position_id}/close`
Закрыть позицию вручную.

**Body:**
```json
{
  "init_data": "..."
}
```

---

### 📜 История сделок

#### `GET /api/trade-history`
Получить историю сделок.

**Параметры:**
- `init_data` (required)
- `limit` (optional, default=10, max=50)

**Ответ:**
```json
[
  {
    "pair": "BTC/USDT",
    "type": "long",
    "entry_price": 41500.00,
    "exit_price": 42000.00,
    "amount": 0.001,
    "pnl": 5.0,
    "timestamp": "2025-11-11T10:00:00"
  }
]
```

---

### 📊 Аналитика

#### `GET /api/analytics`
Получить статистику торговли.

**Параметры:**
- `init_data` (required)

**Ответ:**
```json
{
  "total_trades": 100,
  "winning_trades": 65,
  "losing_trades": 35,
  "win_rate": 65.0,
  "total_profit": 125.50,
  "avg_profit": 1.26,
  "avg_win": 3.50,
  "avg_loss": -2.10,
  "max_win": 15.00,
  "max_loss": -8.50,
  "timestamp": "2025-11-11T12:00:00"
}
```

#### `POST /api/analytics/reset`
Сбросить статистику.

**Body:**
```json
{
  "init_data": "..."
}
```

---

### 🤖 Machine Learning

#### `POST /api/ml/retrain`
Переобучить ML модель.

**Body:**
```json
{
  "init_data": "..."
}
```

**Ответ:**
```json
{
  "status": "success",
  "message": "ML модель успешно переобучена"
}
```

---

## Коды ошибок

- `200` - Успешный запрос
- `401` - Неавторизован (неверный init_data)
- `404` - Endpoint не найден
- `500` - Внутренняя ошибка сервера
- `503` - Бот не инициализирован

## Примеры использования

### JavaScript (Frontend)

```javascript
// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
const initData = tg.initData;

// Получить статус бота
async function getBotStatus() {
  const response = await fetch(`/api/status?init_data=${encodeURIComponent(initData)}`);
  const data = await response.json();
  return data;
}

// Запустить бота
async function startBot() {
  const response = await fetch('/api/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ init_data: initData })
  });
  return await response.json();
}

// Обновить настройки
async function updateSettings(settings) {
  const response = await fetch('/api/settings/trading', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      init_data: initData,
      settings: settings
    })
  });
  return await response.json();
}
```

### Python (Backend тесты)

```python
import requests

BASE_URL = "http://localhost:8000"
INIT_DATA = "your_init_data"

# Получить статус
response = requests.get(
    f"{BASE_URL}/api/status",
    params={"init_data": INIT_DATA}
)
print(response.json())

# Запустить бота
response = requests.post(
    f"{BASE_URL}/api/start",
    json={"init_data": INIT_DATA}
)
print(response.json())
```

---

## Безопасность

- Все защищенные endpoints проверяют подлинность `init_data` от Telegram
- Используется HMAC-SHA256 для валидации данных
- HTTPS обязателен для продакшн использования
- Локальные URL (http://localhost) не работают с Telegram WebApp

---

## Развертывание

### Локальная разработка

```bash
# Запуск сервера
python webapp/server.py

# Сервер будет доступен на http://localhost:8000
```

### Продакшн (Amvera)

```bash
# Установить WEBAPP_URL в .env
WEBAPP_URL=https://your-domain.amvera.io

# Деплой через Git
git push amvera main
```

---

## Лимиты и ограничения

- Максимум 50 записей в истории сделок за один запрос
- Таймаут запроса: 30 секунд
- Rate limiting: не реализован (TODO)

---

## Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь, что бот инициализирован
3. Проверьте корректность init_data
4. Используйте `/api/debug/paths` для диагностики

---

*Документация обновлена: 11 ноября 2025 г.*
