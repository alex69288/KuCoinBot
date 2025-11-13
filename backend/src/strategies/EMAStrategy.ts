import { BaseStrategy, Signal, OHLCV } from './BaseStrategy';
import { logger } from '../utils/logger';

export interface EMAConfig {
  fastPeriod: number;
  slowPeriod: number;
  threshold: number; // Минимальная разница для сигнала (%)
}

export class EMAStrategy extends BaseStrategy {
  private config: EMAConfig;

  constructor(config?: Partial<EMAConfig>) {
    super('EMA Strategy');

    this.config = {
      fastPeriod: config?.fastPeriod || 9,
      slowPeriod: config?.slowPeriod || 21,
      threshold: config?.threshold || 0.25 // 0.25%
    };

    logger.info(`EMA Strategy initialized: Fast=${this.config.fastPeriod}, Slow=${this.config.slowPeriod}, Threshold=${this.config.threshold}%`);
  }

  /**
   * Анализ рынка по EMA стратегии
   */
  analyze(ohlcv: OHLCV[], currentPrice: number): Signal {
    try {
      // Извлекаем цены закрытия
      const closePrices = ohlcv.map(candle => candle.close);

      // Рассчитываем EMA
      const fastEMA = this.calculateEMA(closePrices, this.config.fastPeriod);
      const slowEMA = this.calculateEMA(closePrices, this.config.slowPeriod);

      // Рассчитываем RSI для дополнительного фильтра
      const rsi = this.calculateRSI(closePrices);

      // Разница между EMA в процентах
      const emaDiff = ((fastEMA - slowEMA) / slowEMA) * 100;
      const absEmaDiff = Math.abs(emaDiff);

      logger.debug(`EMA Analysis: Fast=${fastEMA.toFixed(2)}, Slow=${slowEMA.toFixed(2)}, Diff=${emaDiff.toFixed(3)}%, RSI=${rsi.toFixed(1)}`);

      // Генерация сигнала
      let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
      let confidence = 0;
      let reason = '';

      // Сигнал на покупку: Fast EMA > Slow EMA
      if (emaDiff > this.config.threshold && rsi < 70) {
        action = 'BUY';
        confidence = Math.min(absEmaDiff / 2, 0.9); // Макс 90%
        reason = `Fast EMA (${fastEMA.toFixed(2)}) > Slow EMA (${slowEMA.toFixed(2)}), RSI: ${rsi.toFixed(1)}`;
      }
      // Сигнал на продажу: Fast EMA < Slow EMA
      else if (emaDiff < -this.config.threshold && rsi > 30) {
        action = 'SELL';
        confidence = Math.min(absEmaDiff / 2, 0.9); // Макс 90%
        reason = `Fast EMA (${fastEMA.toFixed(2)}) < Slow EMA (${slowEMA.toFixed(2)}), RSI: ${rsi.toFixed(1)}`;
      }
      // Недостаточно сильный сигнал
      else {
        action = 'HOLD';
        confidence = 0.5;
        reason = `EMA diff (${emaDiff.toFixed(3)}%) below threshold (${this.config.threshold}%), RSI: ${rsi.toFixed(1)}`;
      }

      return {
        action,
        confidence,
        reason,
        price: currentPrice,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      logger.error('Error in EMA strategy analysis:', error);

      return {
        action: 'HOLD',
        confidence: 0,
        reason: 'Error in analysis',
        price: currentPrice,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Обновить конфигурацию
   */
  updateConfig(config: Partial<EMAConfig>): void {
    this.config = { ...this.config, ...config };
    logger.info('EMA Strategy config updated:', this.config);
  }

  /**
   * Получить текущую конфигурацию
   */
  getConfig(): EMAConfig {
    return { ...this.config };
  }
}
