"""
СТРАТЕГИЯ BOLLINGER BANDS
"""
from .base_strategy import BaseStrategy
from utils.helpers import calculate_bollinger_bands
from utils.logger import log_info

class BollingerStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="📊 Bollinger Bands",
            description="Торговля на отскоках от границ Bollinger Bands и пробоях"
        )
        self.default_settings = {
            'bb_period': 20,
            'bb_std_dev': 2,
            'use_squeeze': True,
            'exit_on_middle': False,
            'volume_confirmation': False
        }
        self.settings = self.default_settings.copy()
        self.in_squeeze = False
    
    def calculate_signal(self, market_data, ml_confidence=0.5, ml_signal="⚪ НЕЙТРАЛЬНО"):
        """Расчет сигнала Bollinger Bands"""
        is_valid, message = self.validate_market_data(market_data)
        if not is_valid:
            return 'wait'
        
        if 'ohlcv' not in market_data:
            return 'wait'
        
        try:
            closes = [candle[4] for candle in market_data['ohlcv']]
            current_price = market_data['current_price']
            
            period = self.settings.get('bb_period', 20)
            std_dev = self.settings.get('bb_std_dev', 2)
            
            # Расчет Bollinger Bands
            bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(closes, period, std_dev)
            
            if bb_upper == bb_lower:  # Избегаем деления на ноль
                return 'wait'
            
            # Позиция цены относительно BB
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            
            # Определяем сжатие (squeeze)
            band_width = (bb_upper - bb_lower) / bb_middle
            is_squeeze = band_width < 0.05  # Узкие полосы
            
            # Логика входа
            if current_price <= bb_lower and not is_squeeze:
                # Цена коснулась нижней границы - сигнал к покупке
                if self.position != 'long':
                    log_info(f"📊 Bollinger: BUY сигнал (цена у нижней границы)")
                    return 'buy'
                    
            elif current_price >= bb_upper and not is_squeeze:
                # Цена коснулась верхней границы - сигнал к продаже
                if self.position == 'long':
                    log_info(f"📊 Bollinger: SELL сигнал (цена у верхней границы)")
                    return 'sell'
            
            # Логика выхода по средней линии
            if (self.settings.get('exit_on_middle', False) and 
                self.position == 'long' and 
                abs(current_price - bb_middle) / bb_middle < 0.01):
                # Цена близко к средней линии - выход
                log_info(f"📊 Bollinger: EXIT сигнал (цена у средней линии)")
                return 'sell'
            
            # Отслеживание сжатия
            if is_squeeze and not self.in_squeeze:
                log_info("📊 Bollinger: Обнаружено сжатие полос")
                self.in_squeeze = True
            elif not is_squeeze and self.in_squeeze:
                log_info("📊 Bollinger: Сжатие завершено")
                self.in_squeeze = False
            
            return 'wait'
            
        except Exception as e:
            log_info(f"❌ Ошибка расчета Bollinger Bands: {e}")
            return 'wait'
    
    def get_settings_info(self):
        """Информация о настройках"""
        return {
            'bb_period': f"{self.settings.get('bb_period', 20)}",
            'bb_std_dev': f"{self.settings.get('bb_std_dev', 2)}",
            'use_squeeze': 'ВКЛ' if self.settings.get('use_squeeze', True) else 'ВЫКЛ',
            'exit_on_middle': 'ВКЛ' if self.settings.get('exit_on_middle', False) else 'ВЫКЛ',
            'volume_confirmation': 'ВКЛ' if self.settings.get('volume_confirmation', False) else 'ВЫКЛ'
        }