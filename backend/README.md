# KuCoin Bot - Backend

Backend API для торгового бота на Node.js + TypeScript + Express.

## 🚀 Быстрый Старт

### 1. Установка зависимостей

```bash
cd backend
npm install
```

### 2. Настройка окружения

Скопируйте `.env.example` в `.env` и заполните переменные:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:
- `KUCOIN_API_KEY` - ваш API ключ
- `KUCOIN_API_SECRET` - ваш API секрет
- `KUCOIN_API_PASSPHRASE` - ваша passphrase
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- И т.д.

### 3. Запуск

**Development режим** (с hot reload):
```bash
npm run dev
```

**Production build**:
```bash
npm run build
npm start
```

**Тесты**:
```bash
npm test
```

## 📁 Структура Проекта

```
backend/
├── src/
│   ├── api/                # REST API endpoints
│   │   ├── status.ts       # GET /api/status
│   │   ├── market.ts       # GET /api/market
│   │   ├── trade.ts        # POST /api/trade/start|stop
│   │   ├── settings.ts     # GET|PUT /api/settings
│   │   └── routes.ts       # Главный роутер
│   ├── core/               # Основная логика бота
│   │   ├── bot.ts          # Главный класс бота
│   │   ├── exchange.ts     # CCXT обертка
│   │   └── riskManager.ts  # Управление рисками
│   ├── strategies/         # Торговые стратегии
│   ├── services/           # Сервисы (Telegram, ML API)
│   ├── middleware/         # Express middleware
│   │   └── errorHandler.ts
│   ├── utils/              # Утилиты
│   │   └── logger.ts       # Winston logger
│   ├── types/              # TypeScript типы
│   └── index.ts            # Точка входа
├── logs/                   # Логи (создается автоматически)
├── dist/                   # Скомпилированный код
├── tests/                  # Тесты
├── package.json
├── tsconfig.json
└── .env
```

## 🔌 API Endpoints

### Health Check
```
GET /health
Response: { status: 'ok', timestamp: '...' }
```

### Status
```
GET /api/status
Response: {
  isRunning: boolean,
  tradingEnabled: boolean,
  balance: { ... },
  positions: { ... },
  uptime: number
}
```

### Market Data
```
GET /api/market
Response: {
  symbol: string,
  price: number,
  change24h: number,
  volume: number,
  ...
}
```

### Trading Control
```
POST /api/trade/start
Response: { success: true, message: '...' }

POST /api/trade/stop
Response: { success: true, message: '...' }
```

### Settings
```
GET /api/settings
Response: { strategy: '...', riskLevel: '...', ... }

PUT /api/settings
Body: { strategy: '...', ... }
Response: { success: true, settings: { ... } }
```

## 🔧 Скрипты

- `npm run dev` - Запуск в development режиме с hot reload
- `npm run build` - Сборка TypeScript в JavaScript
- `npm start` - Запуск production версии
- `npm test` - Запуск тестов
- `npm run test:watch` - Тесты в watch режиме
- `npm run lint` - Проверка кода ESLint
- `npm run format` - Форматирование кода Prettier

## 📝 TODO

- [ ] Интегрировать CCXT для KuCoin API
- [ ] Реализовать торговые стратегии
- [ ] Подключить ML микросервис
- [ ] Добавить Telegram bot интеграцию
- [ ] Настроить WebSocket для real-time обновлений
- [ ] Добавить Redis для кеширования
- [ ] Написать тесты
- [ ] Добавить Docker support

## 🐛 Troubleshooting

### Порт занят
Если порт 3000 занят, измените `PORT` в `.env` файле.

### Ошибки TypeScript
Убедитесь что все зависимости установлены: `npm install`

### Проблемы с логами
Папка `logs/` создается автоматически при первом запуске.
