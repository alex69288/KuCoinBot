"""
РЕАЛЬНАЯ СТРАТЕГИЯ PRICE ACTION С ПОДДЕРЖКОЙ/СОПРОТИВЛЕНИЕМ
"""
import numpy as np
from .base_strategy import BaseStrategy
from utils.logger import log_info

class PriceActionStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="⚡ Price Action",
            description="Торговля по чистому движению цены и ключевым уровням поддержки/сопротивления"
        )
        self.default_settings = {
            'min_move_percent': 0.15,
            'use_support_resistance': True,
            'volume_confirmation': False,
            'trend_confirmation': True,
            'support_resistance_lookback': 50,  # Период для поиска уровней
            'level_touch_threshold': 0.001,     # 0.1% от уровня
        }
        self.settings = self.default_settings.copy()
        self.last_price = None
        self.support_levels = []
        self.resistance_levels = []
        self.price_history = []
    
    def calculate_signal(self, market_data, ml_confidence=0.5, ml_signal="⚪ НЕЙТРАЛЬНО"):
        """Расчет сигнала Price Action с реальными уровнями поддержки/сопротивления"""
        is_valid, message = self.validate_market_data(market_data)
        if not is_valid:
            return 'wait'
        
        current_price = market_data['current_price']
        
        # Добавляем цену в историю
        self.price_history.append(current_price)
        if len(self.price_history) > 100:  # Ограничиваем размер истории
            self.price_history.pop(0)
        
        # Инициализация последней цены
        if self.last_price is None:
            self.last_price = current_price
            return 'wait'
        
        # Расчет изменения цены
        price_change = current_price - self.last_price
        price_change_percent = (price_change / self.last_price) * 100
        
        min_move = self.settings.get('min_move_percent', 0.15)
        
        # РЕАЛЬНЫЙ АЛГОРИТМ: Обновляем уровни поддержки/сопротивления
        if self.settings.get('use_support_resistance', True):
            self._calculate_real_support_resistance()
        
        # Логика покупки (отскок от поддержки)
        if (self._is_near_support(current_price) and 
            price_change_percent > min_move and 
            self._is_uptrend_confirmed(market_data) and
            self.position != 'long'):
            
            self.last_price = current_price
            log_info(f"⚡ Price Action BUY: отскок от поддержки +{price_change_percent:.2f}%")
            return 'buy'
            
        # Логика продажи (отскок от сопротивления)
        elif (self._is_near_resistance(current_price) and 
              price_change_percent < -min_move and 
              self._is_downtrend_confirmed(market_data) and
              self.position == 'long'):
            
            self.last_price = current_price
            log_info(f"⚡ Price Action SELL: отскок от сопротивления {price_change_percent:.2f}%")
            return 'sell'
        
        self.last_price = current_price
        return 'wait'
    
    def _calculate_real_support_resistance(self):
        """РЕАЛЬНЫЙ алгоритм расчета уровней поддержки и сопротивления"""
        if len(self.price_history) < 20:
            return
        
        prices = np.array(self.price_history)
        
        # Находим локальные минимумы и максимумы
        local_minima = []
        local_maxima = []
        
        for i in range(1, len(prices) - 1):
            # Локальный минимум
            if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                local_minima.append(prices[i])
            # Локальный максимум
            elif prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                local_maxima.append(prices[i])
        
        # Группируем близкие уровни (кластеризация)
        self.support_levels = self._cluster_levels(local_minima, threshold=0.005)  # 0.5%
        self.resistance_levels = self._cluster_levels(local_maxima, threshold=0.005)
        
        # Сортируем и берем ближайшие уровни
        self.support_levels.sort(reverse=True)  # От большего к меньшему
        self.resistance_levels.sort()           # От меньшего к большему
        
        # Ограничиваем количество уровней
        self.support_levels = self.support_levels[:5]
        self.resistance_levels = self.resistance_levels[:5]
    
    def _cluster_levels(self, levels, threshold=0.005):
        """Кластеризация близких уровней"""
        if not levels:
            return []
        
        clusters = []
        levels_sorted = sorted(levels)
        
        current_cluster = [levels_sorted[0]]
        
        for price in levels_sorted[1:]:
            if abs(price - current_cluster[-1]) / current_cluster[-1] <= threshold:
                current_cluster.append(price)
            else:
                # Добавляем среднее значение кластера
                clusters.append(np.mean(current_cluster))
                current_cluster = [price]
        
        if current_cluster:
            clusters.append(np.mean(current_cluster))
        
        return clusters
    
    def _is_near_support(self, current_price):
        """Проверка близости к уровню поддержки"""
        if not self.support_levels:
            return False
        
        threshold = self.settings.get('level_touch_threshold', 0.001)
        for level in self.support_levels:
            if abs(current_price - level) / level <= threshold:
                log_info(f"⚡ Near support: {current_price:.2f} ~ {level:.2f}")
                return True
        return False
    
    def _is_near_resistance(self, current_price):
        """Проверка близости к уровню сопротивления"""
        if not self.resistance_levels:
            return False
        
        threshold = self.settings.get('level_touch_threshold', 0.001)
        for level in self.resistance_levels:
            if abs(current_price - level) / level <= threshold:
                log_info(f"⚡ Near resistance: {current_price:.2f} ~ {level:.2f}")
                return True
        return False
    
    def _is_uptrend_confirmed(self, market_data):
        """Подтверждение восходящего тренда"""
        if not self.settings.get('trend_confirmation', True):
            return True
        
        ema_bullish = market_data['ema_diff_percent'] > 0
        price_above_ema = market_data['current_price'] > market_data['fast_ema']
        
        return ema_bullish and price_above_ema
    
    def _is_downtrend_confirmed(self, market_data):
        """Подтверждение нисходящего тренда"""
        if not self.settings.get('trend_confirmation', True):
            return True
        
        ema_bearish = market_data['ema_diff_percent'] < 0
        price_below_ema = market_data['current_price'] < market_data['slow_ema']
        
        return ema_bearish and price_below_ema
    
    def get_settings_info(self):
        """Информация о настройках"""
        support_info = f"{len(self.support_levels)} ур." if self.support_levels else "нет"
        resistance_info = f"{len(self.resistance_levels)} ур." if self.resistance_levels else "нет"
        
        return {
            'min_move_percent': f"{self.settings.get('min_move_percent', 0.15):.2f}%",
            'support_resistance': '✅ ВКЛ' if self.settings.get('use_support_resistance', True) else '❌ ВЫКЛ',
            'support_levels': support_info,
            'resistance_levels': resistance_info,
            'trend_confirmation': '✅ ВКЛ' if self.settings.get('trend_confirmation', True) else '❌ ВЫКЛ',
            'volume_confirmation': '✅ ВКЛ' if self.settings.get('volume_confirmation', False) else '❌ ВЫКЛ'
        }