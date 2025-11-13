import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';

const router = Router();

// GET /api/status - получить статус бота
router.get('/', async (req: Request, res: Response) => {
  try {
    // TODO: Получить реальный статус от бота
    const status = {
      isRunning: true,
      tradingEnabled: false,
      balance: {
        total: 1000,
        available: 950,
        used: 50
      },
      positions: {
        current: null,
        total: 0,
        profit: 0
      },
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    };

    res.json(status);
  } catch (error) {
    logger.error('Failed to get status:', error);
    res.status(500).json({ error: 'Failed to get status' });
  }
});

export default router;
