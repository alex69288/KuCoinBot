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
    
    def _safe_send_message(self, message):
        """Безопасная отправка сообщения с проверкой инициализации telegram"""
        if not hasattr(self.bot, 'telegram') or self.bot.telegram is None:
            log_error("❌ Telegram бот не инициализирован. Сообщение не отправлено.")
            return False
        try:
            self.bot.telegram.send_message(message)
            return True
        except Exception as e:
            log_error(f"❌ Ошибка отправки сообщения в Telegram: {e}")
            return False

    def handle_message(self, message_text):
        """Основной обработчик сообщений"""
        try:
            if self.waiting_for_input:
                self.handle_direct_input(message_text)
                return
            # 🔧 БЕЗОПАСНАЯ ПРОВЕРКА: убеждаемся, что telegram инициализирован
            if not hasattr(self.bot, 'telegram') or self.bot.telegram is None:
                log_error("❌ Telegram бот не инициализирован. Сообщение не может быть обработано.")
                return
            self.bot.telegram.send_message("⏳ Обрабатываю запрос...")
            # Обработка кнопок "Назад"
            if message_text in ['🔙 Назад к настройкам', '🔙 Назад']:
                self.send_settings_menu()
                return
            if message_text == '🏠 Главное меню' or message_text == 'Меню' or message_text == '/menu':
                self.send_main_menu_inline()
                return
            # Основные команды главного меню
            if message_text == '/start':
                self.send_main_menu_inline()
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
            # 🔹 ОБРАБОТКА ПЕРЕКЛЮЧЕНИЯ РЕЖИМА TP
            elif '🔄 TP режим:' in message_text:
                self.toggle_take_profit_mode()
        except Exception as e:
            error_msg = f"❌ Ошибка обработки команды: {e}"
            log_error(error_msg)
            # 🔧 БЕЗОПАСНАЯ ПРОВЕРКА: убеждаемся, что telegram инициализирован перед отправкой ошибки
            if hasattr(self.bot, 'telegram') and self.bot.telegram is not None:
                try:
                    self.bot.telegram.send_message(error_msg)
                except Exception as send_error:
                    log_error(f"❌ Не удалось отправить сообщение об ошибке: {send_error}")

    def handle_callback(self, callback_data, callback_query=None):
        """Обработка callback от inline кнопок с редактированием сообщений"""
        try:
            log_info(f"🔘 Обрабатываем callback: {callback_data}")
            
            # Получаем информацию о сообщении для редактирования
            chat_id = None
            message_id = None
            if callback_query and "message" in callback_query:
                chat_id = callback_query["message"]["chat"]["id"]
                message_id = callback_query["message"]["message_id"]
            
            # Основные меню
            if callback_data == "main_menu":
                self.send_main_menu_inline()
            elif callback_data == "status":
                self.send_status_inline()
            elif callback_data == "account_info":
                self.send_account_info_inline()
            elif callback_data == "settings":
                self.send_settings_menu_inline()
            elif callback_data == "trades":
                self.send_trade_history_inline()
            elif callback_data == "analytics":
                self.send_analytics_inline()
            elif callback_data == "control":
                self.send_trading_control_menu_inline()
            
            # Настройки
            elif callback_data == "settings_pairs":
                self.send_pairs_menu_inline()
            elif callback_data == "settings_strategy":
                self.send_strategy_menu_inline()
            elif callback_data == "settings_trade_amount":
                self.start_trade_amount_input()
            elif callback_data == "settings_ema_threshold":
                self.start_ema_threshold_input()
            elif callback_data == "settings_ml":
                self.send_ml_settings_menu_inline()
            elif callback_data == "settings_ema":
                self.send_ema_settings_menu_inline()
            elif callback_data == "settings_risk":
                self.send_risk_settings_menu_inline()
            elif callback_data == "settings_toggle_updates":
                self.toggle_price_updates()
                self.send_settings_menu_inline()
            
            # Выбор стратегии и пары
            elif callback_data.startswith("strategy_"):
                strategy_id = callback_data.replace("strategy_", "")
                self.handle_strategy_selection_by_id(strategy_id)
            elif callback_data.startswith("pair_"):
                pair_id = callback_data.replace("pair_", "")
                self.handle_pair_selection_by_id(pair_id)
            
            # EMA настройки
            elif callback_data == "ema_tp":
                strategy = self.bot.get_active_strategy()
                take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
                if take_profit_usdt > 0:
                    self.start_take_profit_usdt_input()
                else:
                    self.start_take_profit_input()
            elif callback_data == "ema_sl":
                self.start_stop_loss_input()
            elif callback_data == "ema_trailing":
                self.toggle_trailing_stop()
                self.send_ema_settings_menu_inline()
            elif callback_data == "ema_hold_time":
                self.start_min_hold_time_input()
            elif callback_data == "ema_tp_mode":
                self.toggle_take_profit_mode()
                self.send_ema_settings_menu_inline()
            
            # ML настройки
            elif callback_data == "ml_toggle":
                self.toggle_ml_enabled()
                self.send_ml_settings_menu_inline()
            elif callback_data == "ml_retrain":
                self.retrain_ml_model()
            elif callback_data == "ml_buy_threshold":
                self.start_ml_buy_threshold_input()
            elif callback_data == "ml_sell_threshold":
                self.start_ml_sell_threshold_input()
            
            # Управление
            elif callback_data == "control_toggle_trading":
                self.toggle_trading_enabled(send_confirmation=False)
                self.send_trading_control_menu_inline(chat_id, message_id)
            elif callback_data == "control_toggle_signals":
                self.toggle_trade_signals(send_confirmation=False)
                self.send_trading_control_menu_inline(chat_id, message_id)
            elif callback_data == "control_toggle_demo":
                self.toggle_demo_mode(send_confirmation=False)
                self.send_trading_control_menu_inline(chat_id, message_id)
            elif callback_data == "control_restart":
                self.restart_bot()
            elif callback_data == "control_emergency":
                self.emergency_stop()
            elif callback_data == "control_demo_trade":
                self.enable_demo_trading(send_confirmation=False)
                self.send_trading_control_menu_inline(chat_id, message_id)
            
            # Риск-менеджмент
            elif callback_data == "risk_max_position":
                self.start_max_position_input()
            elif callback_data == "risk_max_loss":
                self.start_max_daily_loss_input()
            elif callback_data == "risk_max_consecutive":
                self.start_max_consecutive_input()
            
            # Аналитика
            elif callback_data == "analytics_detailed":
                self.send_detailed_report_inline()
            elif callback_data == "analytics_charts":
                self.send_charts_info_inline()
            elif callback_data == "analytics_clear":
                self.clear_statistics()
                self.send_analytics_inline()
            
            # Общие действия
            elif callback_data == "refresh":
                # Обновляем главное меню с актуальными данными
                self.send_main_menu_inline()
            else:
                log_info(f"⚠️ Неизвестный callback: {callback_data}")
        except Exception as e:
            log_error(f"❌ Ошибка обработки callback: {e}")
    
    def send_main_menu_inline(self):
        """Отправка главного меню с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_main_menu_inline()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_settings_menu_inline(self):
        """Отправка меню настроек с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_settings_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_strategy_menu_inline(self):
        """Отправка меню выбора стратегии с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_strategy_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_pairs_menu_inline(self):
        """Отправка меню выбора пары с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_pairs_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_ema_settings_menu_inline(self):
        """Отправка меню настроек EMA с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_ema_settings_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_ml_settings_menu_inline(self):
        """Отправка меню ML настроек с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_ml_settings_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_trading_control_menu_inline(self, chat_id=None, message_id=None):
        """Отправка меню управления торговлей с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_trading_control_menu()
        self._send_or_edit_message(chat_id, message_id, message, inline_keyboard)
    
    def send_risk_settings_menu_inline(self):
        """Отправка меню риск-менеджмента с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_risk_settings_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_analytics_inline(self):
        """Отправка меню аналитики с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_analytics_menu()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_trade_history_inline(self):
        """Отправка истории сделок с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_trade_history()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_account_info_inline(self):
        """Отправка информации об аккаунте с inline-кнопками"""
        message, inline_keyboard = self.bot.telegram.menu_manager.send_account_info()
        self._send_or_edit_message(None, None, message, inline_keyboard)
    
    def send_status_inline(self):
        """Отправка статуса с inline-кнопками"""
        data = self.bot.exchange.get_market_data(self.bot.settings.trading_pairs['active_pair'])
        if not data:
            error_msg = "❌ Не удалось получить данные рынка"
            self.bot.telegram.send_message(error_msg)
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
        
        tp_info = self.bot.get_take_profit_info()
        if tp_info['mode'] == 'USDT':
            tp_display = f"{self.bot.telegram.smart_format(tp_info['take_profit_usdt'], 4)} USDT"
        else:
            tp_display = f"{self.bot.telegram.smart_format(tp_info['take_profit_percent'], 4)}%"
            
        message = f"""
📊 <b>РАСШИРЕННЫЙ СТАТУС</b>

💱 <b>Торговля:</b>
• Пара: {pair_name}
• Стратегия: {strategy_name}
• Позиция: {position_status}
• Размер ставки: {next_trade_amount:.2f} USDT ({trade_amount_percent*100:.1f}%)
• Take Profit: {tp_display}

📈 <b>Рынок:</b>
• Цена: {data['current_price']:.2f} USDT
• Изменение 24ч: {data.get('price_change_24h', 0):+.2f}%
• Тренд EMA: {trend_direction} ({data['ema_diff_percent']*100:+.2f}%)
• Сигнал: {signal.upper()}
• ML: {ml_signal} ({ml_confidence:.1%})

💰 <b>Баланс:</b>
• USDT: {balance['total_usdt']:.2f} (свободно: {balance['free_usdt']:.2f})
• BTC: {balance['total_btc']:.6f} (свободно: {balance['free_btc']:.6f})

📊 <b>Статистика:</b>
• Сделок: {self.bot.metrics.total_trades}
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыль: {self.bot.metrics.total_profit:.2f}% ({self.bot.metrics.total_profit_usdt:.2f} USDT)
"""
        
        # Inline-кнопки для возврата в меню
        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': '🔄 Обновить', 'callback_data': 'status'},
                    {'text': '🏠 Главное меню', 'callback_data': 'main_menu'}
                ]
            ]
        }
        
        # 🔧 БЕЗОПАСНАЯ ПРОВЕРКА перед отправкой сообщения
        if not hasattr(self.bot, 'telegram') or self.bot.telegram is None:
            log_error("❌ Telegram бот не инициализирован. Сообщение не отправлено.")
            return
        # Всегда отправляем новое сообщение
        self.bot.telegram.send_message(message, inline_keyboard)
    
    def _send_or_edit_message(self, chat_id, message_id, message, inline_keyboard):
        """Вспомогательный метод - редактирует сообщение, если есть chat_id и message_id, иначе отправляет новое"""
        # 🔧 БЕЗОПАСНАЯ ПРОВЕРКА перед отправкой сообщения
        if not hasattr(self.bot, 'telegram') or self.bot.telegram is None:
            log_error("❌ Telegram бот не инициализирован. Сообщение не отправлено.")
            return
        
        # Если есть chat_id и message_id, редактируем существующее сообщение
        if chat_id is not None and message_id is not None:
            # Пытаемся отредактировать сообщение
            if not self.bot.telegram.edit_message_text(chat_id, message_id, message, inline_keyboard):
                # Если редактирование не удалось (например, сообщение слишком старое), отправляем новое
                self.bot.telegram.send_message(message, inline_keyboard)
        else:
            # Если нет данных для редактирования, отправляем новое сообщение
            self.bot.telegram.send_message(message, inline_keyboard)
    
    def handle_strategy_selection_by_id(self, strategy_id):
        """Обработка выбора стратегии по ID"""
        old_strategy = self.bot.settings.strategy_settings['active_strategy']
        self.bot.settings.strategy_settings['active_strategy'] = strategy_id
        self.bot.settings.save_settings()
        
        strategy_name = self.bot.settings.strategy_settings['available_strategies'].get(strategy_id, strategy_id)
        msg = f"✅ Стратегия изменена на: <b>{strategy_name}</b>"
        self.bot.telegram.send_message(msg)
        self.send_settings_menu_inline()
    
    def handle_pair_selection_by_id(self, pair_id):
        """Обработка выбора пары по ID"""
        old_pair = self.bot.settings.trading_pairs['active_pair']
        self.bot.settings.trading_pairs['active_pair'] = pair_id
        self.bot.settings.settings['symbol'] = pair_id
        self.bot.settings.save_settings()
        
        pair_name = self.bot.settings.trading_pairs['available_pairs'].get(pair_id, pair_id)
        msg = f"✅ Торговая пара изменена на: <b>{pair_id} - {pair_name}</b>"
        self.bot.telegram.send_message(msg)
        self.send_settings_menu_inline()

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
            if "🎯 Take Profit:" in message_text:
                # Определяем, в каком режиме сейчас TP
                strategy = self.bot.get_active_strategy()
                take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
                if take_profit_usdt > 0:
                    self.start_take_profit_usdt_input()
                else:
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
        """Обработка выбора настроек рисков"""
        try:
            if "💼 Макс. позиция:" in message_text:
                self.start_max_position_input()
            elif "📉 Макс. убыток/день:" in message_text:
                self.start_max_daily_loss_input()
            elif "🔴 Макс. убыточных:" in message_text:
                self.start_max_consecutive_input()
        except Exception as e:
            error_msg = f"❌ Ошибка обработки настроек рисков: {e}"
            log_error(error_msg)
            self.bot.telegram.send_message(error_msg)

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
                    # Возвращаемся к настройкам
                    self.send_settings_menu_inline()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.01 до 10.0")
            elif self.waiting_for_input == 'trade_amount':
                if validate_number_input(value, 1.0, 100.0):
                    self.bot.settings.settings['trade_amount_percent'] = value / 100
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Размер ставки установлен: <b>{value:.1f}%</b>")
                    # Возвращаемся к настройкам
                    self.send_settings_menu_inline()
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
                # ✅ РАЗРЕШАЕМ ВВОД ОТ 0.01% ДО 20.0%
                if value >= 0.01 and value <= 20.0:
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['take_profit_percent'] = value
                    strategy.settings['take_profit_usdt'] = 0.0  # 🔹 Явно устанавливаем режим процентов
                    # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Take Profit установлен: <b>{self.bot.telegram.smart_format(value, 4)}%</b>")
                    self.send_ema_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.01 до 20.0%")
                    
            elif self.waiting_for_input == 'take_profit_usdt':
                # ✅ РАЗРЕШАЕМ ВВОД ОТ 0.01 USDT
                if value >= 0.01:
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['take_profit_usdt'] = value
                    strategy.settings['take_profit_percent'] = 0.0  # 🔹 Явно устанавливаем режим USDT
                    # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Take Profit установлен: <b>{self.bot.telegram.smart_format(value, 4)} USDT</b>")
                    self.send_ema_settings_menu()
                elif value == 0:
                    # Переключение обратно в режим процентов
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['take_profit_usdt'] = 0.0
                    strategy.settings['take_profit_percent'] = 2.0  # Значение по умолчанию
                    # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message("🔄 Take Profit переключен в режим процентов (2.0%)")
                    self.send_ema_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть >= 0.01 USDT или 0 для переключения в %")
                    
            elif self.waiting_for_input == 'stop_loss':
                if validate_number_input(value, 0.5, 10.0):
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['stop_loss_percent'] = value
                    # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
                    self.bot.settings.save_settings()
                    self.bot.telegram.send_message(f"✅ Stop Loss установлен: <b>{value:.1f}%</b>")
                    self.send_ema_settings_menu()
                else:
                    self.bot.telegram.send_message("❌ Значение должно быть от 0.5 до 10.0")
            elif self.waiting_for_input == 'min_hold_time':
                if validate_number_input(value, 1, 60):
                    strategy = self.bot.get_active_strategy()
                    strategy.settings['min_hold_time'] = int(value) * 60
                    # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
                    self.bot.settings.save_settings()
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
            self.waiting_for_input = None
        except Exception as e:
            error_msg = f"❌ Ошибка обработки ввода: {e}"
            log_error(error_msg)
            self.bot.telegram.send_message(error_msg)

    def toggle_take_profit_mode(self):
        """Переключает режим Take Profit между процентами и USDT - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            strategy = self.bot.get_active_strategy()
            current_usdt = strategy.settings.get('take_profit_usdt', 0.0)
            current_percent = strategy.settings.get('take_profit_percent', 2.0)
            
            if current_usdt > 0:
                # Переключаем на проценты - конвертируем USDT в проценты
                position_size = getattr(strategy, 'position_size_usdt', 0)
                if position_size > 0 and current_usdt > 0:
                    new_percent = (current_usdt / position_size) * 100
                    strategy.settings['take_profit_percent'] = max(0.01, new_percent)  # минимум 0.01%
                else:
                    strategy.settings['take_profit_percent'] = 2.0  # значение по умолчанию
                
                strategy.settings['take_profit_usdt'] = 0.0
                msg = "🔄 Take Profit переключен в режим <b>процентов</b>"
            else:
                # Переключаем на USDT - конвертируем проценты в USDT
                position_size = getattr(strategy, 'position_size_usdt', 0)
                if position_size > 0 and current_percent > 0:
                    new_usdt = position_size * (current_percent / 100)
                    strategy.settings['take_profit_usdt'] = max(0.01, new_usdt)  # минимум 0.01 USDT
                else:
                    # Если нет данных о размере позиции, используем разумное значение по умолчанию
                    strategy.settings['take_profit_usdt'] = 0.5  # 0.5 USDT по умолчанию
                
                strategy.settings['take_profit_percent'] = 0.0
                msg = "🔄 Take Profit переключен в режим <b>USDT</b>"
            
            # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
            self.bot.settings.save_settings()
            
            self.bot.telegram.send_message(msg)
            self.send_ema_settings_menu()
            
        except Exception as e:
            error_msg = f"❌ Ошибка переключения режима TP: {e}"
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
                # Возвращаемся к настройкам после изменения
                self.send_settings_menu_inline()
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
                # Возвращаемся к настройкам после изменения
                self.send_settings_menu_inline()
                return

    # Методы отправки меню - теперь все используют inline-кнопки
    def send_main_menu(self):
        """Отправка главного меню - использует inline-кнопки"""
        self.send_main_menu_inline()

    def send_settings_menu(self):
        """Отправка меню настроек - использует inline-кнопки"""
        self.send_settings_menu_inline()

    def send_ema_settings_menu(self):
        """Отправка меню настроек EMA - использует inline-кнопки"""
        self.send_ema_settings_menu_inline()

    def send_strategy_menu(self):
        """Отправка меню выбора стратегии - использует inline-кнопки"""
        self.send_strategy_menu_inline()

    def send_pairs_menu(self):
        """Отправка меню выбора пары - использует inline-кнопки"""
        self.send_pairs_menu_inline()

    def send_ml_settings_menu(self):
        """Отправка меню ML настроек - использует inline-кнопки"""
        self.send_ml_settings_menu_inline()

    def send_trading_control_menu(self):
        """Отправка меню управления торговлей - использует inline-кнопки"""
        self.send_trading_control_menu_inline()

    def send_analytics(self):
        """Отправка меню аналитики - использует inline-кнопки"""
        self.send_analytics_inline()

    def send_detailed_report(self):
        """Отправка детального отчета"""
        from analytics.reporter import ReportGenerator
        reporter = ReportGenerator(self.bot.metrics)
        report = reporter.generate_performance_report()
        self.bot.telegram.send_message(report)
    
    def send_detailed_report_inline(self):
        """Отправка детального отчета с inline-кнопками"""
        from analytics.reporter import ReportGenerator
        reporter = ReportGenerator(self.bot.metrics)
        report = reporter.generate_performance_report()
        
        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': '🔙 Назад к аналитике', 'callback_data': 'analytics'}
                ]
            ]
        }
        
        self._send_or_edit_message(None, None, report, inline_keyboard)

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
    
    def send_charts_info_inline(self):
        """Информация о графиках с inline-кнопками"""
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
        
        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': '🔙 Назад к аналитике', 'callback_data': 'analytics'}
                ]
            ]
        }
        
        self._send_or_edit_message(None, None, message, inline_keyboard)

    def clear_statistics(self):
        """Очистка статистики"""
        self.bot.metrics.reset_metrics()
        message = "🧹 <b>Статистика очищена</b>\nВсе метрики и история сделок сброшены."
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

    def start_take_profit_usdt_input(self):
        self.waiting_for_input = 'take_profit_usdt'
        # 🔹 Автоматически переключаем в режим USDT
        strategy = self.bot.get_active_strategy()
        strategy.settings['take_profit_percent'] = 0.0
        
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        current_tp_usdt = strategy.settings.get('take_profit_usdt', 0.0)
        message = f"""
🎯 <b>НАСТРОЙКА TAKE PROFIT (в USDT)</b>
Текущее значение: <b>{self.bot.telegram.smart_format(current_tp_usdt, 4)} USDT</b>
💡 Введите новое значение (>= 0.01 USDT):
Примеры:
• 0.01 — фиксировать прибыль от 0.01 USDT
• 0.05 — от 0.05 USDT  
• 0.10 — от 0.10 USDT
• 1.00 — от 1.00 USDT
• 0 — отключить (вернётся к %)
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_take_profit_input(self):
        self.waiting_for_input = 'take_profit'
        # 🔹 Автоматически переключаем в режим процентов
        strategy = self.bot.get_active_strategy()
        strategy.settings['take_profit_usdt'] = 0.0
        
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        current_tp = strategy.settings.get('take_profit_percent', 2.0)
        message = f"""
🎯 <b>НАСТРОЙКА TAKE PROFIT</b>
Текущее значение: <b>{self.bot.telegram.smart_format(current_tp, 4)}%</b>
💡 Введите новое значение (0.01 - 20.0%):
Примеры:
• 0.01 — консервативный TP 0.01%
• 0.10 — TP 0.10%
• 0.50 — TP 0.50%
• 1.00 — стандартный TP 1%
• 2.00 — агрессивный TP 2%
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

    def start_max_daily_loss_input(self):
        self.waiting_for_input = 'max_daily_loss'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        current = self.bot.settings.risk_settings.get('max_daily_loss', 3.0)
        message = f"""
📉 <b>МАКС. УБЫТОК/ДЕНЬ</b>
Текущее значение: <b>{current:.1f}%</b>
💡 Введите новое значение (0.5 – 20.0%):
Примеры:
• 2.0 для 2%
• 3.5 для 3.5%
• 5.0 для 5%
"""
        self.bot.telegram.send_message(message, keyboard)

    def start_max_consecutive_input(self):
        self.waiting_for_input = 'max_consecutive_losses'
        keyboard = self.bot.telegram.menu_manager.create_cancel_keyboard()
        current = self.bot.settings.risk_settings.get('max_consecutive_losses', 3)
        message = f"""
🔴 <b>МАКС. УБЫТОЧНЫХ ПОДРЯД</b>
Текущее значение: <b>{current}</b>
💡 Введите новое значение (1 – 10):
Примеры:
• 3 для 3 убыточных сделок
• 5 для 5 убыточных сделок
• 2 для 2 убыточных сделок
"""
        self.bot.telegram.send_message(message, keyboard)

    def send_risk_settings_menu(self):
        """Отправка меню риск-менеджмента - использует inline-кнопки"""
        self.send_risk_settings_menu_inline()

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
        # 🔧 СОХРАНЯЕМ НАСТРОЙКИ
        self.bot.settings.save_settings()
        status = "✅ ВКЛЮЧЕН" if strategy.settings['trailing_stop'] else "❌ ВЫКЛЮЧЕН"
        message = f"📉 Trailing Stop: <b>{status}</b>"
        self.bot.telegram.send_message(message)
        self.send_ema_settings_menu()

    def toggle_trading_enabled(self, send_confirmation=True):
        self.bot.settings.settings['trading_enabled'] = not self.bot.settings.settings['trading_enabled']
        self.bot.settings.save_settings()
        if send_confirmation:
            status = "✅ ВКЛЮЧЕНА" if self.bot.settings.settings['trading_enabled'] else "❌ ОСТАНОВЛЕНА"
            message = f"📊 Автоматическая торговля: <b>{status}</b>"
            self.bot.telegram.send_message(message)
            self.send_trading_control_menu()

    def toggle_trade_signals(self, send_confirmation=True):
        self.bot.settings.settings['enable_trade_signals'] = not self.bot.settings.settings['enable_trade_signals']
        self.bot.settings.save_settings()
        if send_confirmation:
            status = "✅ ВКЛЮЧЕНЫ" if self.bot.settings.settings['enable_trade_signals'] else "❌ ВЫКЛЮЧЕНЫ"
            message = f"🎯 Торговые сигналы: <b>{status}</b>"
            self.bot.telegram.send_message(message)
            self.send_trading_control_menu()

    def toggle_demo_mode(self, send_confirmation=True):
        self.bot.settings.settings['demo_mode'] = not self.bot.settings.settings['demo_mode']
        self.bot.settings.save_settings()
        if send_confirmation:
            mode = "🟢 ДЕМО-РЕЖИМ" if self.bot.settings.settings['demo_mode'] else "🔴 РЕАЛЬНАЯ ТОРГОВЛЯ"
            message = f"🔧 Режим работы: <b>{mode}</b>"
            self.bot.telegram.send_message(message)
            self.send_trading_control_menu_inline()
    
    def enable_demo_trading(self, send_confirmation=True):
        """Включает демо-режим и торговлю одновременно для тестирования"""
        self.bot.settings.settings['demo_mode'] = True
        self.bot.settings.settings['trading_enabled'] = True
        self.bot.settings.save_settings()
        if send_confirmation:
            message = "🧪 <b>ДЕМО-ТОРГОВЛЯ ВКЛЮЧЕНА</b>\n\n✅ Демо-режим: ВКЛ\n✅ Торговля: ВКЛ\n\n💡 Бот будет торговать в демо-режиме для тестирования."
            self.bot.telegram.send_message(message)

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
        message = "🛑 <b>ЭКСТРЕННАЯ ОСТАНОВКА</b>\nПозиции закрыты. Торговля остановлена."
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
        
        # Получаем информацию о Take Profit
        tp_info = self.bot.get_take_profit_info()
        if tp_info['mode'] == 'USDT':
            tp_display = f"{self.bot.telegram.smart_format(tp_info['take_profit_usdt'], 4)} USDT"
        else:
            tp_display = f"{self.bot.telegram.smart_format(tp_info['take_profit_percent'], 4)}%"
            
        message = f"""
📊 <b>РАСШИРЕННЫЙ СТАТУС</b>

💱 <b>Торговля:</b>
• Пара: {pair_name}
• Стратегия: {strategy_name}
• Позиция: {position_status}
• Размер ставки: {next_trade_amount:.2f} USDT ({trade_amount_percent*100:.1f}%)
• Take Profit: {tp_display}

📈 <b>Рынок:</b>
• Цена: {data['current_price']:.2f} USDT
• Изменение 24ч: {data.get('price_change_24h', 0):+.2f}%
• Тренд EMA: {trend_direction} ({data['ema_diff_percent']*100:+.2f}%)
• Сигнал: {signal.upper()}
• ML: {ml_signal} ({ml_confidence:.1%})

💰 <b>Баланс:</b>
• USDT: {balance['total_usdt']:.2f} (свободно: {balance['free_usdt']:.2f})
• BTC: {balance['total_btc']:.6f} (свободно: {balance['free_btc']:.6f})

📊 <b>Статистика:</b>
• Сделок: {self.bot.metrics.total_trades}
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыль: {self.bot.metrics.total_profit:.2f}% ({self.bot.metrics.total_profit_usdt:.2f} USDT)
"""
        self.bot.telegram.send_message(message)

    def send_account_info(self):
        """Отправка информации об аккаунте - использует inline-кнопки"""
        self.send_account_info_inline()

    def send_trade_history(self):
        """Отправка истории сделок - использует inline-кнопки"""
        self.send_trade_history_inline()

    def send_market_update(self):
        """Принудительная отправка обновления рынка"""
        data = self.bot.exchange.get_market_data(self.bot.settings.trading_pairs['active_pair'])
        if not data:
            self.bot.telegram.send_message("❌ Не удалось получить данные рынка")
            return
        
        ml_confidence, ml_signal = self.bot.ml_model.predict(data.get('ohlcv', []))
        signal = self.bot.get_active_strategy().calculate_signal(data, ml_confidence, ml_signal)
        
        self.bot.telegram.send_market_update(data, signal, ml_confidence, ml_signal)