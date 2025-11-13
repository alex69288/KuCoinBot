import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export interface BotStatus {
  isRunning: boolean;
  tradingEnabled: boolean;
  balance: {
    total: number;
    available: number;
    used: number;
  };
  positions: {
    current: any;
    total: number;
    profit: number;
  };
  uptime: number;
  timestamp: string;
}

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
  high24h: number;
  low24h: number;
  timestamp: string;
}

export const getStatus = async (): Promise<BotStatus> => {
  const { data } = await api.get('/status');
  return data;
};

export const getMarket = async (): Promise<MarketData> => {
  const { data } = await api.get('/market');
  return data;
};

export const startTrading = async (): Promise<void> => {
  await api.post('/trade/start');
};

export const stopTrading = async (): Promise<void> => {
  await api.post('/trade/stop');
};
