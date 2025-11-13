import { ExchangeManager } from './exchange';
import { logger } from '../utils/logger';

export interface BotConfig {
  symbol: string;
  timeframe: string;
  tradingEnabled: boolean;
  strategy: 'ema_ml' | 'price_action' | 'macd_rsi' | 'bollinger';
}

export interface Position {
  symbol: string;
  side: 'long' | 'short';
  entryPrice: number;
  currentPrice: number;
  amount: number;
  profit: number;
  profitPercent: number;
  openTime: string;
}

export class TradingBot {
  private exchange: ExchangeManager;
  private config: BotConfig;
  private isRunning: boolean = false;
  private tradingEnabled: boolean = false;
  private currentPosition: Position | null = null;
  private startTime: number;

  constructor(exchange: ExchangeManager, config: BotConfig) {
    this.exchange = exchange;
    this.config = config;
    this.startTime = Date.now();
    
    logger.info('Trading Bot initialized');
    logger.info(`Symbol: ${config.symbol}`);
    logger.info(`Strategy: ${config.strategy}`);
  }

  /**
   * Запустить бота
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('Bot is already running');
      return;
    }

    try {
      // Проверяем подключение к бирже
      const connected = await this.exchange.connect();
      if (!connected) {
        throw new Error('Failed to connect to exchange');
      }

      this.isRunning = true;
      logger.info('🚀 Trading Bot started');
      
      // Запускаем основной цикл
      // this.runTradingLoop();
    } catch (error) {
      logger.error('Failed to start bot:', error);
      throw error;
    }
  }

  /**
   * Остановить бота
   */
  stop(): void {
    if (!this.isRunning) {
      logger.warn('Bot is not running');
      return;
    }

    this.isRunning = false;
    logger.info('🛑 Trading Bot stopped');
  }

  /**
   * Включить торговлю
   */
  enableTrading(): void {
    this.tradingEnabled = true;
    logger.info('✅ Trading enabled');
  }

  /**
   * Отключить торговлю
   */
  disableTrading(): void {
    this.tradingEnabled = false;
    logger.info('⚠️ Trading disabled');
  }

  /**
   * Получить статус бота
   */
  async getStatus(): Promise<any> {
    try {
      const balance = await this.exchange.getBalance('USDT');
      const uptime = Math.floor((Date.now() - this.startTime) / 1000);

      return {
        isRunning: this.isRunning,
        tradingEnabled: this.tradingEnabled,
        balance: {
          total: balance.total,
          available: balance.available,
          used: balance.used,
          currency: balance.currency
        },
        positions: {
          current: this.currentPosition,
          total: this.currentPosition ? 1 : 0,
          profit: this.currentPosition?.profit || 0
        },
        uptime,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      logger.error('Failed to get bot status:', error);
      throw error;
    }
  }

  /**
   * Получить рыночные данные
   */
  async getMarketData(): Promise<any> {
    try {
      return await this.exchange.getMarketData(this.config.symbol);
    } catch (error) {
      logger.error('Failed to get market data:', error);
      throw error;
    }
  }

  /**
   * Получить текущую позицию
   */
  getCurrentPosition(): Position | null {
    return this.currentPosition;
  }

  /**
   * Проверить, запущен ли бот
   */
  isActive(): boolean {
    return this.isRunning;
  }

  /**
   * Проверить, включена ли торговля
   */
  isTradingEnabled(): boolean {
    return this.tradingEnabled;
  }

  /**
   * Обновить конфигурацию
   */
  updateConfig(config: Partial<BotConfig>): void {
    this.config = { ...this.config, ...config };
    logger.info('Bot configuration updated:', config);
  }

  /**
   * Получить uptime в секундах
   */
  getUptime(): number {
    return Math.floor((Date.now() - this.startTime) / 1000);
  }
}
