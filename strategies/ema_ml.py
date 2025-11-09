"""
УЛУЧШЕННАЯ СТРАТЕГИЯ EMA + ML С УЧЕТОМ КОМИССИЙ И TAKE PROFIT В USDT
"""
import time
from .base_strategy import BaseStrategy
from utils.logger import log_info, log_error

class EmaMlStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="📈 EMA + ML",
            description="Комбинация EMA кроссовера и Machine Learning с TP/SL и учетом комиссий"
        )
        self.default_settings = {
            'ema_fast_period': 9,            # Быстрая EMA (по умолчанию 9)
            'ema_slow_period': 21,           # Медленная EMA (по умолчанию 21)
            'ema_threshold': 0.0025,         # 0.25% по умолчанию
            'ml_confidence_buy': 0.4,
            'ml_confidence_sell': 0.3,
            'take_profit_percent': 0.05,    # 0.05% по умолчанию (учитываются комиссии)
            'take_profit_usdt': 0.0,         # 0 = режим процентов, >0 = режим USDT
            'stop_loss_percent': 1.5,
            'trailing_stop': False,
            'exit_on_ml_signal': True,
            'min_hold_time': 300,
            'min_trade_interval': 60,
            'taker_fee': 0.001,              # KuCoin taker fee = 0.1%
        }
        self.settings = self.default_settings.copy()
        
        # 🔧 ЗАГРУЖАЕМ СОХРАНЕННЫЕ НАСТРОЙКИ ПРИ ИНИЦИАЛИЗАЦИИ
        try:
            from config.settings import SettingsManager
            # Создаем временный менеджер настроек для загрузки
            temp_settings = SettingsManager()
            last_tp_usdt = temp_settings.ml_settings.get('last_take_profit_usdt')
            last_tp_percent = temp_settings.ml_settings.get('last_take_profit_percent')
            last_sl_percent = temp_settings.ml_settings.get('last_stop_loss_percent', 1.5)  # 🔧 Загружаем Stop Loss
            
            # Загружаем EMA настройки
            last_ema_fast = temp_settings.ml_settings.get('last_ema_fast_period', 9)
            last_ema_slow = temp_settings.ml_settings.get('last_ema_slow_period', 21)
            last_ema_threshold = temp_settings.ml_settings.get('last_ema_threshold', 0.0025)
            
            if last_tp_usdt is not None and last_tp_usdt > 0:
                self.settings['take_profit_usdt'] = last_tp_usdt
                self.settings['take_profit_percent'] = 0.0
                log_info(f"✅ Загружен сохраненный Take Profit: {last_tp_usdt:.4f} USDT")
            elif last_tp_percent is not None and last_tp_percent != 2.0:
                self.settings['take_profit_percent'] = last_tp_percent
                log_info(f"✅ Загружен сохраненный Take Profit: {last_tp_percent:.4f}%")
            
            # 🔧 Загружаем Stop Loss
            if last_sl_percent is not None:
                self.settings['stop_loss_percent'] = last_sl_percent
                log_info(f"✅ Загружен сохраненный Stop Loss: {last_sl_percent:.2f}%")
            
            # Загружаем EMA настройки
            if last_ema_fast is not None:
                self.settings['ema_fast_period'] = last_ema_fast
                log_info(f"✅ Загружен сохраненный EMA Fast: {last_ema_fast}")
            if last_ema_slow is not None:
                self.settings['ema_slow_period'] = last_ema_slow
                log_info(f"✅ Загружен сохраненный EMA Slow: {last_ema_slow}")
            if last_ema_threshold is not None:
                self.settings['ema_threshold'] = last_ema_threshold
                log_info(f"✅ Загружен сохраненный EMA Threshold: {last_ema_threshold*100:.2f}%")
                
        except Exception as e:
            log_info(f"⚠️ Не удалось загрузить сохраненные настройки: {e}")
    
        self.position_opened_at = None
        self.entry_price = 0
        self.highest_price_since_entry = 0
        self.position_size_usdt = 0
        self.last_signal_time = 0

    def calculate_signal(self, market_data, ml_confidence=0.5, ml_signal="⚪ НЕЙТРАЛЬНО", position_size_usdt=0):
        is_valid, message = self.validate_market_data(market_data)
        if not is_valid:
            return 'wait'

        current_price = market_data['current_price']
        ema_diff = market_data['ema_diff_percent']
        current_time = time.time()

        # Защита от частых сигналов
        if current_time - self.last_signal_time < 30:
            return 'wait'

        # Сохраняем размер позиции в USDT
        self.position_size_usdt = position_size_usdt

        # === ЗАКРЫТИЕ ПОЗИЦИИ ===
        if self.position == 'long':
            taker_fee = self.settings.get('taker_fee', 0.001)
            
            # 🔧 ИСПРАВЛЕНИЕ: Расчет прибыли в зависимости от режима
            take_profit_usdt = self.settings.get('take_profit_usdt', 0.0)
            take_profit_percent = self.settings.get('take_profit_percent', 2.0)
            
            if take_profit_usdt > 0:
                # 🔹 РЕЖИМ USDT (включая маленькие значения)
                current_profit_usdt = (current_price - self.entry_price) / self.entry_price * self.position_size_usdt
                fees_usdt = self.position_size_usdt * taker_fee * 2
                net_profit_usdt = current_profit_usdt - fees_usdt
                
                # 🔧 ПОДДЕРЖКА МАЛЕНЬКИХ ЗНАЧЕНИЙ TP
                if net_profit_usdt >= take_profit_usdt:
                    # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ
                    if take_profit_usdt < 0.1:
                        log_info(f"🎯 Take Profit (USDT) сработал: +{net_profit_usdt:.4f} USDT (цель: {take_profit_usdt:.4f} USDT)")
                    else:
                        log_info(f"🎯 Take Profit (USDT) сработал: +{net_profit_usdt:.2f} USDT (цель: {take_profit_usdt:.2f} USDT)")
                    self.last_signal_time = current_time
                    return 'sell'
                    
            else:
                # 🔹 РЕЖИМ ПРОЦЕНТОВ (включая маленькие значения)
                gross_profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
                total_fees_percent = taker_fee * 2 * 100
                net_profit_percent = gross_profit_percent - total_fees_percent
                
                # 🔧 ПОДДЕРЖКА МАЛЕНЬКИХ ЗНАЧЕНИЙ TP
                if net_profit_percent >= take_profit_percent:
                    # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ
                    if take_profit_percent < 0.1:
                        log_info(f"🎯 Take Profit (%) сработал: +{net_profit_percent:.4f}% (цель: {take_profit_percent:.4f}%)")
                    else:
                        log_info(f"🎯 Take Profit (%) сработал: +{net_profit_percent:.2f}% (цель: {take_profit_percent:.2f}%)")
                    self.last_signal_time = current_time
                    return 'sell'

            # Stop Loss (в процентах для обоих режимов)
            stop_loss = self.settings.get('stop_loss_percent', 1.5)
            current_profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
            # 🔧 ИСПРАВЛЕНИЕ: Stop Loss проверяется по валовой прибыли (цене), а не по чистой
            # Комиссии учитываются только при отображении результата
            net_profit_percent_sl = current_profit_percent - (taker_fee * 2 * 100)
            
            # 🔧 ОТЛАДКА: Логируем значения для диагностики
            # log_info(f"🔍 Stop Loss проверка: текущая прибыль={current_profit_percent:.2f}%, stop_loss={stop_loss:.2f}%, условие={current_profit_percent <= -stop_loss}")
            
            # Проверяем Stop Loss по валовой прибыли (падение цены на stop_loss%)
            if current_profit_percent <= -stop_loss:
                # 🔧 ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ УБЫТКОВ
                if abs(net_profit_percent_sl) < 0.1:
                    log_info(f"🛑 Stop Loss сработал: {net_profit_percent_sl:.4f}% (цена упала на {abs(current_profit_percent):.2f}%, установлен SL: {stop_loss:.2f}%)")
                else:
                    log_info(f"🛑 Stop Loss сработал: {net_profit_percent_sl:.2f}% (цена упала на {abs(current_profit_percent):.2f}%, установлен SL: {stop_loss:.2f}%)")
                self.last_signal_time = current_time
                return 'sell'

            # Trailing Stop (только для процентов)
            if self.settings.get('trailing_stop', False):
                trailing_stop_pct = 1.0
                drawdown = ((self.highest_price_since_entry - current_price) / self.highest_price_since_entry) * 100
                effective_drawdown = drawdown + (taker_fee * 100)
                if effective_drawdown >= trailing_stop_pct:
                    # 🔧 ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ПРОСАДОК
                    if effective_drawdown < 0.1:
                        log_info(f"📉 Trailing Stop сработал: -{effective_drawdown:.4f}%")
                    else:
                        log_info(f"📉 Trailing Stop сработал: -{effective_drawdown:.2f}%")
                    self.last_signal_time = current_time
                    return 'sell'

            # Обновляем максимум
            if current_price > self.highest_price_since_entry:
                self.highest_price_since_entry = current_price

            # 🔧 ДИАГНОСТИЧЕСКОЕ ЛОГИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ (только при близости к TP или проблемах)
            # Логируем только если близко к TP (в пределах 0.02%) или убыток более 0.5%
            if take_profit_usdt > 0:
                # Режим USDT
                remaining_to_tp = max(0, take_profit_usdt - net_profit_usdt)
                if remaining_to_tp < take_profit_usdt * 0.4 or net_profit_usdt < -0.005:  # Близко к TP или убыток
                    if remaining_to_tp < 0.1:
                        log_info(f"📊 Диагностика TP (USDT): прибыль {net_profit_usdt:.4f} USDT, до TP {remaining_to_tp:.4f} USDT")
                    else:
                        log_info(f"📊 Диагностика TP (USDT): прибыль {net_profit_usdt:.2f} USDT, до TP {remaining_to_tp:.2f} USDT")
            else:
                # Режим процентов
                remaining_to_tp = max(0, take_profit_percent - net_profit_percent)
                # Логируем только если близко к TP (в пределах 40% от TP) или убыток более 0.5%
                if remaining_to_tp < take_profit_percent * 0.4 or net_profit_percent < -0.5:
                    if remaining_to_tp < 0.1:
                        log_info(f"📊 Диагностика TP (%): прибыль {net_profit_percent:.4f}%, до TP {remaining_to_tp:.4f}%")
                    else:
                        log_info(f"📊 Диагностика TP (%): прибыль {net_profit_percent:.2f}%, до TP {remaining_to_tp:.2f}%")

            return 'wait'

        # === ОТКРЫТИЕ ПОЗИЦИИ ===
        elif (ema_diff > self.settings['ema_threshold'] and
              ml_confidence > self.settings['ml_confidence_buy'] and
              self.position != 'long'):

            # 🔧 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: убеждаемся, что позиция действительно не открыта
            if self.position == 'long':
                log_info(f"⚠️ Стратегия: попытка открыть позицию, но position уже 'long'. entry_price={self.entry_price:.2f}")
                return 'wait'

            if self.last_signal_time > 0 and (current_time - self.last_signal_time) < self.settings['min_trade_interval']:
                return 'wait'

            self.entry_price = current_price
            self.highest_price_since_entry = current_price
            self.position_opened_at = current_time
            self.position_size_usdt = position_size_usdt
            
            # 🔧 Логирование в правильном режиме с поддержкой маленьких значений
            take_profit_usdt = self.settings.get('take_profit_usdt', 0.0)
            if take_profit_usdt > 0:
                # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ
                if take_profit_usdt < 0.1:
                    log_info(f"🟢 Открываем LONG: цена={current_price:.2f}, TP={take_profit_usdt:.4f} USDT, размер={position_size_usdt:.2f} USDT")
                else:
                    log_info(f"🟢 Открываем LONG: цена={current_price:.2f}, TP={take_profit_usdt:.2f} USDT, размер={position_size_usdt:.2f} USDT")
            else:
                take_profit_percent = self.settings.get('take_profit_percent', 2.0)
                # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ
                if take_profit_percent < 0.1:
                    log_info(f"🟢 Открываем LONG: цена={current_price:.2f}, TP={take_profit_percent:.4f}%, размер={position_size_usdt:.2f} USDT")
                else:
                    log_info(f"🟢 Открываем LONG: цена={current_price:.2f}, TP={take_profit_percent:.2f}%, размер={position_size_usdt:.2f} USDT")
            
            self.last_signal_time = current_time
            return 'buy'

        return 'wait'

    def update_position_info(self, signal, price):
        if signal == 'buy':
            self.position = 'long'
            self.entry_price = price
            self.highest_price_since_entry = price
            self.position_opened_at = time.time()
        elif signal == 'sell':
            self.position = None
            self.entry_price = 0
            self.position_size_usdt = 0

    def get_settings_info(self):
        """Информация о настройках с правильным отображением режима TP"""
        take_profit_usdt = self.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = self.settings.get('take_profit_percent', 2.0)
        
        # 🔹 ПРАВИЛЬНОЕ ОПРЕДЕЛЕНИЕ РЕЖИМА
        if take_profit_usdt > 0:
            # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ
            if take_profit_usdt < 0.1:
                take_profit_display = f"{take_profit_usdt:.4f} USDT"
            else:
                take_profit_display = f"{take_profit_usdt:.2f} USDT"
            tp_mode = "USDT"
        else:
            # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ДЛЯ МАЛЕНЬКИХ ЗНАЧЕНИЙ
            if take_profit_percent < 0.1:
                take_profit_display = f"{take_profit_percent:.4f}%"
            else:
                take_profit_display = f"{take_profit_percent:.2f}%"
            tp_mode = "проценты"
            
        return {
            'take_profit': take_profit_display,
            'tp_mode': tp_mode,
            'stop_loss': f"{self.settings.get('stop_loss_percent', 1.5):.1f}%",
            'trailing_stop': '✅ ВКЛ' if self.settings.get('trailing_stop', False) else '❌ ВЫКЛ',
            'min_hold_time': f"{self.settings.get('min_hold_time', 300)//60} мин",
        }

    def get_current_profit_info(self, current_price):
        """Получение информации о текущей прибыли с поддержкой маленьких значений"""
        if not self.position == 'long' or self.entry_price == 0:
            return "Нет открытой позиции"
        
        take_profit_usdt = self.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = self.settings.get('take_profit_percent', 2.0)
        taker_fee = self.settings.get('taker_fee', 0.001)
        
        if take_profit_usdt > 0:
            # Режим USDT
            current_profit_usdt = (current_price - self.entry_price) / self.entry_price * self.position_size_usdt
            fees_usdt = self.position_size_usdt * taker_fee * 2
            net_profit_usdt = current_profit_usdt - fees_usdt
            remaining_to_tp = max(0, take_profit_usdt - net_profit_usdt)
            
            # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ
            profit_format = ".4f" if abs(net_profit_usdt) < 0.1 else ".2f"
            tp_format = ".4f" if take_profit_usdt < 0.1 else ".2f"
            remaining_format = ".4f" if remaining_to_tp < 0.1 else ".2f"
            
            return {
                'mode': 'USDT',
                'current_profit': net_profit_usdt,
                'current_profit_formatted': f"{net_profit_usdt:{profit_format}} USDT",
                'take_profit': take_profit_usdt,
                'take_profit_formatted': f"{take_profit_usdt:{tp_format}} USDT",
                'remaining_to_tp': remaining_to_tp,
                'remaining_formatted': f"{remaining_to_tp:{remaining_format}} USDT",
                'fees': fees_usdt
            }
        else:
            # Режим процентов
            current_profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
            total_fees_percent = taker_fee * 2 * 100
            net_profit_percent = current_profit_percent - total_fees_percent
            remaining_to_tp = max(0, take_profit_percent - net_profit_percent)
            current_profit_usdt = self.position_size_usdt * (net_profit_percent / 100)
            
            # 🔧 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ
            profit_format = ".4f" if abs(net_profit_percent) < 0.1 else ".2f"
            tp_format = ".4f" if take_profit_percent < 0.1 else ".2f"
            remaining_format = ".4f" if remaining_to_tp < 0.1 else ".2f"
            
            return {
                'mode': 'percent',
                'current_profit': net_profit_percent,
                'current_profit_formatted': f"{net_profit_percent:{profit_format}}%",
                'current_profit_usdt': current_profit_usdt,
                'current_profit_usdt_formatted': f"{current_profit_usdt:.4f} USDT",
                'take_profit': take_profit_percent,
                'take_profit_formatted': f"{take_profit_percent:{tp_format}}%",
                'remaining_to_tp': remaining_to_tp,
                'remaining_formatted': f"{remaining_to_tp:{remaining_format}}%",
                'fees': total_fees_percent
            }

    def save_settings_to_manager(self, settings_manager=None):
        """Сохранение настроек в менеджер настроек
        
        Args:
            settings_manager: Опциональный менеджер настроек. Если не указан, создается новый (не рекомендуется).
        """
        try:
            # 🔧 ИСПОЛЬЗУЕМ ПЕРЕДАННЫЙ МЕНЕДЖЕР НАСТРОЕК ИЛИ СОЗДАЕМ НОВЫЙ (для обратной совместимости)
            if settings_manager is None:
                from config.settings import SettingsManager
                settings_manager = SettingsManager()
            
            # Сохраняем настройки Take Profit
            settings_manager.ml_settings['last_take_profit_usdt'] = self.settings.get('take_profit_usdt', 0.0)
            settings_manager.ml_settings['last_take_profit_percent'] = self.settings.get('take_profit_percent', 2.0)
            settings_manager.ml_settings['last_stop_loss_percent'] = self.settings.get('stop_loss_percent', 1.5)
            
            # Сохраняем EMA настройки
            settings_manager.ml_settings['last_ema_fast_period'] = self.settings.get('ema_fast_period', 9)
            settings_manager.ml_settings['last_ema_slow_period'] = self.settings.get('ema_slow_period', 21)
            settings_manager.ml_settings['last_ema_threshold'] = self.settings.get('ema_threshold', 0.0025)
            
            # Сохраняем настройки
            settings_manager.save_settings(sync_from_strategy=False)  # Не синхронизируем, так как мы уже обновили ml_settings
            log_info("💾 Настройки стратегии сохранены")
            
        except Exception as e:
            log_info(f"⚠️ Не удалось сохранить настройки стратегии: {e}")

    def update_take_profit_settings(self, take_profit_usdt=None, take_profit_percent=None):
        """Обновление настроек Take Profit с сохранением"""
        if take_profit_usdt is not None:
            self.settings['take_profit_usdt'] = take_profit_usdt
        if take_profit_percent is not None:
            self.settings['take_profit_percent'] = take_profit_percent
            
        # Сохраняем настройки
        self.save_settings_to_manager()

    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        self.settings = self.default_settings.copy()
        log_info("🔄 Настройки стратегии сброшены к значениям по умолчанию")
        
        # Сохраняем сброшенные настройки
        self.save_settings_to_manager()
    
    def set_scalping_settings(self):
        """Установка оптимальных настроек для скальпинга (частые сделки)"""
        # Быстрые EMA для более чувствительных сигналов
        self.settings['ema_fast_period'] = 5   # Быстрая EMA (было 9)
        self.settings['ema_slow_period'] = 13  # Медленная EMA (было 21)
        
        # Низкий порог для большего количества сигналов
        self.settings['ema_threshold'] = 0.001  # 0.1% (было 0.25%)
        
        # Маленький Take Profit для быстрых выходов
        self.settings['take_profit_percent'] = 0.03  # 0.03% (было 0.05%)
        self.settings['take_profit_usdt'] = 0.0  # Используем проценты
        
        # Более строгий Stop Loss для скальпинга
        self.settings['stop_loss_percent'] = 1.0  # 1.0% (было 1.5%)
        
        # Короткое время удержания для частых сделок
        self.settings['min_hold_time'] = 60  # 1 минута (было 5 минут)
        self.settings['min_trade_interval'] = 30  # 30 секунд (было 60)
        
        log_info("⚡ Установлены настройки для скальпинга (частые сделки)")
        log_info(f"   📊 EMA: {self.settings['ema_fast_period']}/{self.settings['ema_slow_period']}")
        log_info(f"   🎯 Threshold: {self.settings['ema_threshold']*100:.2f}%")
        log_info(f"   💰 Take Profit: {self.settings['take_profit_percent']:.3f}%")
        log_info(f"   🛑 Stop Loss: {self.settings['stop_loss_percent']:.1f}%")
        log_info(f"   ⏰ Min Hold Time: {self.settings['min_hold_time']} сек")
        
        # Сохраняем настройки
        self.save_settings_to_manager()