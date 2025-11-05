"""
TELEGRAM БОТ ДЛЯ УПРАВЛЕНИЯ - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
import requests
import threading
import time
from datetime import datetime
from utils.logger import log_info, log_error
from .menus import MenuManager
from .handlers import MessageHandler

class TelegramBot:
    def __init__(self, trading_bot):
        self.bot = trading_bot
        self.menu_manager = MenuManager(trading_bot)
        self.message_handler = MessageHandler(trading_bot)
        self.token = self.bot.settings.settings.get('telegram_token')
        self.chat_id = self.bot.settings.settings.get('telegram_chat_id')
        self.last_update_id = 0
        self.connection_issues = 0
        self.last_balance = None  # Для отслеживания изменений баланса
        # Проверяем настройки Telegram
        if not self.token or not self.chat_id:
            log_error("❌ Telegram не настроен: отсутствует token или chat_id в .env файле")
            log_info("💡 Добавьте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в файл .env")
            return
        # Проверяем валидность токена
        if not self.test_connection():
            log_error("❌ Неверный Telegram токен или chat_id")
            return
        # Запускаем слушатель сообщений
        self.start_message_listener()
        # Устанавливаем команды бота в меню (синяя кнопка слева от поля ввода)
        self.set_bot_commands()
        log_info("✅ Telegram бот успешно инициализирован")

    def test_connection(self):
        """Проверка подключения к Telegram API"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    log_info(f"✅ Telegram бот: @{bot_info['result']['username']}")
                    return True
            log_error(f"❌ Ошибка Telegram API: {response.text}")
            return False
        except Exception as e:
            log_error(f"❌ Ошибка подключения к Telegram: {e}")
            return False

    def send_message(self, message, reply_markup=None, retry_count=2):
        """Отправка сообщения в Telegram с повторными попытками"""
        if not self.token or not self.chat_id:
            return False
        
        for attempt in range(retry_count + 1):
            try:
                url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                payload = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
                
                # Используем только переданные кнопки (inline или reply)
                # Reply-кнопка главного меню установлена отдельно при старте
                if reply_markup:
                    payload['reply_markup'] = reply_markup
                
                # Увеличиваем таймаут для проблемных соединений
                timeout = 20 if attempt > 0 else 10
                response = requests.post(url, json=payload, timeout=timeout)
                
                if response.status_code == 200:
                    self.connection_issues = 0  # Сбрасываем счетчик проблем
                    return True
                else:
                    log_error(f"❌ Ошибка отправки в Telegram (попытка {attempt + 1}): {response.text}")
            except requests.exceptions.Timeout:
                log_error(f"⏰ Таймаут отправки в Telegram (попытка {attempt + 1})")
            except requests.exceptions.ConnectionError:
                log_error(f"🔌 Ошибка соединения с Telegram (попытка {attempt + 1})")
            except Exception as e:
                log_error(f"❌ Ошибка отправки в Telegram (попытка {attempt + 1}): {e}")
            # Пауза перед повторной попыткой
            if attempt < retry_count:
                time.sleep(2)
        self.connection_issues += 1
        if self.connection_issues >= 3:
            log_error("🚨 Множественные ошибки подключения к Telegram")
        return False
    
    def set_bot_commands(self):
        """Устанавливает команды бота в меню команд (синяя кнопка слева от поля ввода)"""
        try:
            # Удаляем reply-клавиатуру, если она была установлена ранее
            self.remove_reply_keyboard()
            
            # Устанавливаем команды бота
            url = f"https://api.telegram.org/bot{self.token}/setMyCommands"
            commands = [
                {'command': 'start', 'description': 'Главное меню'},
            ]
            payload = {'commands': commands}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                log_info("✅ Команды бота установлены в меню (синяя кнопка слева)")
            else:
                log_error(f"❌ Ошибка установки команд: {response.text}")
            return True
        except Exception as e:
            log_error(f"❌ Ошибка установки команд бота: {e}")
            return False
    
    def remove_reply_keyboard(self):
        """Удаляет reply-клавиатуру, чтобы команды бота отображались корректно"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': '🤖 <b>Бот готов к работе!</b>\n\nИспользуйте синюю кнопку "Меню" слева от поля ввода или команду /start',
                'parse_mode': 'HTML',
                'reply_markup': {
                    'remove_keyboard': True
                }
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                log_info("✅ Reply-клавиатура удалена, команды бота активны")
            return True
        except Exception as e:
            log_error(f"❌ Ошибка удаления клавиатуры: {e}")
            return False

    def start_message_listener(self):
        """Запуск слушателя сообщений"""
        def listener():
            log_info("🔍 Запущен слушатель команд Telegram...")
            while self.bot.is_running:
                try:
                    url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                    params = {'offset': self.last_update_id + 1, 'timeout': 20}  # Увеличили таймаут
                    response = requests.get(url, params=params, timeout=25)  # Увеличили общий таймаут
                    data = response.json()
                    if data["ok"] and data["result"]:
                        for update in data["result"]:
                            self.last_update_id = update["update_id"]
                            if "message" in update and "text" in update["message"]:
                                message_text = update["message"]["text"]
                                log_info(f"📨 Получена команда: {message_text}")
                                # Обрабатываем сообщение в отдельном потоке
                                threading.Thread(
                                    target=self.message_handler.handle_message,
                                    args=(message_text,),
                                    daemon=True
                                ).start()
                            # Обработка callback от inline кнопок
                            if "callback_query" in update:
                                callback_query = update["callback_query"]
                                callback_data = callback_query.get("data")
                                callback_id = callback_query.get("id")
                                log_info(f"📨 Получен callback: {callback_data}")
                                # Отвечаем на callback сразу
                                self.answer_callback_query(callback_id)
                                # Обрабатываем callback
                                threading.Thread(
                                    target=self.message_handler.handle_callback,
                                    args=(callback_data, callback_query),
                                    daemon=True
                                ).start()
                except requests.exceptions.Timeout:
                    continue
                except Exception as e:
                    log_error(f"❌ Ошибка в слушателе команд: {e}")
                    time.sleep(10)  # Увеличили паузу при ошибках
        threading.Thread(target=listener, daemon=True).start()

    def answer_callback_query(self, callback_id, text=None, show_alert=False):
        """Ответ на callback query (для inline-кнопок)"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
            payload = {
                'callback_query_id': callback_id,
                'show_alert': show_alert
            }
            if text:
                payload['text'] = text
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            log_error(f"❌ Ошибка ответа на callback: {e}")
            return False

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None):
        """Редактирование сообщения с обработкой ошибок"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/editMessageText"
            payload = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            if reply_markup:
                payload['reply_markup'] = reply_markup
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                # Если сообщение слишком старое или не найдено, отправляем новое
                error_data = response.json()
                if error_data.get('error_code') == 400 and 'message can\'t be edited' in error_data.get('description', '').lower():
                    log_info("⚠️ Сообщение слишком старое для редактирования, отправляем новое")
                    # Отправляем новое сообщение вместо редактирования
                    return self.send_message(text, reply_markup)
                return False
        except Exception as e:
            log_error(f"❌ Ошибка редактирования сообщения: {e}")
            # При ошибке отправляем новое сообщение
            return self.send_message(text, reply_markup)

    def smart_format(self, value, decimals=4):
        """Форматирует число, убирая лишние нули в конце"""
        formatted = f"{value:.{decimals}f}"
        # Убираем лишние нули после запятой
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted

    def send_market_update(self, market_data, signal, ml_confidence, ml_signal):
        """Отправка обновления рынка с расширенной информацией о позиции - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if not self.bot.settings.settings['enable_price_updates']:
            return
        symbol = self.bot.settings.trading_pairs['active_pair']
        pair_name = self.bot.settings.get_active_pair_name()
        
        # Добавляем информацию об EMA - ИСПРАВЛЕННЫЙ РАСЧЕТ
        ema_diff_percent = market_data.get('ema_diff_percent', 0) * 100
        # ПРАВИЛЬНОЕ ОПРЕДЕЛЕНИЕ СТАТУСА EMA
        if ema_diff_percent > 0.1:  # Значительный рост
            ema_status = "🟢 ВВЕРХ"
        elif ema_diff_percent < -0.1:  # Значительное падение
            ema_status = "🔴 ВНИЗ"
        else:  # Нейтрально
            ema_status = "⚪ НЕЙТРАЛЬНО"
            
        # Получаем баланс для расчета размера ставки
        balance = self.bot.exchange.get_balance()
        total_usdt = balance['total_usdt'] if balance else 0
        trade_amount_percent = self.bot.settings.settings['trade_amount_percent']
        position_size_usdt = total_usdt * trade_amount_percent
        
        # Расширенная информация о позиции
        position_info = ""
        # 🔧 ИСПРАВЛЕНИЕ: Проверяем, что позиция действительно открыта и имеет корректные данные
        if self.bot.position == 'long':
            strategy = self.bot.get_active_strategy()
            current_price = market_data['current_price']
            
            # 🔧 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: убеждаемся, что позиция действительно открыта
            # Проверяем наличие цены входа и размера позиции
            has_entry_price = hasattr(strategy, 'entry_price') and strategy.entry_price > 0
            has_position_size = (hasattr(strategy, 'position_size_usdt') and strategy.position_size_usdt > 0) or \
                                (hasattr(self.bot, 'current_position_size_usdt') and self.bot.current_position_size_usdt > 0)
            
            if not has_entry_price or not has_position_size:
                # Если нет данных о позиции, не показываем её как открытую
                log_info("⚠️ Позиция помечена как 'long', но отсутствуют данные о цене входа или размере. Не показываем позицию.")
                position_info = ""
            else:
                # 💰 ИСПОЛЬЗУЕМ ФИКСИРОВАННЫЙ РАЗМЕР ПОЗИЦИИ ИЗ СТРАТЕГИИ
                if hasattr(strategy, 'position_size_usdt') and strategy.position_size_usdt > 0:
                    position_size_usdt = strategy.position_size_usdt
                elif hasattr(self.bot, 'current_position_size_usdt') and self.bot.current_position_size_usdt > 0:
                    position_size_usdt = self.bot.current_position_size_usdt
                else:
                    position_size_usdt = total_usdt * trade_amount_percent if balance else 0
                    
                # 🔧 ИСПРАВЛЕНИЕ: Правильное отображение в зависимости от режима
                take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
                take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
                taker_fee = strategy.settings.get('taker_fee', 0.001)
                
                if take_profit_usdt > 0 and hasattr(strategy, 'entry_price') and strategy.entry_price > 0:
                    # 🔹 РЕЖИМ USDT (с поддержкой маленьких значений)
                    current_profit_usdt = (current_price - strategy.entry_price) / strategy.entry_price * position_size_usdt
                    fees_usdt = position_size_usdt * taker_fee * 2
                    net_profit_usdt = current_profit_usdt - fees_usdt
                    remaining_to_tp = max(0, take_profit_usdt - (current_profit_usdt - fees_usdt))
                    
                    # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
                    position_info = f"""
💼 <b>ПОЗИЦИЯ ОТКРЫТА (РЕЖИМ USDT)</b>
💰 <b>Размер ставки:</b> {position_size_usdt:.2f} USDT
🎯 <b>Цена входа:</b> {strategy.entry_price:.2f} USDT
📈 <b>Текущая прибыль:</b> {self.smart_format(current_profit_usdt, 4)} USDT
🎯 <b>До Take Profit:</b> +{self.smart_format(remaining_to_tp, 2)} USDT
🎯 <b>Цель TP:</b> {self.smart_format(take_profit_usdt, 4)} USDT
🛡️ <b>Комиссии:</b> {self.smart_format(fees_usdt, 4)} USDT
"""
                elif hasattr(strategy, 'entry_price') and strategy.entry_price > 0:
                    # 🔹 РЕЖИМ ПРОЦЕНТОВ (с поддержкой маленьких значений)
                    current_profit_percent = ((current_price - strategy.entry_price) / strategy.entry_price) * 100
                    total_fees_percent = taker_fee * 2 * 100
                    net_profit_percent = current_profit_percent - total_fees_percent
                    remaining_to_tp = max(0, take_profit_percent - (current_profit_percent - total_fees_percent))
                    current_profit_usdt = position_size_usdt * (current_profit_percent / 100)
                    fees_usdt = position_size_usdt * (total_fees_percent / 100)
                    
                    # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ:
                    position_info = f"""
💼 <b>ПОЗИЦИЯ ОТКРЫТА (РЕЖИМ %)</b>
💰 <b>Размер ставки:</b> {position_size_usdt:.2f} USDT
🎯 <b>Цена входа:</b> {strategy.entry_price:.2f} USDT
📈 <b>Текущая прибыль:</b> {self.smart_format(current_profit_percent, 4)}% ({self.smart_format(current_profit_usdt, 4)} USDT)
🎯 <b>До Take Profit:</b> +{self.smart_format(remaining_to_tp, 2)}%
🎯 <b>Цель TP:</b> {self.smart_format(take_profit_percent, 4)}%
🛡️ <b>Комиссии:</b> {self.smart_format(total_fees_percent, 2)}% ({self.smart_format(fees_usdt, 4)} USDT)
"""
    
        # Информация о размере следующей ставки (если позиция не открыта)
        next_trade_info = ""
        if self.bot.position != 'long':
            next_trade_info = f"💰 <b>Следующая ставка:</b> {position_size_usdt:.2f} USDT ({trade_amount_percent*100:.1f}%)"
            
        # ПРАВИЛЬНОЕ ФОРМАТИРОВАНИЕ СИГНАЛА
        signal_display = signal.upper()
        if signal == 'buy':
            signal_display = "🟢 ПОКУПКА"
        elif signal == 'sell':
            signal_display = "🔴 ПРОДАЖА"
        elif signal == 'wait':
            signal_display = "⚪ ОЖИДАНИЕ"
            
        message = f"""
📈 <b>ОБНОВЛЕНИЕ РЫНКА</b>
💱 <b>Пара:</b> {pair_name}
💰 <b>Цена:</b> {market_data['current_price']:.2f} USDT
📊 <b>24ч:</b> {market_data.get('price_change_24h', 0):+.2f}%
📈 <b>EMA:</b> {ema_status} ({ema_diff_percent:+.2f}%)
🎯 <b>Сигнал:</b> {signal_display}
🤖 <b>ML:</b> {ml_signal} ({ml_confidence:.1%})
{next_trade_info}
{position_info}
⏰ {datetime.now().strftime("%H:%M:%S")}
"""
        self.send_message(message)

    def send_trade_signal(self, signal, market_data, ml_confidence, ml_signal, strategy_name, order_message, position_size_usdt=0, profit_usdt=0):
        """Отправка сигнала о сделке с информацией о размере позиции - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if signal == 'buy':
            emoji = "🟢"
            action = "ПОКУПКА"
        else:
            emoji = "🔴"
            action = "ПРОДАЖА"
            
        # Добавляем EMA в информацию о сделке
        ema_diff_percent = market_data.get('ema_diff_percent', 0) * 100
        # ПРАВИЛЬНОЕ ОПРЕДЕЛЕНИЕ СТАТУСА EMA
        if ema_diff_percent > 0.1:
            ema_status = "🟢 ВВЕРХ"
        elif ema_diff_percent < -0.1:
            ema_status = "🔴 ВНИЗ"
        else:
            ema_status = "⚪ НЕЙТРАЛЬНО"
            
        # Информация о размере позиции
        position_info = ""
        if position_size_usdt > 0:
            position_info = f"💰 <b>Размер ставки:</b> {position_size_usdt:.2f} USDT"
            
        # 🔧 ИСПРАВЛЕНИЕ: Информация о режиме TP с поддержкой маленьких значений
        strategy = self.bot.get_active_strategy()
        take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
        
        tp_info = ""
        if take_profit_usdt > 0:
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            tp_info = f"🎯 <b>Take Profit:</b> {self.smart_format(take_profit_usdt, 4)} USDT"
        else:
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            tp_info = f"🎯 <b>Take Profit:</b> {self.smart_format(take_profit_percent, 4)}%"
    
        # Информация о прибыли
        profit_info = ""
        if profit_usdt != 0:
            profit_emoji = "📈" if profit_usdt > 0 else "📉"
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            profit_info = f"{profit_emoji} <b>Прибыль:</b> {self.smart_format(profit_usdt, 4)} USDT"
            
        message = f"""
{emoji} <b>СДЕЛКА {action}</b>
🎯 <b>Стратегия:</b> {strategy_name}
💱 <b>Пара:</b> {self.bot.settings.get_active_pair_name()}
💰 <b>Цена:</b> {market_data['current_price']:.2f} USDT
{position_info}
{tp_info}
📈 <b>EMA:</b> {ema_status} ({ema_diff_percent:+.2f}%)
🤖 <b>ML сигнал:</b> {ml_signal} ({ml_confidence:.1%})
{profit_info}
📝 <b>Статус:</b> {order_message}
{'🔸 ДЕМО-РЕЖИМ' if self.bot.settings.settings['demo_mode'] else '🔹 РЕАЛЬНАЯ СДЕЛКА'}
"""
        self.send_message(message)

    def send_balance_update(self, force_send=False):
        """Отправка обновления баланса только при изменениях"""
        balance = self.bot.exchange.get_balance()
        if not balance:
            return
        # Проверяем изменился ли баланс
        balance_changed = (
            self.last_balance is None or
            abs(balance['total_usdt'] - self.last_balance['total_usdt']) > 0.01 or  # Изменение > 0.01 USDT
            abs(balance['free_usdt'] - self.last_balance['free_usdt']) > 0.01 or
            abs(balance['total_btc'] - self.last_balance['total_btc']) > 0.000001   # Изменение > 0.000001 BTC
        )
        if not balance_changed and not force_send:
            log_info("💰 Баланс не изменился - сообщение не отправляем")
            return
        self.last_balance = balance.copy()  # Сохраняем текущий баланс
        # Рассчитываем размер следующей ставки
        trade_amount_percent = self.bot.settings.settings['trade_amount_percent']
        next_trade_amount = balance['total_usdt'] * trade_amount_percent
        
        # 🔧 ДОБАВЛЯЕМ ИНФОРМАЦИЮ О РЕЖИМЕ TP
        strategy = self.bot.get_active_strategy()
        take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
        
        tp_info = ""
        if take_profit_usdt > 0:
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            tp_info = f"🎯 <b>Take Profit:</b> {self.smart_format(take_profit_usdt, 4)} USDT"
        else:
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            tp_info = f"🎯 <b>Take Profit:</b> {self.smart_format(take_profit_percent, 4)}%"
            
        message = f"""
💰 <b>ОБНОВЛЕНИЕ БАЛАНСА</b>
💵 <b>USDT:</b> {balance['total_usdt']:.2f}
• Свободно: {balance['free_usdt']:.2f}
• Занято: {balance['used_usdt']:.2f}
₿ <b>BTC:</b> {balance['total_btc']:.6f}
• Свободно: {balance['free_btc']:.6f}
🎯 <b>Следующая ставка:</b> {next_trade_amount:.2f} USDT ({trade_amount_percent*100:.1f}%)
{tp_info}
📊 <b>Всего сделок:</b> {self.bot.metrics.total_trades}
🎯 <b>Win Rate:</b> {self.bot.metrics.win_rate:.1f}%
⏰ {datetime.now().strftime("%H:%M:%S")}
"""
        self.send_message(message)

    def send_welcome_message(self):
        """Отправка приветственного сообщения"""
        if not self.token or not self.chat_id:
            return
        # Рассчитываем размер ставки на основе текущего баланса
        balance = self.bot.exchange.get_balance()
        trade_amount_percent = self.bot.settings.settings['trade_amount_percent']
        next_trade_amount = balance['total_usdt'] * trade_amount_percent if balance else 0
        
        # 🔧 ИСПРАВЛЕНИЕ: Добавляем информацию о режиме TP с поддержкой маленьких значений
        strategy = self.bot.get_active_strategy()
        take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
        
        tp_info = ""
        if take_profit_usdt > 0:
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            tp_info = f"🎯 <b>Take Profit:</b> {self.smart_format(take_profit_usdt, 4)} USDT"
        else:
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            tp_info = f"🎯 <b>Take Profit:</b> {self.smart_format(take_profit_percent, 4)}%"
            
        message = f"""
🤖 <b>ТОРГОВЫЙ БОТ АКТИВИРОВАН</b>
✅ <b>Статус:</b> Бот запущен и работает
💱 <b>Пара:</b> {self.bot.settings.get_active_pair_name()}
🎯 <b>Стратегия:</b> {self.bot.settings.get_active_strategy_name()}
🤖 <b>ML:</b> {'✅ ВКЛЮЧЕН' if self.bot.settings.ml_settings['enabled'] else '❌ ВЫКЛЮЧЕН'}
💰 <b>Размер ставки:</b> {next_trade_amount:.2f} USDT ({trade_amount_percent*100:.1f}%)
{tp_info}
📊 <b>Используйте команды:</b>
• /start - Главное меню
• 📊 Статус - Текущее состояние
• 💼 Инфо аккаунта - Баланс и статистика
• ⚙️ Настройки - Параметры бота
⏰ {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
"""
        self.send_message(message)

    def _calculate_profit_info_fallback(self, strategy, current_price):
        """Fallback метод для расчета информации о прибыли - УМНОЕ ФОРМАТИРОВАНИЕ"""
        take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
        taker_fee = strategy.settings.get('taker_fee', 0.001)
        position_size = getattr(strategy, 'position_size_usdt', 0)
        
        if take_profit_usdt > 0:
            current_profit_usdt = (current_price - strategy.entry_price) / strategy.entry_price * position_size
            fees_usdt = position_size * taker_fee * 2
            net_profit_usdt = current_profit_usdt - fees_usdt
            remaining_to_tp = max(0, take_profit_usdt - net_profit_usdt)
            
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            return {
                'mode': 'USDT',
                'current_profit': net_profit_usdt,
                'current_profit_formatted': f"{self.smart_format(net_profit_usdt, 4)} USDT",
                'take_profit': take_profit_usdt,
                'take_profit_formatted': f"{self.smart_format(take_profit_usdt, 4)} USDT",
                'remaining_to_tp': remaining_to_tp,
                'remaining_formatted': f"+{self.smart_format(remaining_to_tp, 2)} USDT",
                'fees': fees_usdt
            }
        else:
            current_profit_percent = ((current_price - strategy.entry_price) / strategy.entry_price) * 100
            total_fees_percent = taker_fee * 2 * 100
            net_profit_percent = current_profit_percent - total_fees_percent
            remaining_to_tp = max(0, take_profit_percent - net_profit_percent)
            current_profit_usdt = position_size * (net_profit_percent / 100)
            
            # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
            return {
                'mode': 'percent',
                'current_profit': net_profit_percent,
                'current_profit_formatted': f"{self.smart_format(net_profit_percent, 4)}%",
                'current_profit_usdt': current_profit_usdt,
                'current_profit_usdt_formatted': f"{self.smart_format(current_profit_usdt, 4)} USDT",
                'take_profit': take_profit_percent,
                'take_profit_formatted': f"{self.smart_format(take_profit_percent, 4)}%",
                'remaining_to_tp': remaining_to_tp,
                'remaining_formatted': f"+{self.smart_format(remaining_to_tp, 2)}%",
                'fees': total_fees_percent
            }

    def send_detailed_position_info(self):
        """Отправка детальной информации о позиции с УМНЫМ форматированием"""
        if not self.bot.position == 'long':
            return
            
        strategy = self.bot.get_active_strategy()
        market_data = self.bot.exchange.get_market_data(self.bot.settings.trading_pairs['active_pair'])
        if not market_data:
            return
            
        current_price = market_data['current_price']
        
        # Используем метод из стратегии для получения информации о прибыли
        if hasattr(strategy, 'get_current_profit_info'):
            profit_info = strategy.get_current_profit_info(current_price)
        else:
            # Fallback если метод не реализован
            profit_info = self._calculate_profit_info_fallback(strategy, current_price)
        
        if profit_info.get('mode') == 'USDT':
            message = f"""
📊 <b>ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПОЗИЦИИ (USDT)</b>
💰 <b>Размер позиции:</b> {getattr(strategy, 'position_size_usdt', 0):.2f} USDT
🎯 <b>Цена входа:</b> {strategy.entry_price:.2f} USDT
💰 <b>Текущая цена:</b> {current_price:.2f} USDT
📈 <b>Текущая прибыль:</b> {profit_info['current_profit_formatted']}
🎯 <b>Take Profit:</b> {profit_info['take_profit_formatted']}
📊 <b>До Take Profit:</b> {profit_info['remaining_formatted']}
🛡️ <b>Комиссии:</b> {self.smart_format(profit_info['fees'], 4)} USDT
⏰ <b>Открыта:</b> {datetime.fromtimestamp(strategy.position_opened_at).strftime('%H:%M:%S') if hasattr(strategy, 'position_opened_at') else 'N/A'}
"""
        else:
            message = f"""
📊 <b>ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПОЗИЦИИ (%)</b>
💰 <b>Размер позиции:</b> {getattr(strategy, 'position_size_usdt', 0):.2f} USDT
🎯 <b>Цена входа:</b> {strategy.entry_price:.2f} USDT
💰 <b>Текущая цена:</b> {current_price:.2f} USDT
📈 <b>Текущая прибыль:</b> {profit_info['current_profit_formatted']} ({profit_info.get('current_profit_usdt_formatted', 'N/A')})
🎯 <b>Take Profit:</b> {profit_info['take_profit_formatted']}
📊 <b>До Take Profit:</b> {profit_info['remaining_formatted']}
🛡️ <b>Комиссии:</b> {self.smart_format(profit_info['fees'], 2)}%
⏰ <b>Открыта:</b> {datetime.fromtimestamp(strategy.position_opened_at).strftime('%H:%M:%S') if hasattr(strategy, 'position_opened_at') else 'N/A'}
"""
        self.send_message(message)