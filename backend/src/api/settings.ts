import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';

const router = Router();

// GET /api/settings - получить настройки
router.get('/', async (_req: Request, res: Response) => {
  try {
    // TODO: Получить реальные настройки
    const settings = {
      strategy: 'ema_ml',
      riskLevel: 'medium',
      maxPositionSize: 100,
      stopLoss: 2,
      takeProfit: 5,
      mlEnabled: true
    };

    return res.json(settings);
  } catch (error) {
    logger.error('Failed to get settings:', error);
    return res.status(500).json({ error: 'Failed to get settings' });
  }
});

// PUT /api/settings - обновить настройки
router.put('/', async (req: Request, res: Response) => {
  try {
    const settings = req.body;
    // TODO: Сохранить настройки
    logger.info('Settings updated:', settings);
    res.json({ success: true, settings });
  } catch (error) {
    logger.error('Failed to update settings:', error);
    res.status(500).json({ error: 'Failed to update settings' });
  }
});

export default router;
