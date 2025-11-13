import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';

const router = Router();

// POST /api/trade/start - запустить торговлю
router.post('/start', async (req: Request, res: Response) => {
  try {
    // TODO: Запустить бота
    logger.info('Trading started');
    res.json({ success: true, message: 'Trading started' });
  } catch (error) {
    logger.error('Failed to start trading:', error);
    res.status(500).json({ error: 'Failed to start trading' });
  }
});

// POST /api/trade/stop - остановить торговлю
router.post('/stop', async (req: Request, res: Response) => {
  try {
    // TODO: Остановить бота
    logger.info('Trading stopped');
    res.json({ success: true, message: 'Trading stopped' });
  } catch (error) {
    logger.error('Failed to stop trading:', error);
    res.status(500).json({ error: 'Failed to stop trading' });
  }
});

export default router;
