import ccxt
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel

class ExchangeConfig(BaseModel):
    apiKey: str
    apiSecret: str
    apiPassphrase: Optional[str] = None
    testnet: bool = False

class Balance(BaseModel):
    total: float
    available: float
    used: float
    currency: str

class MarketData(BaseModel):
    symbol: str
    price: float
    change24h: float
    changePercent24h: float
    volume: float
    volume24h: float
    high24h: float
    low24h: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    timestamp: str

class Ticker(BaseModel):
    symbol: str
    last: float
    bid: float
    ask: float
    high: float
    low: float
    volume: float
    percentage: float
    timestamp: int

class ExchangeManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = ExchangeConfig(**config)
        self.exchange = ccxt.kucoin({
            'apiKey': self.config.apiKey,
            'secret': self.config.apiSecret,
            'password': self.config.apiPassphrase,
            'sandbox': self.config.testnet,
            'enableRateLimit': True,
        })
        self.is_connected = False

    async def connect(self) -> bool:
        try:
            # Проверяем подключение через получение баланса
            await self.exchange.loadMarkets()
            self.is_connected = True
            logger.info('Exchange Manager initialized for KuCoin')
            return True
        except Exception as e:
            logger.error(f'Failed to connect to KuCoin: {e}')
            self.is_connected = False
            return False

    async def disconnect(self):
        self.is_connected = False
        logger.info('Exchange Manager disconnected')

    async def get_balance(self, currency: str = 'USDT') -> Balance:
        try:
            balance = await self.exchange.fetchBalance()
            return Balance(
                total=balance.get(currency, {}).get('total', 0),
                available=balance.get(currency, {}).get('free', 0),
                used=balance.get(currency, {}).get('used', 0),
                currency=currency
            )
        except Exception as e:
            logger.error(f'Failed to get balance: {e}')
            return Balance(total=0, available=0, used=0, currency=currency)

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        try:
            ticker = await self.exchange.fetchTicker(symbol)
            return Ticker(
                symbol=ticker['symbol'],
                last=ticker['last'],
                bid=ticker['bid'],
                ask=ticker['ask'],
                high=ticker['high'],
                low=ticker['low'],
                volume=ticker['baseVolume'],
                percentage=ticker['percentage'],
                timestamp=ticker['timestamp']
            )
        except Exception as e:
            logger.error(f'Failed to get ticker for {symbol}: {e}')
            return None

    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        try:
            ticker = await self.get_ticker(symbol)
            if not ticker:
                return None

            # Получаем дополнительные данные
            ohlcv = await self.exchange.fetchOHLCV(symbol, '1d', limit=2)
            if len(ohlcv) < 2:
                return None

            prev_close = ohlcv[-2][4]  # Предыдущая закрытая цена
            change24h = ticker.last - prev_close
            changePercent24h = (change24h / prev_close) * 100 if prev_close > 0 else 0

            return MarketData(
                symbol=symbol,
                price=ticker.last,
                change24h=change24h,
                changePercent24h=changePercent24h,
                volume=ticker.volume,
                volume24h=ticker.volume,
                high24h=ticker.high,
                low24h=ticker.low,
                bid=ticker.bid,
                ask=ticker.ask,
                timestamp=str(ticker.timestamp)
            )
        except Exception as e:
            logger.error(f'Failed to get market data for {symbol}: {e}')
            return None

    async def place_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None, order_type: str = 'limit') -> Dict[str, Any]:
        try:
            if order_type == 'limit' and price:
                order = await self.exchange.createOrder(symbol, 'limit', side, amount, price)
            else:
                order = await self.exchange.createOrder(symbol, 'market', side, amount)
            logger.info(f'Order placed: {order}')
            return order
        except Exception as e:
            logger.error(f'Failed to place order: {e}')
            raise e

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            result = await self.exchange.cancelOrder(order_id, symbol)
            logger.info(f'Order cancelled: {order_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to cancel order {order_id}: {e}')
            return False

    async def get_open_orders(self, symbol: str) -> list:
        try:
            orders = await self.exchange.fetchOpenOrders(symbol)
            return orders
        except Exception as e:
            logger.error(f'Failed to get open orders for {symbol}: {e}')
            return []