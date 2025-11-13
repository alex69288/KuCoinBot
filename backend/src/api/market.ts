import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';

const router = Router();

// GET /api/market - получить рыночные данные
router.get('/', async (req: Request, res: Response) => {
  try {
    // TODO: Получить реальные рыночные данные через CCXT
    const marketData = {
      symbol: 'BTC/USDT',
      price: 45000,
      change24h: 2.5,
      volume: 1234567890,
      high24h: 46000,
      low24h: 44000,
      timestamp: new Date().toISOString()
    };

    res.json(marketData);
  } catch (error) {
    logger.error('Failed to get market data:', error);
    res.status(500).json({ error: 'Failed to get market data' });
  }
});

export default router;
