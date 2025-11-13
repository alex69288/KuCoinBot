from typing import Dict, Any
from datetime import datetime
from loguru import logger
from pydantic import BaseModel

class RiskConfig(BaseModel):
    max_position_percent: float = 10  # % от баланса
    stop_loss_percent: float = 2  # % убытка
    take_profit_percent: float = 5  # % прибыли
    max_daily_trades: int = 10  # Максимум сделок в день
    min_trade_interval: int = 300  # Минимальный интервал между сделками (секунды)
    trailing_stop_enabled: bool = False
    trailing_stop_percent: float = 1
    max_daily_loss_percent: float = 5
    max_drawdown_percent: float = 10
    min_order_size: float = 10
    max_order_size: float = 1000

class TradeSize(BaseModel):
    amount_in_currency: float  # Количество криптовалюты
    amount_in_usdt: float  # Размер в USDT
    stop_loss: float  # Цена stop loss
    take_profit: float  # Цена take profit

class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = RiskConfig(**config)
        self.daily_trade_count = 0
        self.last_trade_time = 0
        self.daily_trade_date = ''
        self.daily_loss = 0

        logger.info(f'Risk Manager initialized: {self.config}')

    def calculate_position_size(self, balance: float, current_price: float) -> float:
        """Рассчитать размер позиции в USDT"""
        position_size_usdt = balance * (self.config.max_position_percent / 100)

        # Ограничиваем минимальным и максимальным размером
        position_size_usdt = max(self.config.min_order_size, min(position_size_usdt, self.config.max_order_size))

        return position_size_usdt

    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Рассчитать цену стоп-лосс"""
        if side == 'long':
            return entry_price * (1 - self.config.stop_loss_percent / 100)
        else:  # short
            return entry_price * (1 + self.config.stop_loss_percent / 100)

    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Рассчитать цену тейк-профит"""
        if side == 'long':
            return entry_price * (1 + self.config.take_profit_percent / 100)
        else:  # short
            return entry_price * (1 - self.config.take_profit_percent / 100)

    def can_open_position(self, current_time: float) -> bool:
        """Проверить, можно ли открыть позицию"""
        # Проверяем дневной лимит сделок
        today = datetime.now().strftime('%Y-%m-%d')
        if self.daily_trade_date != today:
            self.daily_trade_count = 0
            self.daily_trade_date = today

        if self.daily_trade_count >= self.config.max_daily_trades:
            logger.warning('Daily trade limit reached')
            return False

        # Проверяем интервал между сделками
        if current_time - self.last_trade_time < self.config.min_trade_interval:
            logger.warning('Trade interval too short')
            return False

        # Проверяем дневной убыток
        if self.daily_loss >= self.config.max_daily_loss_percent:
            logger.warning('Daily loss limit reached')
            return False

        return True

    def record_trade(self, profit_loss: float = 0):
        """Записать сделку"""
        self.daily_trade_count += 1
        self.last_trade_time = datetime.now().timestamp()
        self.daily_loss += max(0, -profit_loss)  # Только убытки

        logger.info(f'Trade recorded: count={self.daily_trade_count}, daily_loss={self.daily_loss:.2f}%')