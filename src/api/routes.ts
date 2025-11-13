import { Router } from 'express';
import statusRoutes from './status';
import marketRoutes from './market';
import tradeRoutes from './trade';
import settingsRoutes from './settings';

const router = Router();

router.use('/status', statusRoutes);
router.use('/market', marketRoutes);
router.use('/trade', tradeRoutes);
router.use('/settings', settingsRoutes);

export default router;
