import * as ccxt from 'ccxt';
import { logger } from '../utils/logger';

export interface ExchangeConfig {
  apiKey: string;
  apiSecret: string;
  apiPassphrase?: string;
  testnet?: boolean;
}

export interface Balance {
  total: number;
  available: number;
  used: number;
  currency: string;
}

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  bid?: number;
  ask?: number;
  timestamp: string;
}

export interface Ticker {
  symbol: string;
  last: number;
  bid: number;
  ask: number;
  high: number;
  low: number;
  volume: number;
  percentage: number;
  timestamp: number;
}

export class ExchangeManager {
  private exchange: ccxt.Exchange;
  private isConnected: boolean = false;

  constructor(config: ExchangeConfig) {
    const options: any = {
      apiKey: config.apiKey,
      secret: config.apiSecret,
      password: config.apiPassphrase,
      enableRateLimit: true,
      options: {
        defaultType: 'spot', // spot trading
      }
    };

    // Testnet support
    if (config.testnet) {
      options.urls = {
        api: {
          public: 'https://api-sandbox.kucoin.com',
          private: 'https://api-sandbox.kucoin.com',
        }
      };
    }

    this.exchange = new ccxt.kucoin(options);
    logger.info('Exchange Manager initialized for KuCoin');
  }

  /**
   * Проверка подключения к бирже
   */
  async connect(): Promise<boolean> {
    try {
      await this.exchange.loadMarkets();
      this.isConnected = true;
      logger.info('✅ Connected to KuCoin successfully');
      return true;
    } catch (error) {
      logger.error('❌ Failed to connect to KuCoin:', error);
      this.isConnected = false;
      return false;
    }
  }

  /**
   * Получить баланс USDT
   */
  async getBalance(currency: string = 'USDT'): Promise<Balance> {
    try {
      const balance = await this.exchange.fetchBalance();
      const currencyBalance = balance[currency] || { total: 0, free: 0, used: 0 };

      return {
        total: currencyBalance.total || 0,
        available: currencyBalance.free || 0,
        used: currencyBalance.used || 0,
        currency
      };
    } catch (error) {
      logger.error(`Failed to fetch balance for ${currency}:`, error);
      throw error;
    }
  }

  /**
   * Получить текущую цену тикера
   */
  async getTicker(symbol: string = 'BTC/USDT'): Promise<Ticker> {
    try {
      const ticker = await this.exchange.fetchTicker(symbol);

      return {
        symbol: ticker.symbol,
        last: ticker.last || 0,
        bid: ticker.bid || 0,
        ask: ticker.ask || 0,
        high: ticker.high || 0,
        low: ticker.low || 0,
        volume: ticker.baseVolume || 0,
        percentage: ticker.percentage || 0,
        timestamp: ticker.timestamp || Date.now()
      };
    } catch (error) {
      logger.error(`Failed to fetch ticker for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Получить полные рыночные данные
   */
  async getMarketData(symbol: string = 'BTC/USDT'): Promise<MarketData> {
    try {
      const ticker = await this.getTicker(symbol);

      return {
        symbol: ticker.symbol,
        price: ticker.last,
        change24h: ticker.percentage,
        changePercent24h: ticker.percentage,
        volume: ticker.volume,
        volume24h: ticker.volume,
        high24h: ticker.high,
        low24h: ticker.low,
        bid: ticker.bid,
        ask: ticker.ask,
        timestamp: new Date(ticker.timestamp).toISOString()
      };
    } catch (error) {
      logger.error(`Failed to fetch market data for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Получить OHLCV данные для анализа
   */
  async getOHLCV(
    symbol: string = 'BTC/USDT',
    timeframe: string = '1h',
    limit: number = 100
  ): Promise<any[]> {
    try {
      const ohlcv = await this.exchange.fetchOHLCV(symbol, timeframe, undefined, limit);

      return ohlcv.map((candle: any) => ({
        timestamp: candle[0],
        open: candle[1],
        high: candle[2],
        low: candle[3],
        close: candle[4],
        volume: candle[5]
      }));
    } catch (error) {
      logger.error(`Failed to fetch OHLCV for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Создать лимитный ордер
   */
  async createLimitOrder(
    symbol: string,
    side: 'buy' | 'sell',
    amount: number,
    price: number
  ): Promise<any> {
    try {
      logger.info(`Creating ${side} limit order: ${amount} ${symbol} @ ${price}`);

      const order = await this.exchange.createLimitOrder(
        symbol,
        side,
        amount,
        price
      );

      logger.info(`Order created successfully: ${order.id}`);
      return order;
    } catch (error) {
      logger.error(`Failed to create ${side} order:`, error);
      throw error;
    }
  }

  /**
   * Создать рыночный ордер
   */
  async createMarketOrder(
    symbol: string,
    side: 'buy' | 'sell',
    amount: number
  ): Promise<any> {
    try {
      logger.info(`Creating ${side} market order: ${amount} ${symbol}`);

      const order = await this.exchange.createMarketOrder(
        symbol,
        side,
        amount
      );

      logger.info(`Market order created successfully: ${order.id}`);
      return order;
    } catch (error) {
      logger.error(`Failed to create ${side} market order:`, error);
      throw error;
    }
  }

  /**
   * Получить открытые ордера
   */
  async getOpenOrders(symbol?: string): Promise<any[]> {
    try {
      const orders = await this.exchange.fetchOpenOrders(symbol);
      return orders;
    } catch (error) {
      logger.error('Failed to fetch open orders:', error);
      throw error;
    }
  }

  /**
   * Отменить ордер
   */
  async cancelOrder(orderId: string, symbol: string): Promise<any> {
    try {
      logger.info(`Cancelling order ${orderId} for ${symbol}`);
      const result = await this.exchange.cancelOrder(orderId, symbol);
      logger.info(`Order ${orderId} cancelled successfully`);
      return result;
    } catch (error) {
      logger.error(`Failed to cancel order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Проверить, подключен ли exchange
   */
  isExchangeConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Получить минимальный размер ордера
   */
  async getMinAmount(symbol: string): Promise<number> {
    try {
      await this.exchange.loadMarkets();
      const market = this.exchange.market(symbol);
      return market.limits.amount?.min || 0.0001;
    } catch (error) {
      logger.error(`Failed to get min amount for ${symbol}:`, error);
      return 0.0001; // Fallback
    }
  }

  /**
   * Получить информацию о рынке
   */
  async getMarketInfo(symbol: string): Promise<any> {
    try {
      await this.exchange.loadMarkets();
      return this.exchange.market(symbol);
    } catch (error) {
      logger.error(`Failed to get market info for ${symbol}:`, error);
      throw error;
    }
  }
}
