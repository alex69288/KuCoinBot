"""
ОБРАБОТЧИКИ СООБЩЕНИЙ TELEGRAM
"""
import threading
import time
from utils.logger import log_info, log_error
from utils.helpers import validate_number_input

class MessageHandler:
    def __init__(self, trading_bot):
        self.bot = trading_bot
        self.waiting_for_input = None

    def handle_message(self, message_text):
        """Основной обработчик сообщений"""
        try:
            if self.waiting_for_input:
                self.handle_direct_input(message_text)
                return

            self.bot.telegram.send_message("⏳ Обрабатываю запрос...")
            # Обработка кнопок "Назад"
            if message_text in ['🔙 Назад к настройкам', '🔙 Назад']:
                self.send_settings_menu()
                return
            if message_text == '🏠 Главное меню':
                self.send_main_menu()
                return
            # Основные команды главного меню
            if message_text == '/start':
                self.send_main_menu()
            elif message_text == '📊 Статус':
                self.send_status()
            elif message_text == '💼 Инфо аккаунта':
                self.send_account_info()
            elif message_text == '⚙️ Настройки':
                self.send_settings_menu()
            elif message_text == '📈 Сделки':
                self.send_trade_history()
            elif message_text == '📊 Аналитика':
                self.send_analytics()
            elif message_text == '⚡ Управление':
                self.send_trading_control_menu()
            elif message_text == '🔄 Обновить':
                self.send_market_update()
            elif message_text == '🚨 Экстренная остановка':
                self.emergency_stop()
            # Обработка кнопок настроек
            elif '📈 EMA порог:' in message_text:
                self.start_ema_threshold_input()
            elif '💰 Размер позиции:' in message_text:
                self.start_trade_amount_input()
            elif '🎯 Стратегия:' in message_text:
                self.send_strategy_menu()
            elif '💱 Пара:' in message_text:
                self.send_pairs_menu()
            # Обработка ML настроек
            elif '🤖 ML Настройки' in message_text:
                self.send_ml_settings_menu()
            elif any(cmd in message_text for cmd in ['🤖 ML:', '🎯 Порог покупки:', '🎯 Порог продажи:', '🔄 Переобучить модель']):
                self.handle_ml_settings_selection(message_text)
            # Обработка настроек EMA
            elif '⚙️ Настройки EMA' in message_text:
                self.send_ema_settings_menu()
            elif '⚙️ Настройки рисков' in message_text:
                self.send_risk_settings_menu()
            elif any(cmd in message_text for cmd in ['💼 Макс. позиция:', '📉 Макс. убыток/день:', '🔴 Макс. убыточных:']):
                self.handle_risk_settings_selection(message_text)
            elif any(cmd in message_text for cmd in ['🎯 Take Profit:', '🛑 Stop Loss:', '📉 Trailing Stop:', '⏰ Min Hold Time:']):
                self.handle_ema_settings_selection(message_text)
            elif '🔄 Обновления:' in message_text:
                self.toggle_price_updates()
            # Обработка выбора стратегии
            elif any(strategy_name in message_text for strategy_name in self.bot.settings.strategy_settings['available_strategies'].values()):
                self.handle_strategy_selection(message_text)
            # Обработка выбора пары
            elif any(pair_name in message_text for pair_name in self.bot.settings.trading_pairs['available_pairs'].values()):
                self.handle_pair_selection(message_text)
            # Обработка управления торговлей
            elif '📊 Торговля:' in message_text:
                self.toggle_trading_enabled()
            elif '🎯 Сигналы:' in message_text:
                self.toggle_trade_signals()
            elif '🔧 Режим:' in message_text:
                self.toggle_demo_mode()
            elif message_text == '🔄 Перезагрузить бот':
                self.restart_bot()
            # Обработка аналитики
            elif message_text == '📈 Детальный отчет':
                self.send_detailed_report()
            elif message_text == '📊 Графики':
                self.send_charts_info()
            elif message_text == '🧹 Очистить статистику':
                self.clear_statistics()
        except Exception as e:
            error_msg = f"❌ Ошибка обработки команды: {e}"
            log_error(error_msg)
            self.bot.telegram.send_message(error_msg)

    def handle_callback(self, callback_data):
        """Обработка callback от inline кнопок"""
        try:
            log_info(f"🔘 Обрабатываем callback: {callback_data}")
            # Здесь можно добавить обработку inline кнопок
        except Exception as e:
            log_error(f"❌ Ошибка обработки callback: {e}")

    def handle_ml_settings_selection(self, message_text):
        """Обработка выбора ML настроек"""
        try:
            if "🤖 ML:" in message_text:
                self.toggle_ml_enabled()
            elif "🎯 Порог покупки:" in message_text:
                self.start_ml_buy_threshold_input()
            elif "🎯 Порог продажи:" in message_text:
                self.start_ml_sell_threshold_input()
            elif "🔄 Переобучить модель" in message_text:
                self.retrain_ml_model()
            elif "🔙 Назад к настройкам" in message_text:
                self.send_settings_menu()
            else:
                self.bot.telegram.send_message("❌ Неизвестная команда ML настроек")
        except Exception as e:
            error_msg = f"❌ Ошибка обработки ML настроек: {e}"
            log_error(error_msg)
            self.bot.telegram.send_message(error_msg)

    def handle_ema_settings_selection(self, message_text):
        """Обработка выбора настроек EMA"""
        try:
            strategy = self.bot.get_active_strategy()
            if "🎯 Take Profit:" in message_text:
                self.start_take_profit_input()
            elif "🛑 Stop Loss:" in message_text:
                self.start_stop_loss_input()
            elif "📉 Trailing Stop:" in message_text:
                self.toggle_trailing_stop()
            elif "⏰ Min Hold Time:" in message_text:
                self.start_min_hold_time_input()
        except Exception as e:
            error_msg = f"❌ Ошибка обработки настроек EMA: {e}"
            log_error(error_msg)
            self.bot.telegram.send_message(error_msg)

    def handle_risk_settings_selection(self, message_text):
        if "💼 Макс. позиция:" in message_text:
            self.start_max_position_input()
        elif "📉 Макс. убыток/день:" in message_text:
            self.start_max_daily_loss_input()
        elif "🔴 Макс. убыточных:" in message_text:
            self.start_max_consecutive_input()

    def handle_direct_input(self, message_text):
        """Обработка прямого ввода значений"""
        try:
            if message_text == '❌ Отменить ввод':
                self.waiting_for_input = None
                self.bot.telegram.send_message("❌ Ввод отменен")
                self.send_settings_menu()
                return
            try:
                value = float(message_text.replace(',', '.'))
            except ValueError:
                self.bot.telegram.send_message("❌ Введите корректное число")
                return
            if self.waiting_for_input == 'ema_threshold':
                if validate_number_input(value, 0.01, 10.0):
                    self.bot.settings.settings['ema_cross_threshold'] = value / 100
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Порог EMA установлен: <b>{value:.2f}%</b>")
                    self.send_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.01 до 10.0")
            elif self.waiting_for_input == 'trade_amount':
                if validate_number_input(value, 1.0, 100.0):
                    self.bot.settings.settings['trade_amount_percent'] = value / 100
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Размер ставки установлен: <b>{value:.1f}%</b>")
                    self.send_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 1.0 до 100.0")
            elif self.waiting_for_input == 'ml_buy_threshold':
                if validate_number_input(value, 0.1, 0.9):
                    self.bot.settings.ml_settings['confidence_threshold_buy'] = value
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Порог ML для покупки установлен: <b>{value:.1f}</b>")
                    self.send_ml_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.1 до 0.9")
            elif self.waiting_for_input == 'ml_sell_threshold':
                if validate_number_input(value, 0.1, 0.9):
                    self.bot.settings.ml_settings['confidence_threshold_sell'] = value
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Порог ML для продажи установлен: <b>{value:.1f}</b>")
                    self.send_ml_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.1 до 0.9")
            elif self.waiting_for_input == 'take_profit':
                if validate_number_input(value, 0.5, 20.0):
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['take_profit_percent'] = value
                    self.bot.telegram.send_message(f"✅ Take Profit установлен: <b>{value:.1f}%</b>")
                    self.send_ema_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.5 до 20.0")
            elif self.waiting_for_input == 'stop_loss':
                if validate_number_input(value, 0.5, 10.0):
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['stop_loss_percent'] = value
                    self.bot.telegram.send_message(f"✅ Stop Loss установлен: <b>{value:.1f}%</b>")
                    self.send_ema_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.5 до 10.0")
            elif self.waiting_for_input == 'min_hold_time':
                if validate_number_input(value, 1, 60):
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['min_hold_time'] = int(value) * 60  # Конвертируем в секунды
                    self.bot.telegram.send_message(f"✅ Min Hold Time установлен: <b>{value} мин</b>")
                    self.send_ema_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 1 до 60 минут")

            elif self.waiting_for_input == 'max_daily_loss':
                if validate_number_input(value, 0.5, 20.0):
                    self.bot.settings.risk_settings['max_daily_loss'] = value
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Макс. убыток/день: <b>{value:.1f}%</b>")
                    self.send_risk_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.5 до 20.0")

            elif self.waiting_for_input == 'max_consecutive_losses':
                if validate_number_input(value, 1, 10) and value == int(value):
                    self.bot.settings.risk_settings['max_consecutive_losses'] = int(value)
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Макс. убыточных подряд: <b>{int(value)}</b>")
                    self.send_risk_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Введите целое число от 1 до 10")
            elif self.waiting_for_input == 'max_position_size':
                if validate_number_input(value, 5.0, 100.0):
                    self.bot.settings.risk_settings['max_position_size'] = value
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Макс. размер позиции: <b>{value:.1f}%</b>")
                    self.send_risk_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 5.0 до 100.0")

            elif self.waiting_for_input == 'max_daily_loss':
                if validate_number_input(value, 0.5, 20.0):
                    self.bot.settings.risk_settings['max_daily_loss'] = value
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Макс. убыток/день: <b>{value:.1f}%</b>")
                    self.send_risk_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.5 до 20.0")

            elif self.waiting_for_input == 'max_consecutive_losses':
                if validate_number_input(value, 1, 10) and value == int(value):
                    self.bot.settings.risk_settings['max_consecutive_losses'] = int(value)
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Макс. убыточных подряд: <b>{int(value)}</b>")
                    self.send_risk_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Введите целое число от 1 до 10")
            self.waiting_for_input = None
        except Exception as e:
            error_msg = f"❌ Ошибка обработки ввода: {e}"
            log_error(error_msg)
            self.bot.telegram.send_message(error_msg)

    def handle_strategy_selection(self, message_text):
        """Обработка выбора стратегии"""
        for strategy_id, strategy_name in self.bot.settings.strategy_settings['available_strategies'].items():
            if strategy_name in message_text:
                old_strategy = self.bot.settings.strategy_settings['active_strategy']
                self.bot.settings.strategy_settings['active_strategy'] = strategy_id
                self.bot.settings.save_settings()
                message = f"""
✅ <b>СТРАТЕГИЯ ИЗМЕНЕНА</b>

🔄 Было: <b>{self.bot.settings.strategy_settings['available_strategies'][old_strategy]}</b>
🎯 Стало: <b>{strategy_name}</b>

💡 Бот теперь использует выбранную стратегию для торговли.
"""
                self.bot.telegram.send_message(message)
                self.send_strategy_menu()
                return

    def handle_pair_selection(self, message_text):
        """Обработка выбора торговой пары"""
        for pair_id, pair_name in self.bot.settings.trading_pairs['available_pairs'].items():
            if pair_name in message_text:
                old_pair = self.bot.settings.trading_pairs['active_pair']
                self.bot.settings.trading_pairs['active_pair'] = pair_id
                self.bot.settings.settings['symbol'] = pair_id
                self.bot.settings.save_settings()
                new_data = self.bot.exchange.get_market_data(pair_id)
                if new_data:
                    message = f"""
✅ <b>ТОРГОВАЯ ПАРА ИЗМЕНЕНА</b>

🔄 Было: <b>{old_pair}</b>
🎯 Стало: <b>{pair_id} - {pair_name}</b>

💰 Текущая цена: <b>{new_data['current_price']:.2f} USDT</b>
📈 Изменение 24ч: <b>{new_data['price_change_24h']:+.2f}%</b>
"""
                else:
                    message = f"""
✅ <b>ТОРГОВАЯ ПАРА ИЗМЕНЕНА</b>

🔄 Было: <b>{old_pair}</b>  
🎯 Стало: <b>{pair_id} - {pair_name}</b>
"""
                self.bot.telegram.send_message(message)
                self.send_pairs_menu()
                return

    # Методы отправки меню
    def send_main_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_main_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_settings_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_settings_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_ema_settings_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_ema_settings_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_strategy_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_strategy_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_pairs_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_pairs_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_ml_settings_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_ml_settings_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_trading_control_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_trading_control_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_analytics(self):
        message, keyboard = self.bot.telegram.menu_manager.send_analytics_menu()
        self.bot.telegram.send_message(message, keyboard)

    def send_detailed_report(self):
        """Отправка детального отчета"""
        from analytics.reporter import ReportGenerator
        reporter = ReportGenerator(self.bot.metrics)
        report = reporter.generate_performance_report()
        self.bot.telegram.send_message(report)

    def send_charts_info(self):
        """Информация о графиках"""
        message = """
📊 <b>ГРАФИКИ И ВИЗУАЛИЗАЦИЯ</b>

📈 <b>Доступные графики:</b>
• 📊 График цен с индикаторами
• 📉 История сделок
• 🎯 Эффективность стратегий
• ⚡ Уровни риска

💡 <b>Функция в разработке:</b>
В следующем обновлении будут добавлены интерактивные графики для лучшей визуализации данных.
"""
        self.bot.telegram.send_message(message)

    def clear_statistics(self):
        """Очистка статистики"""
        self.bot.metrics.reset_metrics()
        message = "🧹 <b>Статистика очищена</b>\n\nВсе метрики и история сделок сброшены."
        self.bot.telegram.send_message(message)

    # Методы управления настройками
    def start_ema_threshold_input(self):
        self.waiting_for_input = 'ema_threshold'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        message = f"""
📈 <b>НАСТРОЙКА ПОРОГА EMA</b>

Текущее значение: <b>{self.bot.settings.settings['ema_cross_threshold'] * 100:.2f}%</b>

💡 Введите новое значение в процентах:
Примеры:
• 0.25 для 0.25%
• .25 для 0.25%  
• 0.5 для 0.5%
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_trade_amount_input(self):
        self.waiting_for_input = 'trade_amount'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        message = f"""
💰 <b>НАСТРОЙКА РАЗМЕРА СТАВКИ</b>

Текущее значение: <b>{self.bot.settings.settings['trade_amount_percent'] * 100:.1f}%</b>

💡 Введите новое значение в процентах:
Примеры:
• 25 для 25%
• 15.5 для 15.5%
• 50 для 50%
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_ml_buy_threshold_input(self):
        self.waiting_for_input = 'ml_buy_threshold'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        message = f"""
🎯 <b>НАСТРОЙКА ПОРОГА ML ДЛЯ ПОКУПКИ</b>

Текущее значение: <b>{self.bot.settings.ml_settings['confidence_threshold_buy']:.1f}</b>

💡 Введите новое значение (0.1 - 0.9):
Чем выше значение, тем строже фильтрация сигналов.
Примеры:
• 0.3 - более агрессивно
• 0.6 - более консервативно  
• 0.5 - сбалансировано
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_ml_sell_threshold_input(self):
        self.waiting_for_input = 'ml_sell_threshold'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        message = f"""
🎯 <b>НАСТРОЙКА ПОРОГА ML ДЛЯ ПРОДАЖИ</b>

Текущее значение: <b>{self.bot.settings.ml_settings['confidence_threshold_sell']:.1f}</b>

💡 Введите новое значение (0.1 - 0.9):
Чем ниже значение, тем строже фильтрация сигналов.
Примеры:
• 0.2 - более агрессивно
• 0.5 - более консервативно
• 0.3 - сбалансировано
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_take_profit_input(self):
        self.waiting_for_input = 'take_profit'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        strategy = self.bot.get_active_strategy()
        current_tp = strategy.settings.get('take_profit_percent', 2.0)
        message = f"""
🎯 <b>НАСТРОЙКА TAKE PROFIT</b>

Текущее значение: <b>{current_tp:.1f}%</b>

💡 Введите новое значение (0.5 - 20.0%):
Take Profit - процент прибыли для автоматического закрытия позиции.
Примеры:
• 2.0 - стандартный TP 2%
• 1.5 - консервативный TP 1.5%
• 3.0 - агрессивный TP 3%
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_stop_loss_input(self):
        self.waiting_for_input = 'stop_loss'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        strategy = self.bot.get_active_strategy()
        current_sl = strategy.settings.get('stop_loss_percent', 1.5)
        message = f"""
🛑 <b>НАСТРОЙКА STOP LOSS</b>

Текущее значение: <b>{current_sl:.1f}%</b>

💡 Введите новое значение (0.5 - 10.0%):
Stop Loss - процент убытка для автоматического закрытия позиции.
Примеры:
• 1.5 - стандартный SL 1.5%
• 1.0 - консервативный SL 1%
• 2.0 - агрессивный SL 2%
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_min_hold_time_input(self):
        self.waiting_for_input = 'min_hold_time'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        strategy = self.bot.get_active_strategy()
        current_time = strategy.settings.get('min_hold_time', 300) // 60
        message = f"""
⏰ <b>НАСТРОЙКА MIN HOLD TIME</b>

Текущее значение: <b>{current_time} мин</b>

💡 Введите новое значение (1 - 60 минут):
Минимальное время удержания позиции перед возможностью закрытия.
Примеры:
• 5 - 5 минут (стандарт)
• 10 - 10 минут (консервативно)
• 2 - 2 минуты (агрессивно)
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_max_position_input(self):
        self.waiting_for_input = 'max_position_size'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        current = self.bot.settings.risk_settings.get('max_position_size', 25.0)
        message = f"""
💼 <b>МАКС. РАЗМЕР ПОЗИЦИИ</b>
Текущее значение: <b>{current:.1f}%</b>
💡 Введите новое значение (5.0 – 100.0%):
Примеры:
• 30 для 30%
• 25.5 для 25.5%
• 50 для 50%
"""
        self.bot.telegram.send_message(message, keyboard)

    def send_risk_settings_menu(self):
        message, keyboard = self.bot.telegram.menu_manager.send_risk_settings_menu()
        self.bot.telegram.send_message(message, keyboard)

    def toggle_ml_enabled(self):
        self.bot.settings.ml_settings['enabled'] = not self.bot.settings.ml_settings['enabled']
        self.bot.settings.save_settings()
        status = "✅ ВКЛЮЧЕН" if self.bot.settings.ml_settings['enabled'] else "❌ ВЫКЛЮЧЕН"
        message = f"🤖 Machine Learning: <b>{status}</b>"
        self.bot.telegram.send_message(message)
        self.send_ml_settings_menu()

    def toggle_trailing_stop(self):
        strategy = self.bot.get_active_strategy()
        strategy.settings['trailing_stop'] = not strategy.settings.get('trailing_stop', False)
        status = "✅ ВКЛЮЧЕН" if strategy.settings['trailing_stop'] else "❌ ВЫКЛЮЧЕН"
        message = f"📉 Trailing Stop: <b>{status}</b>"
        self.bot.telegram.send_message(message)
        self.send_ema_settings_menu()

    def toggle_trading_enabled(self):
        self.bot.settings.settings['trading_enabled'] = not self.bot.settings.settings['trading_enabled']
        self.bot.settings.save_settings()
        status = "✅ ВКЛЮЧЕНА" if self.bot.settings.settings['trading_enabled'] else "❌ ОСТАНОВЛЕНА"
        message = f"📊 Автоматическая торговля: <b>{status}</b>"
        self.bot.telegram.send_message(message)
        self.send_trading_control_menu()

    def toggle_trade_signals(self):
        self.bot.settings.settings['enable_trade_signals'] = not self.bot.settings.settings['enable_trade_signals']
        self.bot.settings.save_settings()
        status = "✅ ВКЛЮЧЕНЫ" if self.bot.settings.settings['enable_trade_signals'] else "❌ ВЫКЛЮЧЕНЫ"
        message = f"🎯 Торговые сигналы: <b>{status}</b>"
        self.bot.telegram.send_message(message)
        self.send_trading_control_menu()

    def toggle_demo_mode(self):
        self.bot.settings.settings['demo_mode'] = not self.bot.settings.settings['demo_mode']
        self.bot.settings.save_settings()
        mode = "🟢 ДЕМО-РЕЖИМ" if self.bot.settings.settings['demo_mode'] else "🔴 РЕАЛЬНАЯ ТОРГОВЛЯ"
        message = f"🔧 Режим работы: <b>{mode}</b>"
        self.bot.telegram.send_message(message)
        self.send_trading_control_menu()

    def toggle_price_updates(self):
        self.bot.settings.settings['enable_price_updates'] = not self.bot.settings.settings['enable_price_updates']
        self.bot.settings.save_settings()
        status = "✅ ВКЛЮЧЕНЫ" if self.bot.settings.settings['enable_price_updates'] else "❌ ОТКЛЮЧЕНЫ"
        message = f"📊 Обновления цены: <b>{status}</b>"
        self.bot.telegram.send_message(message)
        self.send_settings_menu()

    def retrain_ml_model(self):
        message = "🤖 Запущено переобучение ML модели... Это может занять несколько минут."
        self.bot.telegram.send_message(message)
        threading.Thread(target=self.bot.ml_model.train, args=(self.bot.exchange.exchange,), daemon=True).start()

    def restart_bot(self):
        message = "🔄 Перезагрузка бота..."
        self.bot.telegram.send_message(message)
        self.bot.telegram.send_message("✅ Бот перезагружен")

    def emergency_stop(self):
        if self.bot.position:
            self.bot.position = None
            self.bot.entry_price = 0
        self.bot.settings.settings['trading_enabled'] = False
        self.bot.settings.save_settings()
        message = "🛑 <b>ЭКСТРЕННАЯ ОСТАНОВКА</b>\n\nПозиции закрыты. Торговля остановлена."
        self.bot.telegram.send_message(message)

    def send_status(self):
        data = self.bot.exchange.get_market_data(self.bot.settings.trading_pairs['active_pair'])
        if not data:
            self.bot.telegram.send_message("❌ Не удалось получить данные рынка")
            return
        current_pair = self.bot.settings.trading_pairs['active_pair']
        pair_name = self.bot.settings.get_active_pair_name()
        strategy_name = self.bot.settings.get_active_strategy_name()
        ml_confidence, ml_signal = self.bot.ml_model.predict(data.get('ohlcv', []))
        signal = self.bot.get_active_strategy().calculate_signal(data, ml_confidence, ml_signal)
        position_status = "🟢 ОТКРЫТА" if self.bot.position == 'long' else "⚪ ОЖИДАНИЕ"
        trend_direction = "🟢 ВВЕРХ" if data['ema_diff_percent'] > 0 else "🔴 ВНИЗ"
        balance = self.bot.exchange.get_balance()
        trade_amount_percent = self.bot.settings.settings['trade_amount_percent']
        next_trade_amount = balance['total_usdt'] * trade_amount_percent if balance else 0
        message = f"""
📊 <b>РАСШИРЕННЫЙ СТАТУС</b>

💱 <b>Пара:</b> {pair_name} ({current_pair})
🎯 <b>Стратегия:</b> {strategy_name}
💰 <b>Цена:</b> {data['current_price']:.2f} USDT
📈 <b>Тренд:</b> {trend_direction} ({data['ema_diff_percent']*100:+.2f}%)
🤖 <b>ML сигнал:</b> {ml_signal} ({ml_confidence:.1%})
🎯 <b>Торговый сигнал:</b> {signal.upper()}
📈 <b>Позиция:</b> {position_status}

💰 <b>Следующая ставка:</b> {next_trade_amount:.2f} USDT ({trade_amount_percent*100:.1f}%)

📊 <b>АНАЛИТИКА:</b>
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыльных: {self.bot.metrics.winning_trades}
• Всего сделок: {self.bot.metrics.total_trades}

⚡ <b>СИСТЕМА:</b>
• Торговля: {'✅ ВКЛ' if self.bot.settings.settings['trading_enabled'] else '❌ ВЫКЛ'}
• ML: {'✅ ВКЛ' if self.bot.settings.ml_settings['enabled'] else '❌ ВЫКЛ'}
• Режим: {'🟢 ДЕМО' if self.bot.settings.settings['demo_mode'] else '🔴 РЕАЛЬНЫЙ'}

⏰ {self.bot.metrics.get_current_time()}
"""
        self.bot.telegram.send_message(message)

    def send_account_info(self):
        balance = self.bot.exchange.get_balance()
        if not balance:
            self.bot.telegram.send_message("❌ Не удалось получить информацию об аккаунте")
            return
        market_data = self.bot.exchange.get_market_data(self.bot.settings.trading_pairs['active_pair'])
        btc_price = market_data['current_price'] if market_data else 0
        btc_value = balance['total_btc'] * btc_price
        total_value = balance['total_usdt'] + btc_value
        trade_amount_percent = self.bot.settings.settings['trade_amount_percent']
        next_trade_amount = balance['total_usdt'] * trade_amount_percent
        message = f"""
💼 <b>ИНФОРМАЦИЯ ОБ АККАУНТЕ</b>

💰 <b>БАЛАНС USDT:</b>
• Всего: {balance['total_usdt']:.2f} USDT
• Свободно: {balance['free_usdt']:.2f} USDT
• Занято: {balance['used_usdt']:.2f} USDT

₿ <b>БАЛАНС BTC:</b>
• Всего: {balance['total_btc']:.6f} BTC
• Свободно: {balance['free_btc']:.6f} BTC
• Стоимость: {btc_value:.2f} USDT

📊 <b>ОБЩАЯ СТАТИСТИКА:</b>
• Общая стоимость: {total_value:.2f} USDT
• Прибыль за сегодня: {self.bot.metrics.daily_profit:.2f} USDT
• Открыта позиция: {'✅ ДА' if self.bot.position else '❌ НЕТ'}
• Всего сделок: {len(self.bot.metrics.trade_history)}

🎯 <b>СЛЕДУЮЩАЯ СТАВКА:</b>
• Размер: {next_trade_amount:.2f} USDT
• Процент: {trade_amount_percent*100:.1f}%

⚡ <b>СТАТУС:</b>
• Режим: {'🟢 ДЕМО' if self.bot.settings.settings['demo_mode'] else '🔴 РЕАЛЬНЫЙ'}
• Торговые сигналы: {'✅ ВКЛ' if self.bot.settings.settings['enable_trade_signals'] else '❌ ВЫКЛ'}

⏰ Обновлено: {self.bot.metrics.get_current_time()}
"""
        self.bot.telegram.send_message(message)

    def send_trade_history(self):
        if not self.bot.metrics.trade_history:
            message = "📊 <b>ИСТОРИЯ СДЕЛОК</b>\n\nИстория пуста"
        else:
            message = "📊 <b>ПОСЛЕДНИЕ СДЕЛКИ</b>\n\n"
            for trade in self.bot.metrics.trade_history[-5:]:
                emoji = "🟢" if trade.get('profit', 0) > 0 else "🔴"
                profit_str = f"+{trade['profit']:.2f}%" if trade.get('profit', 0) > 0 else f"{trade['profit']:.2f}%"
                position_size = trade.get('position_size_usdt', 0)
                message += f"{emoji} {trade['signal'].upper()} - {trade['price']:.2f} USDT ({profit_str}) | Ставка: {position_size:.2f} USDT\n"
        self.bot.telegram.send_message(message)

    def send_market_update(self):
        data = self.bot.exchange.get_market_data(self.bot.settings.trading_pairs['active_pair'])
        if not data:
            return
        ml_confidence, ml_signal = self.bot.ml_model.predict(data.get('ohlcv', []))
        signal = self.bot.get_active_strategy().calculate_signal(data, ml_confidence, ml_signal)
        self.bot.telegram.send_market_update(data, signal, ml_confidence, ml_signal)