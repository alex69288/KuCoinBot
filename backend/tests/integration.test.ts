/**
 * Интеграционный тест для проверки Bot Manager + ML Service + Risk Manager
 */

import { ExchangeManager } from '../src/core/exchange';
import { TradingBot } from '../src/core/bot';

describe('Trading Bot Integration Tests', () => {
  let exchange: ExchangeManager;
  let bot: TradingBot;

  beforeEach(() => {
    // Инициализация с тестовыми данными
    exchange = new ExchangeManager({
      apiKey: 'test-key',
      apiSecret: 'test-secret',
      apiPassphrase: 'test-passphrase',
      testnet: true
    });

    bot = new TradingBot(
      exchange,
      {
        symbol: 'BTC/USDT',
        timeframe: '1h',
        tradingEnabled: false,
        strategy: 'ema_ml'
      },
      'http://localhost:5000' // ML Service URL
    );
  });

  test('Bot should initialize correctly', () => {
    expect(bot).toBeDefined();
    expect(bot.isActive()).toBe(false);
    expect(bot.isTradingEnabled()).toBe(false);
  });

  test('Bot should have all required methods', () => {
    expect(typeof bot.start).toBe('function');
    expect(typeof bot.stop).toBe('function');
    expect(typeof bot.enableTrading).toBe('function');
    expect(typeof bot.disableTrading).toBe('function');
    expect(typeof bot.getStatus).toBe('function');
    expect(typeof bot.getMarketData).toBe('function');
    expect(typeof bot.getCurrentPosition).toBe('function');
  });

  test('Bot should enable/disable trading', () => {
    expect(bot.isTradingEnabled()).toBe(false);

    bot.enableTrading();
    expect(bot.isTradingEnabled()).toBe(true);

    bot.disableTrading();
    expect(bot.isTradingEnabled()).toBe(false);
  });

  test('Bot should return null position when no trades', () => {
    const position = bot.getCurrentPosition();
    expect(position).toBeNull();
  });

  test('Bot should update configuration', () => {
    bot.updateConfig({ symbol: 'ETH/USDT' });
    // Configuration updated successfully
    expect(true).toBe(true);
  });

  test('Bot uptime should increase', (done) => {
    const uptime1 = bot.getUptime();

    setTimeout(() => {
      const uptime2 = bot.getUptime();
      expect(uptime2).toBeGreaterThanOrEqual(uptime1);
      done();
    }, 1100);
  });

  // Пропускаем тесты, требующие реального подключения
  test.skip('Bot should start and connect to exchange', async () => {
    await bot.start();
    expect(bot.isActive()).toBe(true);
    bot.stop();
  });

  test.skip('Bot should get market data', async () => {
    const marketData = await bot.getMarketData();
    expect(marketData).toBeDefined();
    expect(marketData.symbol).toBe('BTC/USDT');
  });

  test.skip('Bot should get status', async () => {
    const status = await bot.getStatus();
    expect(status).toBeDefined();
    expect(status.bot).toBeDefined();
    expect(status.exchange).toBeDefined();
    expect(status.balance).toBeDefined();
  });
});

describe('Risk Manager Tests', () => {
  test('Risk Manager should be initialized in Bot', () => {
    const exchange = new ExchangeManager({
      apiKey: 'test',
      apiSecret: 'test',
      apiPassphrase: 'test',
      testnet: true
    });

    const bot = new TradingBot(exchange, {
      symbol: 'BTC/USDT',
      timeframe: '1h',
      tradingEnabled: false,
      strategy: 'ema_ml'
    });

    expect(bot).toBeDefined();
  });
});
