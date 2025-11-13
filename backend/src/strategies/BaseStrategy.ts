export interface Signal {
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reason: string;
  price: number;
  timestamp: string;
}

export interface OHLCV {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export abstract class BaseStrategy {
  protected name: string;

  constructor(name: string) {
    this.name = name;
  }

  /**
   * Анализ рынка и генерация сигнала
   */
  abstract analyze(ohlcv: OHLCV[], currentPrice: number): Signal;

  /**
   * Получить имя стратегии
   */
  getName(): string {
    return this.name;
  }

  /**
   * Рассчитать EMA (Exponential Moving Average)
   */
  protected calculateEMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices[prices.length - 1] || 0;
    }

    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] - ema) * multiplier + ema;
    }

    return ema;
  }

  /**
   * Рассчитать SMA (Simple Moving Average)
   */
  protected calculateSMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices[prices.length - 1] || 0;
    }

    const slice = prices.slice(-period);
    return slice.reduce((a, b) => a + b, 0) / period;
  }

  /**
   * Рассчитать RSI (Relative Strength Index)
   */
  protected calculateRSI(prices: number[], period: number = 14): number {
    if (prices.length < period + 1) {
      return 50; // Neutral
    }

    let gains = 0;
    let losses = 0;

    for (let i = prices.length - period; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      if (change > 0) {
        gains += change;
      } else {
        losses -= change;
      }
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    if (avgLoss === 0) return 100;

    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  }
}
