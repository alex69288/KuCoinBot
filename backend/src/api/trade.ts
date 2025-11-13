import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';
import { tradingBot } from '../index';

const router = Router();

// POST /api/trade/start - запустить торговлю
router.post('/start', async (req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      logger.warn('⚠️ Trading bot not available in mock mode');
      return res.status(200).json({
        success: false,
        message: 'Bot running in mock mode (no API credentials)',
        mockMode: true
      });
    }

    if (!tradingBot.isActive()) {
      await tradingBot.start();
    }

    tradingBot.enableTrading();
    logger.info('✅ Trading started');

    res.json({ success: true, message: 'Trading started' });
  } catch (error) {
    logger.error('Failed to start trading:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start trading'
    });
  }
});

// POST /api/trade/stop - остановить торговлю
router.post('/stop', async (_req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(200).json({
        success: false,
        message: 'Bot running in mock mode',
        mockMode: true
      });
    }

    tradingBot.disableTrading();
    logger.info('⚠️ Trading stopped');

    return res.json({ success: true, message: 'Trading stopped' });
  } catch (error) {
    logger.error('Failed to stop trading:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to stop trading'
    });
  }
});

// POST /api/trade/bot/start - запустить бота (но не торговлю)
router.post('/bot/start', async (_req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(200).json({
        success: false,
        message: 'Bot running in mock mode',
        mockMode: true
      });
    }

    await tradingBot.start();
    logger.info('🚀 Bot started');

    return res.json({ success: true, message: 'Bot started (trading disabled)' });
  } catch (error) {
    logger.error('Failed to start bot:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to start bot'
    });
  }
});

// POST /api/trade/bot/stop - остановить бота полностью
router.post('/bot/stop', async (_req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(200).json({
        success: false,
        message: 'Bot running in mock mode',
        mockMode: true
      });
    }

    tradingBot.stop();
    logger.info('🛑 Bot stopped');

    return res.json({ success: true, message: 'Bot stopped completely' });
  } catch (error) {
    logger.error('Failed to stop bot:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to stop bot'
    });
  }
});

export default router;
