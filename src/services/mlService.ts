import axios, { AxiosInstance } from 'axios';
import { logger } from '../utils/logger';

export interface MLPrediction {
  prediction: 0 | 1;
  confidence: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  timestamp: string;
}

export interface MLServiceConfig {
  baseURL: string;
  timeout?: number;
}

export class MLService {
  private client: AxiosInstance;
  private isAvailable: boolean = false;

  constructor(config: MLServiceConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    logger.info(`ML Service initialized: ${config.baseURL}`);
  }

  /**
   * Проверка доступности ML сервиса
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      this.isAvailable = response.data.status === 'ok' && response.data.model_loaded;

      if (this.isAvailable) {
        logger.info('✅ ML Service is available and model is loaded');
      } else {
        logger.warn('⚠️ ML Service is available but model is not loaded');
      }

      return this.isAvailable;
    } catch (error) {
      logger.warn('⚠️ ML Service is not available:', (error as Error).message);
      this.isAvailable = false;
      return false;
    }
  }

  /**
   * Получить ML предсказание
   */
  async predict(features: number[], ohlcv?: any[]): Promise<MLPrediction> {
    try {
      const response = await this.client.post('/predict', {
        features,
        ohlcv: ohlcv || []
      });

      return {
        prediction: response.data.prediction,
        confidence: response.data.confidence,
        signal: response.data.signal,
        timestamp: response.data.timestamp
      };
    } catch (error) {
      logger.error('Failed to get ML prediction:', error);

      // Возвращаем нейтральное предсказание в случае ошибки
      return {
        prediction: 0,
        confidence: 0.5,
        signal: 'HOLD',
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Проверить, доступен ли ML сервис
   */
  isServiceAvailable(): boolean {
    return this.isAvailable;
  }

  /**
   * Подготовить features из OHLCV данных
   * (упрощенная версия, можно расширить)
   */
  prepareFeatures(ohlcv: any[]): number[] {
    if (ohlcv.length < 20) {
      return [];
    }

    const closes = ohlcv.map(c => c.close);
    const volumes = ohlcv.map(c => c.volume);

    // Простые features для ML
    const features: number[] = [];

    // 1. Последние 5 цен закрытия (нормализованные)
    const recentCloses = closes.slice(-5);
    const avgClose = recentCloses.reduce((a, b) => a + b, 0) / recentCloses.length;
    recentCloses.forEach(close => {
      features.push((close - avgClose) / avgClose);
    });

    // 2. Изменение цены за последние 5 периодов
    for (let i = 1; i <= 5; i++) {
      const change = (closes[closes.length - i] - closes[closes.length - i - 1]) / closes[closes.length - i - 1];
      features.push(change);
    }

    // 3. Средний объем
    const avgVolume = volumes.slice(-10).reduce((a, b) => a + b, 0) / 10;
    features.push(volumes[volumes.length - 1] / avgVolume - 1);

    // 4. Волатильность (стандартное отклонение последних 10 цен)
    const last10 = closes.slice(-10);
    const mean = last10.reduce((a, b) => a + b, 0) / last10.length;
    const variance = last10.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / last10.length;
    features.push(Math.sqrt(variance) / mean);

    return features;
  }
}
