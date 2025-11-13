# 🚀 Инструкция по запуску Trading Bot для тестирования

## Быстрый старт (без реальных API ключей)

Бот может работать в **mock-режиме** без подключения к бирже - для демонстрации интерфейса.

### 1. Запуск Backend:

```bash
cd backend
npm run dev
```

**Что происходит:**
- Запускается Express сервер на порту 3000
- Инициализируется Trading Bot в mock-режиме (без API ключей)
- WebSocket начинает broadcast каждые 5-10 секунд
- API доступен на `http://localhost:3000`

**Проверка:**
```bash
# В другом терминале:
curl http://localhost:3000/health
# Должно вернуть: {"status":"ok","timestamp":"..."}
```

### 2. Запуск Frontend:

```bash
cd frontend
npm run dev
```

**Открой в браузере:** `http://localhost:5173`

---

## Полноценное тестирование с KuCoin Testnet

### Шаг 1: Получи API ключи для Testnet

1. Зарегистрируйся на **KuCoin Testnet**: https://sandbox.kucoin.com
2. Перейди в **API Management** → **Create API**
3. Скопируй:
   - API Key
   - API Secret
   - API Passphrase

### Шаг 2: Настрой `.env` файл

Открой `backend/.env` и заполни:

```env
# KuCoin API Keys
KUCOIN_API_KEY=your_testnet_api_key
KUCOIN_API_SECRET=your_testnet_api_secret
KUCOIN_API_PASSPHRASE=your_testnet_passphrase
KUCOIN_TESTNET=true  # ВАЖНО: должно быть true для testnet

# Trading Settings
TRADING_SYMBOL=BTC/USDT
TRADING_TIMEFRAME=1h
```

### Шаг 3: Запусти Backend

```bash
cd backend
npm run dev
```

**Логи должны показать:**
```
✅ Exchange and Trading Bot initialized
🚀 Backend server started on port 3000
📡 WebSocket ready on port 3000
📡 WebSocket broadcasting started
```

### Шаг 4: Протестируй API

#### 1. Статус бота:
```bash
curl http://localhost:3000/api/status
```

Ответ:
```json
{
  "bot": {
    "isRunning": false,
    "tradingEnabled": false,
    "strategy": "ema_ml"
  },
  "exchange": {
    "connected": true,
    "testnet": true
  },
  "balance": {
    "total": 10000,
    "available": 10000,
    "used": 0
  }
}
```

#### 2. Рыночные данные:
```bash
curl http://localhost:3000/api/market
```

#### 3. Запуск бота:
```bash
curl -X POST http://localhost:3000/api/trade/start
```

Бот начнет торговый цикл каждые 30 секунд.

#### 4. Включение торговли:
```bash
curl -X POST http://localhost:3000/api/trade/enable
```

⚠️ **ВАЖНО:** Реальные ордера ОТКЛЮЧЕНЫ в коде. Бот будет только симулировать сделки.

#### 5. Остановка бота:
```bash
curl -X POST http://localhost:3000/api/trade/stop
```

---

## Тестирование через Frontend

### 1. Запусти Backend + Frontend:

```bash
# Терминал 1:
cd backend
npm run dev

# Терминал 2:
cd frontend
npm run dev
```

### 2. Открой браузер:
`http://localhost:5173`

### 3. Проверь WebSocket подключение:

Открой DevTools → Console. Должны появляться логи каждые 5-10 секунд:
```
WebSocket status update: {...}
WebSocket market update: {...}
```

### 4. Используй интерфейс:

- **Start Bot** - запускает торговый цикл
- **Stop Bot** - останавливает
- **Enable Trading** - включает открытие позиций
- **Disable Trading** - отключает (только мониторинг)

---

## Запуск ML Service (опционально)

ML Service добавляет предсказания к EMA сигналам.

### 1. Установи зависимости:

```bash
cd ml-service
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Запусти Flask сервер:

```bash
python app.py
```

Сервер запустится на `http://localhost:5000`

### 3. Проверь работу:

```bash
curl http://localhost:5000/health
# Ответ: {"status":"healthy","model_loaded":false}
```

**Примечание:** Модель ML не обучена, будет возвращать случайные предсказания. Для реальной работы нужно обучить RandomForest на исторических данных.

---

## Мониторинг логов

### Backend логи (Winston):

```bash
cd backend
tail -f logs/combined.log
# или
tail -f logs/error.log
```

### Что смотреть в логах:

```
✅ Успешный запуск:
🚀 Trading Bot started
Trading loop started (30s interval)

📊 Торговый цикл:
Trading cycle: BTC/USDT @ 43250.5
EMA Signal: BUY (confidence: 75.2%)
ML Signal: BUY (confidence: 68.5%)

🔷 Открытие позиции:
Opening LONG position:
   Amount: 0.023150 BTC
   Size: $1000.00
   Stop Loss: $42405.49
   Take Profit: $45412.03
✅ Position opened successfully

🔶 Закрытие позиции:
Closing LONG position:
   Profit: $125.50 (2.51%)
   Reason: Take Profit hit
✅ Position closed successfully
```

---

## Проверка работы компонентов

### ✅ Exchange Manager:
```bash
curl http://localhost:3000/api/market
```
Должны вернуться реальные цены с KuCoin.

### ✅ Risk Manager:
Проверь логи при попытке открыть позицию:
- Рассчитывается размер позиции (10% баланса)
- Устанавливается SL (-2%) и TP (+5%)
- Проверяются дневные лимиты

### ✅ Trading Cycle:
После `POST /api/trade/start` смотри логи каждые 30 секунд:
```
Trading cycle: BTC/USDT @ 43250.5
EMA Signal: HOLD (confidence: 45.0%)
```

### ✅ WebSocket:
Открой Frontend и смотри DevTools → Network → WS. Должны приходить сообщения `status` и `market`.

---

## Отключение реальной торговли

По умолчанию **реальные ордера ОТКЛЮЧЕНЫ**. В коде `bot.ts`:

```typescript
// ВАЖНО: В production здесь создается реальный ордер
// const order = await this.exchange.createMarketOrder(
//   this.config.symbol,
//   side,
//   tradeSize.amountInCurrency
// );
```

### Для включения реальных сделок:

1. Раскомментируй `createMarketOrder()` в методах:
   - `openPosition()`
   - `closePosition()`

2. Протестируй сначала на **testnet** с малыми суммами

3. Убедись в правильности Risk Manager настроек:
   ```typescript
   maxPositionPercent: 10,  // Не более 10% на сделку
   stopLossPercent: 2,      // SL -2%
   takeProfitPercent: 5,    // TP +5%
   maxDailyTrades: 10       // Макс 10 сделок в день
   ```

---

## Troubleshooting

### ❌ "Failed to connect to exchange"

**Причина:** Неверные API ключи или они не для testnet.

**Решение:**
1. Проверь `.env` файл
2. Убедись что `KUCOIN_TESTNET=true`
3. Ключи должны быть с https://sandbox.kucoin.com

### ❌ "ML Service not available"

**Причина:** ML Service не запущен.

**Решение:** Это нормально! Бот работает и без ML, используя только EMA Strategy.

Чтобы запустить ML:
```bash
cd ml-service
python app.py
```

### ❌ WebSocket не работает

**Причина:** Frontend не может подключиться к Backend.

**Решение:**
1. Проверь что Backend запущен на порту 3000
2. Проверь CORS в `backend/src/index.ts`
3. Проверь `FRONTEND_URL` в `.env`

### ❌ "Cannot trade: Daily limit reached"

**Причина:** Risk Manager ограничил торговлю (10 сделок в день).

**Решение:**
- Подожди до следующего дня (00:00 UTC)
- Или измени `maxDailyTrades` в `bot.ts`

---

## Следующие шаги

После успешного тестирования:

1. **Обучи ML модель** на исторических данных
2. **Настрой Risk Manager** под свою стратегию
3. **Протестируй на testnet** несколько дней
4. **Добавь Telegram уведомления** для мониторинга
5. **Деплой на сервер** (Amvera/Railway)

---

## Быстрые команды

```bash
# Запуск всего стека
cd backend && npm run dev
cd frontend && npm run dev
cd ml-service && python app.py

# Тесты
cd backend && npm test

# Логи
tail -f backend/logs/combined.log

# Статус бота
curl http://localhost:3000/api/status

# Запуск бота
curl -X POST http://localhost:3000/api/trade/start

# Включить торговлю
curl -X POST http://localhost:3000/api/trade/enable

# Остановить
curl -X POST http://localhost:3000/api/trade/stop
```

---

## 🎯 Готово к тестированию!

Запускай бота и смотри как он анализирует рынок каждые 30 секунд 🚀
