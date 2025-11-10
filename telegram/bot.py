"""
TELEGRAM БОТ ДЛЯ УПРАВЛЕНИЯ - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
import requests
import threading
import time
import os
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
        
        # Настройка прокси для Telegram (если указано в .env)
        self.proxies = None
        self.use_proxy = False
        proxy_url = os.getenv('PROXY_URL')
        if proxy_url:
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url,
            }
            self.use_proxy = True
            # Скрываем чувствительные данные при логировании
            safe_proxy = proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url
            log_info(f"🔒 Telegram использует прокси: {safe_proxy}")
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
        # Отправляем кнопку Web App
        self.send_webapp_button()
        # Отправляем приветственное сообщение один раз при запуске
        self.send_startup_message()
        log_info("✅ Telegram бот успешно инициализирован")

    def test_connection(self):
        """Проверка подключения к Telegram API"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            # Увеличиваем таймаут для прокси, уменьшаем для прямого подключения
            timeout = 20 if self.use_proxy else 10
            response = requests.get(url, timeout=timeout, proxies=self.proxies)
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
                
                # Адаптивный таймаут: больше для прокси и повторных попыток
                if self.use_proxy:
                    timeout = 25 if attempt > 0 else 15
                else:
                    timeout = 15 if attempt > 0 else 8
                response = requests.post(url, json=payload, timeout=timeout, proxies=self.proxies)
                
                if response.status_code == 200:
                    self.connection_issues = 0  # Сбрасываем счетчик проблем
                    # Возвращаем message_id из ответа для последующего редактирования
                    try:
                        result = response.json()
                        if result.get('ok') and 'result' in result:
                            return result['result'].get('message_id')
                    except:
                        pass
                    return True
                else:
                    log_error(f"❌ Ошибка отправки в Telegram (попытка {attempt + 1}): {response.text}")
            except requests.exceptions.Timeout:
                log_error(f"⏰ Таймаут отправки в Telegram (попытка {attempt + 1})")
            except requests.exceptions.ConnectionError:
                log_error(f"🔌 Ошибка соединения с Telegram (попытка {attempt + 1})")
            except Exception as e:
                log_error(f"❌ Ошибка отправки в Telegram (попытка {attempt + 1}): {e}")
            # Пауза перед повторной попыткой (короче для прямого подключения)
            if attempt < retry_count:
                pause = 3 if self.use_proxy else 1
                time.sleep(pause)
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
            timeout = 15 if self.use_proxy else 8
            response = requests.post(url, json=payload, timeout=timeout, proxies=self.proxies)
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
                'text': ' ',  # Минимальный текст для удаления клавиатуры
                'reply_markup': {
                    'remove_keyboard': True
                }
            }
            timeout = 15 if self.use_proxy else 8
            response = requests.post(url, json=payload, timeout=timeout, proxies=self.proxies)
            if response.status_code == 200:
                log_info("✅ Reply-клавиатура удалена, команды бота активны")
            return True
        except Exception as e:
            log_error(f"❌ Ошибка удаления клавиатуры: {e}")
            return False
    
    def send_webapp_button(self):
        """Отправляет кнопку для открытия Web App"""
        try:
            webapp_url = os.getenv('WEBAPP_URL', 'https://your-server.com')
            log_info(f"🌐 Создание кнопки Web App с URL: {webapp_url}")
            
            if webapp_url == 'https://your-server.com':
                log_error("⚠️ WEBAPP_URL не установлена! Используется заглушка. Установите переменную окружения WEBAPP_URL.")
            
            message = """
🌐 <b>Web App доступен!</b>

Откройте полнофункциональный веб-интерфейс для управления ботом.

<b>Возможности Web App:</b>
📊 Мониторинг в реальном времени
⚙️ Управление настройками
📈 Детальная статистика
💰 Информация о балансе
🎯 Управление позициями

<i>Нажмите кнопку ниже для открытия</i>
"""
            
            reply_markup = {
                "inline_keyboard": [[
                    {
                        "text": "🚀 Открыть Web App",
                        "web_app": {"url": webapp_url}
                    }
                ]]
            }
            
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'reply_markup': reply_markup
            }
            
            timeout = 15 if self.use_proxy else 8
            response = requests.post(url, json=payload, timeout=timeout, proxies=self.proxies)
            
            if response.status_code == 200:
                log_info("✅ Кнопка Web App отправлена")
                return True
            else:
                log_error(f"❌ Ошибка отправки кнопки Web App: {response.text}")
                return False
                
        except Exception as e:
            log_error(f"❌ Ошибка отправки кнопки Web App: {e}")
            return False
    
    def send_startup_message(self):
        """Отправляет приветственное сообщение один раз при запуске бота"""
        if not self.token or not self.chat_id:
            return
        try:
            message = '🤖 <b>Бот готов к работе!</b>\n\nИспользуйте синюю кнопку "Меню" слева от поля ввода или команду /start'
            self.send_message(message)
        except Exception as e:
            log_error(f"❌ Ошибка отправки приветственного сообщения: {e}")

    def start_message_listener(self):
        """Запуск слушателя сообщений"""
        def listener():
            log_info("🔍 Запущен слушатель команд Telegram...")
            while self.bot.is_running:
                try:
                    url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                    # Long polling таймаут (время ожидания новых сообщений на сервере)
                    polling_timeout = 15 if self.use_proxy else 10
                    # HTTP таймаут (должен быть больше polling_timeout)
                    http_timeout = polling_timeout + 10
                    params = {'offset': self.last_update_id + 1, 'timeout': polling_timeout}
                    response = requests.get(url, params=params, timeout=http_timeout, proxies=self.proxies)
                    data = response.json()
                    if data["ok"] and data["result"]:
                        for update in data["result"]:
                            self.last_update_id = update["update_id"]
                            if "message" in update and "text" in update["message"]:
                                message_text = update["message"]["text"]
                                message_chat_id = update["message"]["chat"]["id"]
                                log_info(f"📨 Получена команда: {message_text}")
                                # Обрабатываем сообщение в отдельном потоке
                                threading.Thread(
                                    target=self.message_handler.handle_message,
                                    args=(message_text, message_chat_id),
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
                    # Таймаут - это нормально для long polling, просто продолжаем
                    continue
                except Exception as e:
                    log_error(f"❌ Ошибка в слушателе команд: {e}")
                    # Меньше пауза для быстрого восстановления
                    time.sleep(3)
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
            timeout = 15 if self.use_proxy else 8
            response = requests.post(url, json=payload, timeout=timeout, proxies=self.proxies)
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
            timeout = 15 if self.use_proxy else 8
            response = requests.post(url, json=payload, timeout=timeout, proxies=self.proxies)
            
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
        open_positions_count = 0
        log_info(f"📊 Telegram send_market_update: начало, position={self.bot.position}")
        # 🔧 ИСПРАВЛЕНИЕ: Проверяем, что позиция действительно открыта и имеет корректные данные
        if self.bot.position == 'long':
            strategy = self.bot.get_active_strategy()
            current_price = market_data['current_price']
            
            # 🔧 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: убеждаемся, что позиция действительно открыта
            # Проверяем наличие цены входа и размера позиции
            has_entry_price = hasattr(strategy, 'entry_price') and strategy.entry_price > 0
            has_position_size = (hasattr(strategy, 'position_size_usdt') and strategy.position_size_usdt > 0) or \
                                (hasattr(self.bot, 'current_position_size_usdt') and self.bot.current_position_size_usdt > 0)
            
            # 🔧 ПОЛУЧАЕМ КОЛИЧЕСТВО ОТКРЫТЫХ ПОЗИЦИЙ И РАССЧИТЫВАЕМ РАЗМЕР СТАВКИ
            open_buy_trades = []
            all_open_trades = []
            open_positions_count = 0
            if not has_entry_price or not has_position_size:
                # Если нет данных о позиции, не показываем её как открытую
                log_info("⚠️ Позиция помечена как 'long', но отсутствуют данные о цене входа или размере. Не показываем позицию.")
                position_info = ""
                open_positions_count = 0
            else:
                # 🔧 ПОДСЧЕТ ОТКРЫТЫХ ПОЗИЦИЙ - ИСПОЛЬЗУЕМ position_state.json КАК ОСНОВНОЙ ИСТОЧНИК
                # Причина: KuCoin API не возвращает старые сделки (history только ~1 сделка)
                import json
                import os
                try:
                    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'position_state.json')
                    if os.path.exists(state_file):
                        with open(state_file, 'r') as f:
                            position_state = json.load(f)
                        
                        # Считаем открытые позиции по НОВОЙ структуре (массив positions)
                        open_positions_count = 0
                        total_position_size_all_pairs = 0
                        
                        for pair_symbol, pair_data in position_state.items():
                            # Новая структура: проверяем массив positions
                            positions = pair_data.get('positions', [])
                            
                            if positions:
                                # Количество открытых позиций = длина массива
                                pair_positions_count = len(positions)
                                pair_total_size = pair_data.get('total_position_size_usdt', 0)
                                
                                open_positions_count += pair_positions_count
                                total_position_size_all_pairs += pair_total_size
                                
                                log_info(f"📊 Telegram: Пара {pair_symbol} имеет {pair_positions_count} позиций, общий размер: {pair_total_size:.2f} USDT")
                                
                                # Логируем каждую позицию
                                for pos in positions:
                                    pos_id = pos.get('id', 'unknown')
                                    pos_price = pos.get('entry_price', 0)
                                    pos_size = pos.get('position_size_usdt', 0)
                                    is_legacy = pos.get('is_legacy', False)
                                    log_info(f"   - Позиция {pos_id}: {pos_size:.2f} USDT @ {pos_price:.2f} {'(legacy)' if is_legacy else ''}")
                        
                        log_info(f"📊 Telegram: Всего открытых позиций по всем парам: {open_positions_count}")
                        
                        # Для текущей пары берем данные из position_state
                        current_pair_data = position_state.get(symbol, {})
                        position_size_for_current = current_pair_data.get('position_size_usdt', 0)
                    else:
                        log_info(f"📊 Telegram: Файл position_state.json не найден")
                        open_positions_count = 1 if has_entry_price and has_position_size else 0
                        total_position_size_all_pairs = 0
                except Exception as e:
                    log_error(f"❌ Ошибка чтения position_state.json: {e}")
                    open_positions_count = 1 if has_entry_price and has_position_size else 0
                    total_position_size_all_pairs = 0
                
                # 💰 РАСЧЕТ РАЗМЕРА СТАВКИ
                log_info(f"📊 Telegram: Проверка количества позиций для расчета ставки: {open_positions_count}")
                
                # Если открыто 2+ позиций, показываем сумму всех ставок из position_state
                if open_positions_count >= 2:
                    position_size_usdt = total_position_size_all_pairs
                    log_info(f"📊 Открыто позиций: {open_positions_count}, сумма всех ставок: {position_size_usdt:.2f} USDT")
                else:
                    # Одна позиция - берем размер из стратегии или position_state
                    if hasattr(strategy, 'position_size_usdt') and strategy.position_size_usdt > 0:
                        position_size_usdt = strategy.position_size_usdt
                    elif hasattr(self.bot, 'current_position_size_usdt') and self.bot.current_position_size_usdt > 0:
                        position_size_usdt = self.bot.current_position_size_usdt
                    else:
                        position_size_usdt = total_usdt * trade_amount_percent if balance else 0
                    
                    log_info(f"📊 Одна позиция, размер ставки: {position_size_usdt:.2f} USDT")
                    
                # 🔧 ОПРЕДЕЛЕНИЕ ЦЕНЫ ВХОДА ДЛЯ TP
                # Если открыто 2+ позиций, используем МАКСИМАЛЬНУЮ цену входа (чтобы не продавать в минус)
                # Если 1 позиция, используем её цену входа
                try:
                    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'position_state.json')
                    if os.path.exists(state_file):
                        with open(state_file, 'r') as f:
                            position_state_for_tp = json.load(f)
                        current_pair_data = position_state_for_tp.get(symbol, {})
                        
                        # Проверяем, есть ли max_entry_price (для нескольких позиций)
                        if open_positions_count >= 2 and 'max_entry_price' in current_pair_data:
                            entry_price_for_tp = current_pair_data['max_entry_price']
                            log_info(f"📊 Telegram: Используем MAX цену входа для TP: {entry_price_for_tp:.2f} (позиций: {open_positions_count})")
                        else:
                            entry_price_for_tp = strategy.entry_price if hasattr(strategy, 'entry_price') else 0
                            log_info(f"📊 Telegram: Используем стандартную цену входа для TP: {entry_price_for_tp:.2f}")
                    else:
                        entry_price_for_tp = strategy.entry_price if hasattr(strategy, 'entry_price') else 0
                except Exception as e:
                    log_error(f"❌ Ошибка чтения max_entry_price: {e}")
                    entry_price_for_tp = strategy.entry_price if hasattr(strategy, 'entry_price') else 0
                
                # 🔧 ИСПРАВЛЕНИЕ: Правильное отображение в зависимости от режима
                take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
                take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
                taker_fee = strategy.settings.get('taker_fee', 0.001)
                
                if take_profit_usdt > 0 and entry_price_for_tp > 0:
                    # 🔹 РЕЖИМ USDT (с поддержкой маленьких значений)
                    current_profit_usdt = (current_price - entry_price_for_tp) / entry_price_for_tp * position_size_usdt
                    fees_usdt = position_size_usdt * taker_fee * 2
                    net_profit_usdt = current_profit_usdt - fees_usdt
                    remaining_to_tp = max(0, take_profit_usdt - (current_profit_usdt - fees_usdt))
                    
                    # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ
                    log_info(f"📊 Telegram: Формирование сообщения USDT, количество позиций: {open_positions_count}")
                    # Всегда показываем количество позиций
                    positions_count_text = f"📊 <b>Количество открытых позиций:</b> {open_positions_count}\n"
                    position_info = f"""
💼 <b>ПОЗИЦИЯ ОТКРЫТА (РЕЖИМ USDT)</b>
{positions_count_text}💰 <b>Размер ставки:</b> {position_size_usdt:.2f} USDT
🎯 <b>Цена входа (TP):</b> {entry_price_for_tp:.2f} USDT
📈 <b>Текущая прибыль:</b> {self.smart_format(current_profit_usdt, 4)} USDT
🎯 <b>До Take Profit:</b> +{self.smart_format(remaining_to_tp, 2)} USDT
🎯 <b>Цель TP:</b> {self.smart_format(take_profit_usdt, 4)} USDT
🛡️ <b>Комиссии:</b> {self.smart_format(fees_usdt, 4)} USDT
"""
                elif entry_price_for_tp > 0:
                    # 🔹 РЕЖИМ ПРОЦЕНТОВ (с поддержкой маленьких значений)
                    current_profit_percent = ((current_price - entry_price_for_tp) / entry_price_for_tp) * 100
                    total_fees_percent = taker_fee * 2 * 100
                    net_profit_percent = current_profit_percent - total_fees_percent
                    remaining_to_tp = max(0, take_profit_percent - (current_profit_percent - total_fees_percent))
                    current_profit_usdt = position_size_usdt * (current_profit_percent / 100)
                    fees_usdt = position_size_usdt * (total_fees_percent / 100)
                    
                    # 🔧 УМНОЕ ФОРМАТИРОВАНИЕ:
                    log_info(f"📊 Telegram: Формирование сообщения %, количество позиций: {open_positions_count}")
                    # Всегда показываем количество позиций
                    positions_count_text = f"📊 <b>Количество открытых позиций:</b> {open_positions_count}\n"
                    position_info = f"""
💼 <b>ПОЗИЦИЯ ОТКРЫТА (РЕЖИМ %)</b>
{positions_count_text}💰 <b>Размер ставки:</b> {position_size_usdt:.2f} USDT
🎯 <b>Цена входа (TP):</b> {entry_price_for_tp:.2f} USDT
📈 <b>Текущая прибыль:</b> {current_profit_percent:.2f}% ({self.smart_format(current_profit_usdt, 4)} USDT)
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
        log_info(f"📊 Telegram: ФИНАЛЬНОЕ значение open_positions_count перед отправкой: {open_positions_count}")
        log_info(f"📊 Telegram: position_info содержит: {position_info[:200]}...")
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
                'current_profit_formatted': f"{net_profit_percent:.2f}%",
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