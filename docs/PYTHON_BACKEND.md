# Python Backend Documentation

## Обзор
Проект был успешно мигрирован с Node.js + TypeScript на Python + FastAPI. Новый backend предоставляет те же функции, что и оригинальный, но с улучшенной производительностью и асинхронной обработкой.

## Архитектура

### Основные компоненты
- **main.py** - Главное приложение FastAPI с маршрутами API
- **core/exchange.py** - Асинхронный менеджер биржи KuCoin
- **core/bot.py** - Логика торгового бота
- **core/risk_manager.py** - Управление рисками
- **services/ml_service.py** - Клиент ML сервиса
- **strategies/ema_strategy.py** - EMA торговая стратегия

### Зависимости
- FastAPI - веб-фреймворк
- Uvicorn - ASGI сервер
- CCXT - библиотека для работы с криптобиржами
- Socket.IO - WebSocket коммуникация
- SlowAPI - rate limiting
- Loguru - логирование

## API Маршруты

### Health Check
- **GET** `/health` - Проверка работоспособности сервера

### Статус
- **GET** `/api/status` - Получение статуса бота

### Рынок
- **GET** `/api/market` - Получение рыночных данных

### Торговля
- **POST** `/api/trade/start` - Запуск торговли
- **POST** `/api/trade/stop` - Остановка торговли
- **POST** `/api/trade/bot/start` - Запуск бота
- **POST** `/api/trade/bot/stop` - Полная остановка бота

### Настройки
- **GET** `/api/settings` - Получение настроек
- **PUT** `/api/settings` - Обновление настроек

## WebSocket
Сервер поддерживает WebSocket соединения через Socket.IO для реального времени обновлений статуса и рыночных данных.

## Запуск

### Локальный запуск
```bash
cd backend_py
pip install -r requirements.txt
python main.py
```

### Переменные окружения
- `KUCOIN_API_KEY` - API ключ KuCoin
- `KUCOIN_API_SECRET` - API секрет KuCoin
- `KUCOIN_API_PASSPHRASE` - API пароль KuCoin
- `KUCOIN_TESTNET` - Использовать тестовую сеть (true/false)
- `PORT` - Порт сервера (по умолчанию 3000)

## Тестирование
```bash
python test_api.py
```

## Развертывание
Backend настроен для развертывания на Railway с командой:
```bash
cd backend_py && python main.py
```

## Совместимость
Новый Python backend полностью совместим с существующим фронтендом и поддерживает все те же API endpoints и WebSocket события.