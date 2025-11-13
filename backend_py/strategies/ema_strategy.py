import numpy as np
from typing import List, Optional, Dict, Any
from loguru import logger
from pydantic import BaseModel

class OHLCV(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class EMAConfig(BaseModel):
    fast_period: int = 9
    slow_period: int = 21
    threshold: float = 0.25  # Минимальная разница для сигнала (%)

class EMAStrategy:
    def __init__(self, exchange, symbol: str, timeframe: str, config: Optional[Dict[str, Any]] = None):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = EMAConfig(**(config or {}))

        logger.info(f'EMA Strategy initialized: Fast={self.config.fast_period}, Slow={self.config.slow_period}, Threshold={self.config.threshold}%')

    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Рассчитывает EMA для списка цен"""
        if len(prices) < period:
            return prices[-1] if prices else 0

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Рассчитывает RSI"""
        if len(prices) < period + 1:
            return 50

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    async def get_signal(self) -> Optional[str]:
        """Анализ рынка и генерация сигнала"""
        try:
            # Получаем исторические данные
            ohlcv = await self.exchange.exchange.fetchOHLCV(self.symbol, self.timeframe, limit=100)
            if len(ohlcv) < 50:
                return None

            # Извлекаем цены закрытия
            close_prices = [candle[4] for candle in ohlcv]

            # Рассчитываем EMA
            fast_ema = self.calculate_ema(close_prices, self.config.fast_period)
            slow_ema = self.calculate_ema(close_prices, self.config.slow_period)

            # Рассчитываем RSI
            rsi = self.calculate_rsi(close_prices)

            # Разница между EMA в процентах
            ema_diff = ((fast_ema - slow_ema) / slow_ema) * 100
            abs_ema_diff = abs(ema_diff)

            logger.debug(f'EMA Analysis: Fast={fast_ema:.2f}, Slow={slow_ema:.2f}, Diff={ema_diff:.3f}%, RSI={rsi:.1f}')

            # Генерация сигнала
            if abs_ema_diff >= self.config.threshold:
                if ema_diff > 0 and rsi < 70:  # Fast EMA выше Slow и RSI не перекуплен
                    return 'buy'
                elif ema_diff < 0 and rsi > 30:  # Fast EMA ниже Slow и RSI не перепродан
                    return 'sell'

            return None  # HOLD
        except Exception as e:
            logger.error(f'Failed to get EMA signal: {e}')
            return None