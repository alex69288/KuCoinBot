import { ExchangeManager } from './exchange';
import { RiskManager } from './riskManager';
import { MLService } from '../services/mlService';
import { EMAStrategy } from '../strategies/EMAStrategy';
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
  stopLoss: number;
  takeProfit: number;
  openTime: string;
}

export class TradingBot {
  private exchange: ExchangeManager;
  private riskManager: RiskManager;
  private mlService: MLService;
  private strategy: EMAStrategy;
  private config: BotConfig;
  private isRunning: boolean = false;
  private tradingEnabled: boolean = false;
  private currentPosition: Position | null = null;
  private startTime: number;
  private tradingLoopInterval: NodeJS.Timeout | null = null;

  constructor(
    exchange: ExchangeManager,
    config: BotConfig,
    mlServiceURL?: string
  ) {
    this.exchange = exchange;
    this.config = config;
    this.startTime = Date.now();

    // Инициализация Risk Manager
    this.riskManager = new RiskManager({
      maxPositionPercent: 10,
      stopLossPercent: 2,
      takeProfitPercent: 5,
      maxDailyTrades: 10,
      minTradeInterval: 300
    });

    // Инициализация ML Service
    this.mlService = new MLService({
      baseURL: mlServiceURL || process.env.ML_SERVICE_URL || 'http://localhost:5000'
    });

    // Инициализация стратегии
    this.strategy = new EMAStrategy({
      fastPeriod: 9,
      slowPeriod: 21,
      threshold: 0.25
    });

    logger.info('Trading Bot initialized');
    logger.info(`Symbol: ${config.symbol}`);
    logger.info(`Strategy: ${config.strategy}`);
  }  /**
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

      // Проверяем ML Service (необязательно)
      await this.mlService.checkHealth();

      this.isRunning = true;
      logger.info('🚀 Trading Bot started');
      
      // Запускаем основной торговый цикл
      this.runTradingLoop();
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

    // Останавливаем торговый цикл
    if (this.tradingLoopInterval) {
      clearInterval(this.tradingLoopInterval);
      this.tradingLoopInterval = null;
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

  /**
   * Основной торговый цикл
   */
  private runTradingLoop(): void {
    // Запускаем цикл каждые 30 секунд
    this.tradingLoopInterval = setInterval(async () => {
      if (!this.isRunning) {
        return;
      }

      try {
        await this.executeTradingCycle();
      } catch (error) {
        logger.error('Error in trading cycle:', error);
      }
    }, 30000); // 30 секунд

    logger.info('Trading loop started (30s interval)');
  }

  /**
   * Выполнить один цикл торговли
   */
  private async executeTradingCycle(): Promise<void> {
    try {
      // Получаем текущую цену и OHLCV данные
      const ticker = await this.exchange.getTicker(this.config.symbol);
      const ohlcv = await this.exchange.getOHLCV(
        this.config.symbol,
        this.config.timeframe,
        100
      );

      const currentPrice = ticker.last;

      logger.debug(`Trading cycle: ${this.config.symbol} @ ${currentPrice}`);

      // Если есть открытая позиция, проверяем нужно ли её закрыть
      if (this.currentPosition) {
        await this.checkPositionExit(currentPrice);
        return; // Не открываем новую позицию, если уже есть открытая
      }

      // Если торговля не включена, не открываем позиции
      if (!this.tradingEnabled) {
        return;
      }

      // Проверяем можно ли открыть новую сделку (risk management)
      const canTrade = this.riskManager.canOpenTrade();
      if (!canTrade.allowed) {
        logger.debug(`Cannot trade: ${canTrade.reason}`);
        return;
      }

      // Анализируем рынок через EMA стратегию
      const emaSignal = this.strategy.analyze(ohlcv, currentPrice);
      logger.debug(`EMA Signal: ${emaSignal.action} (confidence: ${(emaSignal.confidence * 100).toFixed(1)}%)`);

      // Если ML Service доступен, получаем ML предсказание
      let mlSignal = null;
      if (this.mlService.isServiceAvailable()) {
        const features = this.mlService.prepareFeatures(ohlcv);
        if (features.length > 0) {
          mlSignal = await this.mlService.predict(features, ohlcv);
          logger.debug(`ML Signal: ${mlSignal.signal} (confidence: ${(mlSignal.confidence * 100).toFixed(1)}%)`);
        }
      }

      // Комбинируем сигналы
      const finalSignal = this.combineSignals(emaSignal, mlSignal);

      // Открываем позицию если сигнал сильный
      if (finalSignal.action === 'BUY' && finalSignal.confidence > 0.6) {
        await this.openPosition('buy', currentPrice, finalSignal.reason);
      } else if (finalSignal.action === 'SELL' && finalSignal.confidence > 0.6) {
        await this.openPosition('sell', currentPrice, finalSignal.reason);
      }

    } catch (error) {
      logger.error('Error in trading cycle:', error);
    }
  }

  /**
   * Комбинировать EMA и ML сигналы
   */
  private combineSignals(emaSignal: any, mlSignal: any): any {
    if (!mlSignal) {
      return emaSignal; // Только EMA
    }

    // Если оба сигнала согласны
    if (emaSignal.action === mlSignal.signal) {
      return {
        action: emaSignal.action,
        confidence: (emaSignal.confidence + mlSignal.confidence) / 2,
        reason: `EMA + ML agree: ${emaSignal.action}`
      };
    }

    // Если сигналы противоречат, берем более уверенный
    if (emaSignal.confidence > mlSignal.confidence) {
      return {
        action: emaSignal.action,
        confidence: emaSignal.confidence * 0.7, // Снижаем уверенность
        reason: `EMA stronger: ${emaSignal.action}`
      };
    } else {
      return {
        action: mlSignal.signal,
        confidence: mlSignal.confidence * 0.7,
        reason: `ML stronger: ${mlSignal.signal}`
      };
    }
  }

  /**
   * Открыть позицию
   */
  private async openPosition(
    side: 'buy' | 'sell',
    currentPrice: number,
    reason: string
  ): Promise<void> {
    try {
      // Получаем баланс
      const balance = await this.exchange.getBalance('USDT');

      // Рассчитываем размер позиции через Risk Manager
      const tradeSize = this.riskManager.calculatePositionSize(
        balance.available,
        currentPrice,
        side
      );

      logger.info(`🔷 Opening ${side.toUpperCase()} position:`);
      logger.info(`   Amount: ${tradeSize.amountInCurrency.toFixed(6)} ${this.config.symbol.split('/')[0]}`);
      logger.info(`   Size: $${tradeSize.amountInUSDT.toFixed(2)}`);
      logger.info(`   Stop Loss: $${tradeSize.stopLoss.toFixed(2)}`);
      logger.info(`   Take Profit: $${tradeSize.takeProfit.toFixed(2)}`);
      logger.info(`   Reason: ${reason}`);

      // ВАЖНО: В production здесь создается реальный ордер
      // const order = await this.exchange.createMarketOrder(
      //   this.config.symbol,
      //   side,
      //   tradeSize.amountInCurrency
      // );

      // Сохраняем позицию
      this.currentPosition = {
        symbol: this.config.symbol,
        side: side === 'buy' ? 'long' : 'short',
        entryPrice: currentPrice,
        currentPrice: currentPrice,
        amount: tradeSize.amountInCurrency,
        profit: 0,
        profitPercent: 0,
        stopLoss: tradeSize.stopLoss,
        takeProfit: tradeSize.takeProfit,
        openTime: new Date().toISOString()
      };

      // Регистрируем сделку в Risk Manager
      this.riskManager.registerTrade();

      logger.info('✅ Position opened successfully');

    } catch (error) {
      logger.error('Failed to open position:', error);
    }
  }

  /**
   * Проверить нужно ли закрыть позицию
   */
  private async checkPositionExit(currentPrice: number): Promise<void> {
    if (!this.currentPosition) return;

    // Обновляем текущую цену и прибыль
    const { profit, profitPercent } = this.riskManager.calculateProfitLoss(
      this.currentPosition.entryPrice,
      currentPrice,
      this.currentPosition.amount,
      this.currentPosition.side
    );

    this.currentPosition.currentPrice = currentPrice;
    this.currentPosition.profit = profit;
    this.currentPosition.profitPercent = profitPercent;

    // Проверяем Stop Loss / Take Profit
    const shouldClose = this.riskManager.shouldClosePosition(
      this.currentPosition.entryPrice,
      currentPrice,
      this.currentPosition.side,
      this.currentPosition.stopLoss,
      this.currentPosition.takeProfit
    );

    if (shouldClose.shouldClose) {
      await this.closePosition(shouldClose.reason || 'Unknown reason');
    }
  }

  /**
   * Закрыть позицию
   */
  private async closePosition(reason: string): Promise<void> {
    if (!this.currentPosition) return;

    try {
      logger.info(`🔶 Closing ${this.currentPosition.side.toUpperCase()} position:`);
      logger.info(`   Profit: $${this.currentPosition.profit.toFixed(2)} (${this.currentPosition.profitPercent.toFixed(2)}%)`);
      logger.info(`   Reason: ${reason}`);

      // ВАЖНО: В production здесь создается ордер на закрытие
      // const side = this.currentPosition.side === 'long' ? 'sell' : 'buy';
      // await this.exchange.createMarketOrder(
      //   this.config.symbol,
      //   side,
      //   this.currentPosition.amount
      // );

      logger.info('✅ Position closed successfully');

      // Очищаем позицию
      this.currentPosition = null;

    } catch (error) {
      logger.error('Failed to close position:', error);
    }
  }
}
