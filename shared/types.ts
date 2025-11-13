/**
 * Общие TypeScript типы для Frontend и Backend
 * Экспортируются для использования в обоих проектах
 */

// ========================================
// BOT STATUS TYPES
// ========================================

export interface BotStatus {
  isRunning: boolean;
  tradingEnabled: boolean;
  balance: Balance;
  positions: Positions;
  uptime: number;
  timestamp: string;
}

export interface Balance {
  total: number;
  available: number;
  used: number;
  currency?: string;
}

export interface Positions {
  current: Position | null;
  total: number;
  profit: number;
  profitPercent?: number;
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

// ========================================
// MARKET DATA TYPES
// ========================================

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h?: number;
  volume: number;
  volume24h?: number;
  high24h: number;
  low24h: number;
  bid?: number;
  ask?: number;
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

// ========================================
// TRADING TYPES
// ========================================

export interface TradeSignal {
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  strategy: string;
  price: number;
  timestamp: string;
  reason?: string;
}

export interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: number;
  amount: number;
  total: number;
  fee: number;
  profit?: number;
  timestamp: string;
  strategy: string;
}

// ========================================
// SETTINGS TYPES
// ========================================

export interface BotSettings {
  strategy: TradingStrategy;
  riskLevel: RiskLevel;
  maxPositionSize: number;
  stopLoss: number;
  takeProfit: number;
  mlEnabled: boolean;
  trading: TradingSettings;
  ml: MLSettings;
  risk: RiskSettings;
}

export type TradingStrategy = 'ema_ml' | 'price_action' | 'macd_rsi' | 'bollinger';

export type RiskLevel = 'conservative' | 'medium' | 'aggressive';

export interface TradingSettings {
  enabled: boolean;
  symbol: string;
  timeframe: string;
  maxDailyTrades: number;
  minTradeInterval: number; // seconds
}

export interface MLSettings {
  enabled: boolean;
  confidence: Threshold;
  model: string;
}

export interface RiskSettings {
  maxPositionSize: number; // USDT
  maxPositionPercent: number; // % of balance
  stopLoss: number; // %
  takeProfit: number; // %
  trailingStop: boolean;
  trailingStopPercent?: number;
}

export interface StrategySettings {
  ema: EMASettings;
  macd: MACDSettings;
  rsi: RSISettings;
  bollinger: BollingerSettings;
}

export interface EMASettings {
  fastPeriod: number;
  slowPeriod: number;
  threshold: number;
}

export interface MACDSettings {
  fastPeriod: number;
  slowPeriod: number;
  signalPeriod: number;
}

export interface RSISettings {
  period: number;
  overbought: number;
  oversold: number;
}

export interface BollingerSettings {
  period: number;
  stdDev: number;
}

// ========================================
// ML TYPES
// ========================================

export interface MLPrediction {
  prediction: 0 | 1;
  confidence: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  timestamp: string;
}

export interface MLModel {
  name: string;
  version: string;
  accuracy: number;
  lastTrained: string;
}

// ========================================
// ANALYTICS TYPES
// ========================================

export interface Analytics {
  totalTrades: number;
  winRate: number;
  profitLoss: number;
  profitLossPercent: number;
  bestTrade: number;
  worstTrade: number;
  averageProfit: number;
  sharpeRatio?: number;
  maxDrawdown?: number;
}

export interface PerformanceMetrics {
  daily: MetricsPeriod;
  weekly: MetricsPeriod;
  monthly: MetricsPeriod;
  allTime: MetricsPeriod;
}

export interface MetricsPeriod {
  trades: number;
  profit: number;
  profitPercent: number;
  winRate: number;
}

// ========================================
// API RESPONSE TYPES
// ========================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

// ========================================
// UTILITY TYPES
// ========================================

export interface Threshold {
  min: number;
  max: number;
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}
