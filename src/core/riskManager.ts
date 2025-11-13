import { logger } from '../utils/logger';

export interface RiskConfig {
  maxPositionPercent: number; // % от баланса (например, 10 = 10%)
  stopLossPercent: number; // % убытка (например, 2 = 2%)
  takeProfitPercent: number; // % прибыли (например, 5 = 5%)
  maxDailyTrades: number; // Максимум сделок в день
  minTradeInterval: number; // Минимальный интервал между сделками (секунды)
  trailingStopEnabled: boolean; // Включить trailing stop
  trailingStopPercent?: number; // % для trailing stop
}

export interface TradeSize {
  amountInCurrency: number; // Количество криптовалюты
  amountInUSDT: number; // Размер в USDT
  stopLoss: number; // Цена stop loss
  takeProfit: number; // Цена take profit
}

export class RiskManager {
  private config: RiskConfig;
  private dailyTradeCount: number = 0;
  private lastTradeTime: number = 0;
  private dailyTradeDate: string = '';

  constructor(config?: Partial<RiskConfig>) {
    this.config = {
      maxPositionPercent: config?.maxPositionPercent || 10,
      stopLossPercent: config?.stopLossPercent || 2,
      takeProfitPercent: config?.takeProfitPercent || 5,
      maxDailyTrades: config?.maxDailyTrades || 10,
      minTradeInterval: config?.minTradeInterval || 300, // 5 минут
      trailingStopEnabled: config?.trailingStopEnabled || false,
      trailingStopPercent: config?.trailingStopPercent || 1
    };

    logger.info('Risk Manager initialized:', this.config);
  }

  /**
   * Рассчитать размер позиции
   */
  calculatePositionSize(
    balance: number,
    currentPrice: number,
    side: 'buy' | 'sell'
  ): TradeSize {
    // Размер позиции в USDT
    const positionSizeUSDT = balance * (this.config.maxPositionPercent / 100);

    // Количество криптовалюты
    const amountInCurrency = positionSizeUSDT / currentPrice;

    // Рассчитываем Stop Loss и Take Profit
    let stopLoss: number;
    let takeProfit: number;

    if (side === 'buy') {
      // Для long позиции
      stopLoss = currentPrice * (1 - this.config.stopLossPercent / 100);
      takeProfit = currentPrice * (1 + this.config.takeProfitPercent / 100);
    } else {
      // Для short позиции
      stopLoss = currentPrice * (1 + this.config.stopLossPercent / 100);
      takeProfit = currentPrice * (1 - this.config.takeProfitPercent / 100);
    }

    logger.debug(`Position size calculated: ${amountInCurrency.toFixed(6)} @ ${currentPrice}`);
    logger.debug(`Stop Loss: ${stopLoss.toFixed(2)}, Take Profit: ${takeProfit.toFixed(2)}`);

    return {
      amountInCurrency,
      amountInUSDT: positionSizeUSDT,
      stopLoss,
      takeProfit
    };
  }

  /**
   * Проверить, можно ли открыть новую сделку
   */
  canOpenTrade(): { allowed: boolean; reason?: string } {
    // Проверка дневного лимита
    const today = new Date().toISOString().split('T')[0];
    if (this.dailyTradeDate !== today) {
      this.dailyTradeCount = 0;
      this.dailyTradeDate = today;
    }

    if (this.dailyTradeCount >= this.config.maxDailyTrades) {
      return {
        allowed: false,
        reason: `Daily trade limit reached (${this.config.maxDailyTrades})`
      };
    }

    // Проверка минимального интервала
    const now = Date.now();
    const timeSinceLastTrade = (now - this.lastTradeTime) / 1000;

    if (this.lastTradeTime > 0 && timeSinceLastTrade < this.config.minTradeInterval) {
      return {
        allowed: false,
        reason: `Min interval not met (${timeSinceLastTrade.toFixed(0)}s < ${this.config.minTradeInterval}s)`
      };
    }

    return { allowed: true };
  }

  /**
   * Зарегистрировать открытие сделки
   */
  registerTrade(): void {
    this.dailyTradeCount++;
    this.lastTradeTime = Date.now();
    logger.info(`Trade registered. Daily count: ${this.dailyTradeCount}/${this.config.maxDailyTrades}`);
  }

  /**
   * Проверить, нужно ли закрыть позицию (Stop Loss / Take Profit)
   */
  shouldClosePosition(
    _entryPrice: number, // Префикс _ означает, что параметр намеренно не используется
    currentPrice: number,
    side: 'long' | 'short',
    stopLoss: number,
    takeProfit: number
  ): { shouldClose: boolean; reason?: string } {
    if (side === 'long') {
      // Long позиция
      if (currentPrice <= stopLoss) {
        return { shouldClose: true, reason: 'Stop Loss hit' };
      }
      if (currentPrice >= takeProfit) {
        return { shouldClose: true, reason: 'Take Profit hit' };
      }
    } else {
      // Short позиция
      if (currentPrice >= stopLoss) {
        return { shouldClose: true, reason: 'Stop Loss hit' };
      }
      if (currentPrice <= takeProfit) {
        return { shouldClose: true, reason: 'Take Profit hit' };
      }
    }

    return { shouldClose: false };
  }

  /**
   * Рассчитать прибыль/убыток
   */
  calculateProfitLoss(
    entryPrice: number,
    currentPrice: number,
    amount: number,
    side: 'long' | 'short'
  ): { profit: number; profitPercent: number } {
    let profit: number;

    if (side === 'long') {
      profit = (currentPrice - entryPrice) * amount;
    } else {
      profit = (entryPrice - currentPrice) * amount;
    }

    const profitPercent = (profit / (entryPrice * amount)) * 100;

    return { profit, profitPercent };
  }

  /**
   * Обновить конфигурацию
   */
  updateConfig(config: Partial<RiskConfig>): void {
    this.config = { ...this.config, ...config };
    logger.info('Risk Manager config updated:', this.config);
  }

  /**
   * Получить текущую конфигурацию
   */
  getConfig(): RiskConfig {
    return { ...this.config };
  }

  /**
   * Получить статистику
   */
  getStats(): {
    dailyTradeCount: number;
    maxDailyTrades: number;
    lastTradeTime: number;
  } {
    return {
      dailyTradeCount: this.dailyTradeCount,
      maxDailyTrades: this.config.maxDailyTrades,
      lastTradeTime: this.lastTradeTime
    };
  }
}
