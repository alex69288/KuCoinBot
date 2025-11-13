import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import { logger } from './utils/logger';
import { errorHandler } from './middleware/errorHandler';
import apiRoutes from './api/routes';
import { ExchangeManager } from './core/exchange';
import { TradingBot } from './core/bot';

// Загружаем переменные окружения
dotenv.config();

// Инициализация Exchange и Bot
let exchange: ExchangeManager | null = null;
let tradingBot: TradingBot | null = null;

try {
  const apiKey = process.env.KUCOIN_API_KEY || '';
  const apiSecret = process.env.KUCOIN_API_SECRET || '';
  const apiPassphrase = process.env.KUCOIN_API_PASSPHRASE || '';
  const testnet = process.env.KUCOIN_TESTNET === 'true';

  if (apiKey && apiSecret && apiPassphrase) {
    exchange = new ExchangeManager({
      apiKey,
      apiSecret,
      apiPassphrase,
      testnet
    });

    tradingBot = new TradingBot(exchange, {
      symbol: process.env.TRADING_SYMBOL || 'BTC/USDT',
      timeframe: process.env.TRADING_TIMEFRAME || '1h',
      tradingEnabled: false, // Всегда начинаем с отключенной торговлей
      strategy: 'ema_ml'
    });

    logger.info('✅ Exchange and Trading Bot initialized');
  } else {
    logger.warn('⚠️ KuCoin credentials not found, running in mock mode');
  }
} catch (error) {
  logger.error('Failed to initialize Exchange/Bot:', error);
}

// Экспортируем для использования в routes
export { tradingBot, exchange };

const app: Express = express();
const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:5173',
    methods: ['GET', 'POST']
  }
});

const PORT = process.env.PORT || 3000;
const WS_PORT = process.env.WS_PORT || 3001;

// Middleware
app.use(helmet()); // Безопасность
app.use(cors()); // CORS
app.use(compression()); // Сжатие ответов
app.use(express.json()); // Парсинг JSON
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000'),
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api', apiRoutes);

// WebSocket connection
io.on('connection', (socket) => {
  logger.info(`WebSocket client connected: ${socket.id}`);

  // Отправляем начальный статус
  if (tradingBot) {
    tradingBot.getStatus().then(status => {
      socket.emit('status', status);
    }).catch(err => {
      logger.error('Failed to send initial status:', err);
    });
  }

  socket.on('disconnect', () => {
    logger.info(`WebSocket client disconnected: ${socket.id}`);
  });
});

// WebSocket broadcasting - отправка обновлений клиентам
function startWebSocketBroadcasting() {
  // Отправка статуса бота каждые 5 секунд
  setInterval(async () => {
    if (!tradingBot) return;

    try {
      const status = await tradingBot.getStatus();
      io.emit('status', status);
    } catch (error) {
      logger.error('Failed to broadcast status:', error);
    }
  }, 5000);

  // Отправка рыночных данных каждые 10 секунд
  setInterval(async () => {
    if (!tradingBot) return;

    try {
      const marketData = await tradingBot.getMarketData();
      io.emit('market', marketData);
    } catch (error) {
      logger.error('Failed to broadcast market data:', error);
    }
  }, 10000);

  logger.info('📡 WebSocket broadcasting started');
}

// Обработка ошибок (должен быть последним)
app.use(errorHandler);

// Запуск сервера
httpServer.listen(PORT, () => {
  logger.info(`🚀 Backend server started on port ${PORT}`);
  logger.info(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`📡 WebSocket ready on port ${PORT}`);

  // Запускаем WebSocket broadcasting
  startWebSocketBroadcasting();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  httpServer.close(() => {
    logger.info('HTTP server closed');
  });
});

export { app, io };
