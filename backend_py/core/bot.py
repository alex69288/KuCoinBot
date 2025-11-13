import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from pydantic import BaseModel

from .exchange import ExchangeManager, MarketData

class BotConfig(BaseModel):
    symbol: str
    timeframe: str
    trading_enabled: bool
    strategy: str  # 'ema_ml' | 'price_action' | 'macd_rsi' | 'bollinger'

class Position(BaseModel):
    symbol: str
    side: str  # 'long' | 'short'
    entry_price: float
    current_price: float
    amount: float
    profit: float
    profit_percent: float
    stop_loss: float
    take_profit: float
    open_time: str

class TradingBot:
    def __init__(self, exchange: ExchangeManager, config: Dict[str, Any], ml_service_url: str = 'http://localhost:5000'):
        self.exchange = exchange
        self.config = BotConfig(**config)
        self.start_time = datetime.now().timestamp() * 1000

        # Импорт здесь для избежания циклических импортов
        from .risk_manager import RiskManager
        from ..services.ml_service import MLService
        from ..strategies.ema_strategy import EMAStrategy

        # Инициализация компонентов
        self.risk_manager = RiskManager({
            'max_position_percent': 10,
            'max_daily_loss_percent': 5,
            'max_drawdown_percent': 10,
            'min_order_size': 10,
            'max_order_size': 1000
        })

        self.ml_service = MLService(ml_service_url)
        self.strategy = EMAStrategy(exchange, config['symbol'], config['timeframe'])

        self.is_running = False
        self.trading_enabled = config.get('trading_enabled', False)
        self.current_position: Optional[Position] = None
        self.trading_loop_task: Optional[asyncio.Task] = None

    async def start(self):
        if self.is_running:
            return

        self.is_running = True
        logger.info(f'🚀 Trading Bot started for {self.config.symbol} with strategy {self.config.strategy}')

        # Запускаем торговый цикл
        self.trading_loop_task = asyncio.create_task(self._trading_loop())

    async def stop(self):
        self.is_running = False
        if self.trading_loop_task:
            self.trading_loop_task.cancel()
            try:
                await self.trading_loop_task
            except asyncio.CancelledError:
                pass
        logger.info('🛑 Trading Bot stopped')

    async def _trading_loop(self):
        while self.is_running:
            try:
                if self.trading_enabled:
                    await self._check_signals()
                    await self._manage_position()
                await asyncio.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                logger.error(f'Trading loop error: {e}')
                await asyncio.sleep(60)

    async def _check_signals(self):
        try:
            # Получаем сигнал от стратегии
            signal = await self.strategy.get_signal()

            if signal and not self.current_position:
                # Открываем позицию
                await self._open_position(signal)
            elif signal == 'close' and self.current_position:
                # Закрываем позицию
                await self._close_position()
        except Exception as e:
            logger.error(f'Failed to check signals: {e}')

    async def _open_position(self, signal: str):
        try:
            market_data = await self.exchange.get_market_data(self.config.symbol)
            if not market_data:
                return

            # Рассчитываем размер позиции через Risk Manager
            balance = await self.exchange.get_balance('USDT')
            position_size = self.risk_manager.calculate_position_size(balance.available, market_data.price)

            if position_size < self.risk_manager.config.min_order_size:
                logger.warning(f'Position size too small: {position_size}')
                return

            # Размещаем ордер
            side = 'buy' if signal == 'buy' else 'sell'
            order = await self.exchange.place_order(
                self.config.symbol,
                side,
                position_size / market_data.price,  # Количество в базовой валюте
                market_data.price
            )

            # Создаем позицию
            self.current_position = Position(
                symbol=self.config.symbol,
                side='long' if side == 'buy' else 'short',
                entry_price=market_data.price,
                current_price=market_data.price,
                amount=position_size / market_data.price,
                profit=0,
                profit_percent=0,
                stop_loss=self.risk_manager.calculate_stop_loss(market_data.price, 'long' if side == 'buy' else 'short'),
                take_profit=self.risk_manager.calculate_take_profit(market_data.price, 'long' if side == 'buy' else 'short'),
                open_time=datetime.now().isoformat()
            )

            logger.info(f'Position opened: {self.current_position}')
        except Exception as e:
            logger.error(f'Failed to open position: {e}')

    async def _close_position(self):
        try:
            if not self.current_position:
                return

            market_data = await self.exchange.get_market_data(self.config.symbol)
            if not market_data:
                return

            # Закрываем позицию
            side = 'sell' if self.current_position.side == 'long' else 'buy'
            order = await self.exchange.place_order(
                self.config.symbol,
                side,
                self.current_position.amount,
                market_data.price
            )

            # Обновляем позицию
            self.current_position.current_price = market_data.price
            self.current_position.profit = (market_data.price - self.current_position.entry_price) * self.current_position.amount
            self.current_position.profit_percent = (self.current_position.profit / (self.current_position.entry_price * self.current_position.amount)) * 100

            logger.info(f'Position closed: {self.current_position}')
            self.current_position = None
        except Exception as e:
            logger.error(f'Failed to close position: {e}')

    async def _manage_position(self):
        if not self.current_position:
            return

        try:
            market_data = await self.exchange.get_market_data(self.config.symbol)
            if not market_data:
                return

            # Проверяем стоп-лосс и тейк-профит
            if self.current_position.side == 'long':
                if market_data.price <= self.current_position.stop_loss or market_data.price >= self.current_position.take_profit:
                    await self._close_position()
            else:  # short
                if market_data.price >= self.current_position.stop_loss or market_data.price <= self.current_position.take_profit:
                    await self._close_position()
        except Exception as e:
            logger.error(f'Failed to manage position: {e}')

    async def get_status(self) -> Dict[str, Any]:
        return {
            'is_running': self.is_running,
            'trading_enabled': self.trading_enabled,
            'symbol': self.config.symbol,
            'strategy': self.config.strategy,
            'current_position': self.current_position.dict() if self.current_position else None,
            'uptime': datetime.now().timestamp() * 1000 - self.start_time
        }

    async def get_market_data(self) -> Optional[MarketData]:
        return await self.exchange.get_market_data(self.config.symbol)

    def enable_trading(self):
        self.trading_enabled = True
        logger.info('Trading enabled')

    def disable_trading(self):
        self.trading_enabled = False
        logger.info('Trading disabled')