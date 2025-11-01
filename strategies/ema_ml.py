"""
УЛУЧШЕННАЯ СТРАТЕГИЯ EMA + ML С УЧЕТОМ КОМИССИЙ (ИСПРАВЛЕННАЯ)
"""
import time
from .base_strategy import BaseStrategy
from utils.logger import log_info

class EmaMlStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="📈 EMA + ML",
            description="Комбинация EMA кроссовера и Machine Learning с TP/SL и учетом комиссий"
        )
        self.default_settings = {
            'ema_threshold': 0.005,
            'ml_confidence_buy': 0.4,
            'ml_confidence_sell': 0.3,
            'take_profit_percent': 2.0,      # Тейк-профит 2%
            'stop_loss_percent': 1.5,        # Стоп-лосс 1.5%
            'trailing_stop': False,          # Трейлинг-стоп
            'exit_on_ml_signal': True,       # Выход по ML сигналу
            'min_hold_time': 300,            # Минимальное время удержания 5 мин
            'min_trade_interval': 60,        # Минимальный интервал между сделками 60 сек
            'taker_fee': 0.001,              # Комиссия тейкера 0.1% (KuCoin)
            'maker_fee': 0.001,              # Комиссия мейкера 0.1% (KuCoin)
        }
        self.settings = self.default_settings.copy()
        self.position_opened_at = None
        self.entry_price = 0  # ДОЛЖНА ФИКСИРОВАТЬСЯ ПРИ ОТКРЫТИИ!
        self.highest_price_since_entry = 0
        self.position_size = 0
        # Новый атрибут для хранения размера позиции в USDT
        self.position_size_usdt = 0
        # Время последнего сигнала (для защиты от частых сигналов)
        self.last_signal_time = 0

    def calculate_signal(self, market_data, ml_confidence=0.5, ml_signal="⚪ НЕЙТРАЛЬНО", position_size_usdt=0):
        """Расчет сигнала EMA + ML с учетом комиссий"""
        # Валидация данных
        is_valid, message = self.validate_market_data(market_data)
        if not is_valid:
            return 'wait'
            
        # Получаем актуальные настройки
        ema_threshold = self.settings.get('ema_threshold', 0.005)
        ml_buy_threshold = self.settings.get('ml_confidence_buy', 0.4)
        ml_sell_threshold = self.settings.get('ml_confidence_sell', 0.3)
        
        current_price = market_data['current_price']
        ema_diff = market_data['ema_diff_percent']
        
        # 💰 ЗАПОМИНАЕМ РАЗМЕР ПОЗИЦИИ В USDT
        self.position_size_usdt = position_size_usdt
        
        # 🔧 ЗАЩИТА ОТ ЧАСТЫХ СИГНАЛОВ (минимум 30 секунд между сигналами)
        current_time = time.time()
        time_since_last_signal = current_time - self.last_signal_time
        min_signal_interval = 30  # 30 секунд
        
        if time_since_last_signal < min_signal_interval:
            log_info(f"⏰ Слишком частый сигнал: {time_since_last_signal:.0f} сек < {min_signal_interval} сек")
            return 'wait'
        
        # 🔴 УСЛОВИЯ ЗАКРЫТИЯ ПОЗИЦИИ (если позиция открыта)
        if self.position == 'long':
            # Обновляем максимальную цену для трейлинг-стопа
            if current_price > self.highest_price_since_entry:
                self.highest_price_since_entry = current_price
                
            # 📊 РАСЧЕТ РЕАЛЬНОЙ ПРИБЫЛИ С УЧЕТОМ КОМИССИЙ
            taker_fee = self.settings.get('taker_fee', 0.001)
            gross_profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
            total_fees_percent = taker_fee * 2 * 100  # 0.1% * 2 = 0.2%
            net_profit_percent = gross_profit_percent - total_fees_percent
            
            log_info(f"📊 Прибыль: цена входа={self.entry_price:.2f}, текущая={current_price:.2f}, брутто={gross_profit_percent:.2f}%, нетто={net_profit_percent:.2f}%")
            
            # 1. Тейк-профит по ЧИСТОЙ прибыли (уже за вычетом комиссий)
            take_profit = self.settings.get('take_profit_percent', 2.0)
            if net_profit_percent >= take_profit:
                log_info(f"🎯 Take Profit сработал: +{net_profit_percent:.2f}% (чистая прибыль)")
                self.last_signal_time = current_time
                return 'sell'
                
            # 2. Стоп-лосс по ЧИСТОМУ убытку (уже с учетом комиссий)
            stop_loss = self.settings.get('stop_loss_percent', 1.5)
            if net_profit_percent <= -stop_loss:
                log_info(f"🛑 Stop Loss сработал: {net_profit_percent:.2f}% (чистый убыток)")
                self.last_signal_time = current_time
                return 'sell'
                
            # 3. Трейлинг-стоп (если включен) - тоже с учетом комиссий
            if self.settings.get('trailing_stop', False):
                trailing_stop_pct = self.settings.get('trailing_stop_percent', 1.0)
                # Учитываем комиссию при расчете отката от максимума
                current_drawdown_from_peak = ((self.highest_price_since_entry - current_price) / 
                                            self.highest_price_since_entry) * 100
                # Добавляем комиссию продажи к откату
                effective_drawdown = current_drawdown_from_peak + (taker_fee * 100)
                if effective_drawdown >= trailing_stop_pct:
                    log_info(f"📉 Trailing Stop сработал: -{effective_drawdown:.2f}% (с учетом комиссий)")
                    self.last_signal_time = current_time
                    return 'sell'
                    
            # 4. Выход по обратному ML сигналу
            if (self.settings.get('exit_on_ml_signal', True) and 
                ml_confidence < ml_sell_threshold):
                log_info(f"🤖 ML сигнал на выход: confidence={ml_confidence:.3f}")
                self.last_signal_time = current_time
                return 'sell'
                
            # 5. Выход при смене тренда EMA
            if ema_diff < -ema_threshold:
                log_info(f"📉 EMA сменила направление: {ema_diff*100:+.2f}%")
                self.last_signal_time = current_time
                return 'sell'
                
            # 6. Минимальное время удержания
            if self.position_opened_at:
                hold_time = current_time - self.position_opened_at
                min_hold = self.settings.get('min_hold_time', 300)
                if hold_time < min_hold:
                    log_info(f"⏰ Удерживаем позицию: {hold_time:.0f} сек < {min_hold} сек")
                    return 'wait'  # Не закрываем раньше минимального времени
                    
            # Если ни одно условие закрытия не сработало - удерживаем позицию
            log_info("📈 Удерживаем LONG позицию - условия закрытия не сработали")
            return 'wait'
        
        # 🟢 УСЛОВИЯ ОТКРЫТИЯ ПОЗИЦИИ (если позиция не открыта)
        elif (ema_diff > ema_threshold and 
              ml_confidence > ml_buy_threshold and
              self.position != 'long'):
            # 📈 EMA показывает восходящий тренд
            # 🤖 ML подтверждает с высокой уверенностью
            log_info(f"📈 Сигналы: EMA={ema_diff*100:+.2f}% (> {ema_threshold*100:.2f}%), ML={ml_confidence:.3f} (> {ml_buy_threshold:.1f})")
            
            # 🔧 ПРОВЕРКА: достаточно ли времени прошло с последней сделки
            if self.last_signal_time > 0:
                time_since_last = current_time - self.last_signal_time
                min_interval = self.settings.get('min_trade_interval', 60)  # Минимум 60 секунд между сделками
                if time_since_last < min_interval:
                    log_info(f"⏰ Слишком рано для новой сделки: {time_since_last:.0f} сек < {min_interval} сек")
                    return 'wait'
            
            # ЗАПОМИНАЕМ ПАРАМЕТРЫ ВХОДА (ТОЛЬКО ПРИ ОТКРЫТИИ!)
            self.entry_price = current_price  # ФИКСИРУЕМ ЦЕНУ ВХОДА
            self.highest_price_since_entry = current_price
            self.position_opened_at = current_time
            # ЗАПОМИНАЕМ РАЗМЕР ПОЗИЦИИ В USDT
            self.position_size_usdt = position_size_usdt
            
            log_info(f"🟢 Открываем LONG: цена входа={self.entry_price:.2f}, EMA={ema_diff*100:+.2f}%, ML={ml_confidence:.3f}, Размер позиции={position_size_usdt:.2f} USDT")
            self.last_signal_time = current_time
            return 'buy'
            
        # 🔵 СИГНАЛ ОЖИДАНИЯ (если условия не выполнены)
        else:
            if self.position == 'long':
                log_info("🔵 Удерживаем позицию - условия для действий отсутствуют")
            else:
                if ema_diff <= ema_threshold:
                    log_info(f"🔵 EMA недостаточно сильна: {ema_diff*100:+.2f}% <= {ema_threshold*100:.2f}%")
                if ml_confidence <= ml_buy_threshold:
                    log_info(f"🔵 ML уверенность недостаточна: {ml_confidence:.3f} <= {ml_buy_threshold:.1f}")
            
        return 'wait'

    def calculate_breakeven_price(self):
        """Расчет цены безубыточности с учетом комиссий"""
        if not self.position or self.entry_price == 0:
            return 0
        taker_fee = self.settings.get('taker_fee', 0.001)
        # Чтобы выйти в 0, цена должна покрыть комиссии за обе сделки
        # Комиссия покупки: entry_price * taker_fee
        # Комиссия продажи: breakeven_price * taker_fee  
        # Уравнение: breakeven_price - entry_price = (entry_price + breakeven_price) * taker_fee
        breakeven = self.entry_price * (1 + taker_fee) / (1 - taker_fee)
        return breakeven

    def update_position_info(self, signal, price):
        """Обновление информации о позиции при сделке"""
        if signal == 'buy':
            self.position = 'long'
            self.entry_price = price  # ФИКСИРУЕМ ЦЕНУ ВХОДА ПРИ ПОКУПКЕ
            self.highest_price_since_entry = price
            self.position_opened_at = time.time()
            # Рассчитываем и логируем цену безубыточности
            breakeven = self.calculate_breakeven_price()
            log_info(f"💰 Цена входа зафиксирована: {self.entry_price:.2f} USDT")
            log_info(f"💰 Размер позиции: {self.position_size_usdt:.2f} USDT")
            log_info(f"💰 Цена безубыточности: {breakeven:.2f} USDT (+{(breakeven - price):.2f})")
        elif signal == 'sell':
            # Логируем итоговую прибыль перед закрытием
            if self.entry_price > 0:
                gross_profit_percent = ((price - self.entry_price) / self.entry_price) * 100
                taker_fee = self.settings.get('taker_fee', 0.001)
                net_profit_percent = gross_profit_percent - (taker_fee * 2 * 100)
                net_profit_usdt = self.position_size_usdt * (net_profit_percent / 100)
                log_info(f"💰 Закрытие позиции: вход={self.entry_price:.2f}, выход={price:.2f}, прибыль={net_profit_percent:.2f}% ({net_profit_usdt:+.2f} USDT)")
            self.position = None
            self.entry_price = 0  # СБРАСЫВАЕМ ЦЕНУ ВХОДА
            self.highest_price_since_entry = 0
            self.position_opened_at = None
            self.position_size_usdt = 0  # СБРАСЫВАЕМ РАЗМЕР ПОЗИЦИИ В USDT

    def get_net_profit_percent(self, current_price):
        """Расчет чистой прибыли в процентах с учетом комиссий"""
        if not self.position or self.entry_price == 0:
            return 0
        taker_fee = self.settings.get('taker_fee', 0.001)
        gross_profit = ((current_price - self.entry_price) / self.entry_price) * 100
        total_fees = taker_fee * 2 * 100  # Комиссии за покупку и продажу
        return gross_profit - total_fees

    def get_position_info(self):
        """Получение информации о текущей позиции"""
        if self.position == 'long' and self.entry_price > 0:
            current_profit_percent = self.get_net_profit_percent(self.entry_price)
            current_profit_usdt = self.position_size_usdt * (current_profit_percent / 100)
            
            return {
                'position': self.position,
                'entry_price': self.entry_price,  # ФИКСИРОВАННАЯ ЦЕНА
                'opened_at': self.position_opened_at,
                'hold_time': time.time() - self.position_opened_at if self.position_opened_at else 0,
                'position_size_usdt': self.position_size_usdt,
                'current_profit_percent': current_profit_percent,
                'current_profit_usdt': current_profit_usdt,
                'breakeven_price': self.calculate_breakeven_price()
            }
        return None

    def get_settings_info(self):
        """Информация о настройках"""
        breakeven_info = ""
        if self.position and self.entry_price > 0:
            breakeven = self.calculate_breakeven_price()
            breakeven_info = f"\n💡 Цена безубыточности: {breakeven:.2f}"
        return {
            'ema_threshold': f"{self.settings.get('ema_threshold', 0.005)*100:.2f}%",
            'ml_confidence_buy': f"{self.settings.get('ml_confidence_buy', 0.4):.1f}",
            'ml_confidence_sell': f"{self.settings.get('ml_confidence_sell', 0.3):.1f}",
            'take_profit': f"{self.settings.get('take_profit_percent', 2.0):.1f}%",
            'stop_loss': f"{self.settings.get('stop_loss_percent', 1.5):.1f}%",
            'commission': f"{self.settings.get('taker_fee', 0.001)*100:.1f}%",
            'trailing_stop': '✅ ВКЛ' if self.settings.get('trailing_stop', False) else '❌ ВЫКЛ',
            'min_hold_time': f"{self.settings.get('min_hold_time', 300)//60} мин",
            'min_trade_interval': f"{self.settings.get('min_trade_interval', 60)} сек"
        }