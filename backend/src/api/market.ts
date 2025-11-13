import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';
import { tradingBot } from '../index';

const router = Router();

// GET /api/market - получить рыночные данные
router.get('/', async (_req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      // Mock данные если бот не инициализирован
      return res.json({
        symbol: 'BTC/USDT',
        price: 45000,
        change24h: 0,
        changePercent24h: 0,
        volume: 0,
        volume24h: 0,
        high24h: 45000,
        low24h: 45000,
        timestamp: new Date().toISOString(),
        error: 'Bot not initialized (missing API credentials)'
      });
    }

    // Получаем реальные рыночные данные через бота
    const marketData = await tradingBot.getMarketData();
    return res.json(marketData);
  } catch (error) {
    logger.error('Failed to get market data:', error);
    return res.status(500).json({ error: 'Failed to get market data' });
  }
});

export default router;
