import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';
import { tradingBot } from '../index';

const router = Router();

// GET /api/status - получить статус бота
router.get('/', async (req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      // Если бот не инициализирован, возвращаем mock данные
      return res.json({
        isRunning: false,
        tradingEnabled: false,
        balance: {
          total: 0,
          available: 0,
          used: 0,
          currency: 'USDT'
        },
        positions: {
          current: null,
          total: 0,
          profit: 0
        },
        uptime: process.uptime(),
        timestamp: new Date().toISOString(),
        error: 'Bot not initialized (missing API credentials)'
      });
    }

    // Получаем реальный статус от бота
    const status = await tradingBot.getStatus();
    res.json(status);
  } catch (error) {
    logger.error('Failed to get status:', error);
    res.status(500).json({ error: 'Failed to get status' });
  }
});

export default router;
