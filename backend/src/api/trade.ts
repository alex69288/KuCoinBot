import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';
import { tradingBot } from '../index';

const router = Router();

// POST /api/trade/start - запустить торговлю
router.post('/start', async (req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(400).json({ 
        success: false, 
        error: 'Bot not initialized (missing API credentials)' 
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
router.post('/stop', async (req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(400).json({ 
        success: false, 
        error: 'Bot not initialized' 
      });
    }

    tradingBot.disableTrading();
    logger.info('⚠️ Trading stopped');
    
    res.json({ success: true, message: 'Trading stopped' });
  } catch (error) {
    logger.error('Failed to stop trading:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to stop trading' 
    });
  }
});

// POST /api/trade/bot/start - запустить бота (но не торговлю)
router.post('/bot/start', async (req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(400).json({ 
        success: false, 
        error: 'Bot not initialized' 
      });
    }

    await tradingBot.start();
    logger.info('🚀 Bot started');
    
    res.json({ success: true, message: 'Bot started (trading disabled)' });
  } catch (error) {
    logger.error('Failed to start bot:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to start bot' 
    });
  }
});

// POST /api/trade/bot/stop - остановить бота полностью
router.post('/bot/stop', async (req: Request, res: Response) => {
  try {
    if (!tradingBot) {
      return res.status(400).json({ 
        success: false, 
        error: 'Bot not initialized' 
      });
    }

    tradingBot.stop();
    logger.info('🛑 Bot stopped');
    
    res.json({ success: true, message: 'Bot stopped completely' });
  } catch (error) {
    logger.error('Failed to stop bot:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to stop bot' 
    });
  }
});

export default router;
