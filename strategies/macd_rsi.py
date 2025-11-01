"""
СТРАТЕГИЯ MACD + RSI
"""
from .base_strategy import BaseStrategy
from utils.helpers import calculate_rsi, calculate_macd
from utils.logger import log_info

class MacdRsiStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="🎯 MACD + RSI",
            description="Комбинация индикаторов MACD и RSI для точных входов"
        )
        self.default_settings = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'use_histogram': True
        }
        self.settings = self.default_settings.copy()
    
    def calculate_signal(self, market_data, ml_confidence=0.5, ml_signal="⚪ НЕЙТРАЛЬНО"):
        """Расчет сигнала MACD + RSI"""
        is_valid, message = self.validate_market_data(market_data)
        if not is_valid:
            return 'wait'
        
        if 'ohlcv' not in market_data:
            return 'wait'
        
        try:
            closes = [candle[4] for candle in market_data['ohlcv']]
            current_price = market_data['current_price']
            
            # Расчет RSI
            rsi_period = self.settings.get('rsi_period', 14)
            rsi = calculate_rsi(closes, rsi_period)
            
            # Расчет MACD
            macd_fast = self.settings.get('macd_fast', 12)
            macd_slow = self.settings.get('macd_slow', 26)
            macd_signal_period = self.settings.get('macd_signal', 9)
            
            macd, macd_signal = calculate_macd(closes, macd_fast, macd_slow, macd_signal_period)
            macd_histogram = macd - macd_signal
            
            # Получаем настройки RSI
            rsi_oversold = self.settings.get('rsi_oversold', 30)
            rsi_overbought = self.settings.get('rsi_overbought', 70)
            
            # Сигналы RSI
            rsi_buy_signal = rsi < rsi_oversold
            rsi_sell_signal = rsi > rsi_overbought
            
            # Сигналы MACD
            macd_buy_signal = macd > macd_signal and self.settings.get('use_histogram', True) and macd_histogram > 0
            macd_sell_signal = macd < macd_signal and self.settings.get('use_histogram', True) and macd_histogram < 0
            
            # Комбинированная логика
            if rsi_buy_signal and macd_buy_signal and self.position != 'long':
                log_info(f"🎯 MACD+RSI: BUY сигнал (RSI: {rsi:.1f}, MACD: {macd:.4f})")
                return 'buy'
                
            elif rsi_sell_signal and macd_sell_signal and self.position == 'long':
                log_info(f"🎯 MACD+RSI: SELL сигнал (RSI: {rsi:.1f}, MACD: {macd:.4f})")
                return 'sell'
            
            return 'wait'
            
        except Exception as e:
            log_info(f"❌ Ошибка расчета MACD+RSI: {e}")
            return 'wait'
    
    def get_settings_info(self):
        """Информация о настройках"""
        return {
            'rsi_period': f"{self.settings.get('rsi_period', 14)}",
            'rsi_oversold': f"{self.settings.get('rsi_oversold', 30)}",
            'rsi_overbought': f"{self.settings.get('rsi_overbought', 70)}",
            'macd_fast': f"{self.settings.get('macd_fast', 12)}",
            'macd_slow': f"{self.settings.get('macd_slow', 26)}",
            'macd_signal': f"{self.settings.get('macd_signal', 9)}",
            'use_histogram': 'ВКЛ' if self.settings.get('use_histogram', True) else 'ВЫКЛ'
        }