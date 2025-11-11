"""
МЕНЮ TELEGRAM БОТА
"""
import os
from utils.logger import log_info

class MenuManager:
    def __init__(self, trading_bot):
        self.bot = trading_bot

    def smart_format(self, value, decimals=4):
        """Форматирует число, убирая лишние нули в конце"""
        formatted = f"{value:.{decimals}f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted

    def send_main_menu(self):
        """Главное меню - теперь использует inline-кнопки"""
        return self.send_main_menu_inline()

    def send_settings_menu(self):
        """Меню настроек с inline-кнопками"""
        tp_info = self.bot.get_take_profit_info()
        if tp_info['mode'] == 'USDT':
            tp_display = f"{self.smart_format(tp_info['take_profit_usdt'], 4)} USDT"
        else:
            tp_display = f"{self.smart_format(tp_info['take_profit_percent'], 4)}%"

        # Получаем порог EMA из стратегии
        strategy = self.bot.get_active_strategy()
        ema_threshold = strategy.settings.get('ema_threshold', 0.0025) * 100  # Конвертируем в проценты

        message = f"""
⚙️ <b>НАСТРОЙКИ БОТА</b>

🎯 <b>Текущие настройки:</b>
• Пара: {self.bot.settings.get_active_pair_name()}
• Стратегия: {self.bot.settings.get_active_strategy_name()}
• Размер ставки: {self.bot.settings.settings['trade_amount_percent'] * 100:.1f}%
• Take Profit: {tp_display}
• EMA порог: {self.smart_format(ema_threshold, 2)}%
• Торговля: {'✅ ВКЛ' if self.bot.settings.settings['trading_enabled'] else '❌ ВЫКЛ'}
• Режим: {'🟢 ДЕМО' if self.bot.settings.settings['demo_mode'] else '🔴 РЕАЛЬНЫЙ'}

💡 <b>Выберите категорию:</b>
"""

        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': f'💱 Пара', 'callback_data': 'settings_pairs'},
                    {'text': f'🎯 Стратегия', 'callback_data': 'settings_strategy'}
                ],
                [
                    {'text': f'💰 Размер: {self.bot.settings.settings["trade_amount_percent"] * 100:.1f}%', 'callback_data': 'settings_trade_amount'},
                    {'text': f'📈 EMA: {self.smart_format(ema_threshold, 2)}%', 'callback_data': 'settings_ema_threshold'}
                ],
                [
                    {'text': '🤖 ML Настройки', 'callback_data': 'settings_ml'},
                    {'text': '⚙️ EMA Настройки', 'callback_data': 'settings_ema'}
                ],
                [
                    {'text': '⚙️ Риск-менеджмент', 'callback_data': 'settings_risk'},
                    {'text': f'🔄 Обновления: {"✅" if self.bot.settings.settings["enable_price_updates"] else "❌"}', 'callback_data': 'settings_toggle_updates'}
                ],
                [
                    {'text': '🏠 Главное меню', 'callback_data': 'main_menu'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_ema_settings_menu(self):
        """Меню настроек EMA стратегии с УМНЫМ ФОРМАТИРОВАНИЕМ"""
        strategy = self.bot.get_active_strategy()
        
        take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
        take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
        
        # Определяем режим и форматируем значение
        if take_profit_usdt > 0:
            tp_display = f"{self.smart_format(take_profit_usdt, 4)} USDT"
            tp_mode = "USDT"
        else:
            tp_display = f"{self.smart_format(take_profit_percent, 4)}%"
            tp_mode = "%"
        
        trailing_stop_status = "✅ ВКЛ" if strategy.settings.get('trailing_stop', False) else "❌ ВЫКЛ"
        stop_loss = strategy.settings.get('stop_loss_percent', 1.5)
        min_hold_time = strategy.settings.get('min_hold_time', 300) // 60
        
        # EMA периоды и порог
        ema_fast = strategy.settings.get('ema_fast_period', 9)
        ema_slow = strategy.settings.get('ema_slow_period', 21)
        ema_threshold = strategy.settings.get('ema_threshold', 0.0025) * 100  # Конвертируем в проценты

        message = f"""
⚙️ <b>НАСТРОЙКИ EMA СТРАТЕГИИ</b>

📊 <b>EMA Периоды:</b>
   • Быстрая EMA: <b>{ema_fast}</b>
   • Медленная EMA: <b>{ema_slow}</b>
   • Порог EMA: <b>{self.smart_format(ema_threshold, 2)}%</b>

🎯 <b>Take Profit:</b> {tp_display}
🛑 <b>Stop Loss:</b> {self.smart_format(stop_loss, 1)}%
📉 <b>Trailing Stop:</b> {trailing_stop_status}
⏰ <b>Min Hold Time:</b> {min_hold_time} мин
🔄 <b>TP режим:</b> {tp_mode}

💡 <b>Выберите параметр для настройки:</b>
💡 <b>Примечание:</b> Порог EMA настраивается в общем меню настроек
"""
        
        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': f'📊 Fast: {ema_fast}', 'callback_data': 'ema_fast'},
                    {'text': f'📊 Slow: {ema_slow}', 'callback_data': 'ema_slow'}
                ],
                [
                    {'text': f'🎯 TP: {tp_display}', 'callback_data': 'ema_tp'},
                    {'text': f'🛑 SL: {self.smart_format(stop_loss, 1)}%', 'callback_data': 'ema_sl'}
                ],
                [
                    {'text': f'📉 Trailing: {trailing_stop_status}', 'callback_data': 'ema_trailing'},
                    {'text': f'⏰ Hold: {min_hold_time} мин', 'callback_data': 'ema_hold_time'}
                ],
                [
                    {'text': f'🔄 TP режим: {tp_mode}', 'callback_data': 'ema_tp_mode'},
                    {'text': '🔙 Назад', 'callback_data': 'settings'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_strategy_menu(self):
        """Меню выбора стратегии с inline-кнопками"""
        current_strategy = self.bot.settings.strategy_settings['active_strategy']
        
        message = """
🎯 <b>ВЫБОР СТРАТЕГИИ</b>

💡 <b>Доступные стратегии:</b>
• 📈 EMA + ML - Комбинация EMA кроссовера и Machine Learning
• ⚡ Price Action - Торговля по чистому движению цены
• 🎯 MACD + RSI - Комбинация индикаторов MACD и RSI
• 📊 Bollinger Bands - Торговля на отскоках от границ Bollinger Bands

Выберите стратегию:
"""

        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': f"{'✅' if current_strategy == 'ema_ml' else ''} 📈 EMA + ML", 'callback_data': 'strategy_ema_ml'},
                    {'text': f"{'✅' if current_strategy == 'price_action' else ''} ⚡ Price Action", 'callback_data': 'strategy_price_action'}
                ],
                [
                    {'text': f"{'✅' if current_strategy == 'macd_rsi' else ''} 🎯 MACD + RSI", 'callback_data': 'strategy_macd_rsi'},
                    {'text': f"{'✅' if current_strategy == 'bollinger' else ''} 📊 Bollinger", 'callback_data': 'strategy_bollinger'}
                ],
                [
                    {'text': '🔙 Назад к настройкам', 'callback_data': 'settings'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_pairs_menu(self):
        """Меню выбора торговой пары с inline-кнопками (динамическое)"""
        current_pair = self.bot.settings.trading_pairs['active_pair']
        available_pairs = self.bot.settings.trading_pairs['available_pairs']
        
        # Формируем список доступных пар
        pairs_list = []
        for pair_id, pair_name in available_pairs.items():
            pairs_list.append(f"• {pair_name} ({pair_id})")
        
        pairs_text = "\n".join(pairs_list) if pairs_list else "• Нет доступных пар"
        
        message = f"""
💱 <b>ВЫБОР ТОРГОВОЙ ПАРЫ</b>

💡 <b>Доступные пары:</b>
{pairs_text}

Выберите торговую пару:
"""
        
        # Формируем кнопки для пар (каждая пара в отдельной строке)
        inline_keyboard = {'inline_keyboard': []}
        pairs_items = list(available_pairs.items())
        
        # Добавляем каждую кнопку пары в отдельную строку
        for pair_id, pair_name in pairs_items:
            is_active = '✅' if current_pair == pair_id else ''
            inline_keyboard['inline_keyboard'].append([{
                'text': f"{is_active} {pair_name}",
                'callback_data': f'pair_{pair_id}'
            }])
        
        # Добавляем кнопки управления
        inline_keyboard['inline_keyboard'].append([
            {'text': '➕ Добавить пару', 'callback_data': 'pair_add'},
            {'text': '🗑️ Удалить пару', 'callback_data': 'pair_delete_menu'}
        ])
        inline_keyboard['inline_keyboard'].append([
            {'text': '🔄 Обновить', 'callback_data': 'settings_pairs'},
            {'text': '🔙 Назад к настройкам', 'callback_data': 'settings'}
        ])

        return message, inline_keyboard
    
    def send_delete_pairs_menu(self):
        """Меню удаления торговых пар"""
        current_pair = self.bot.settings.trading_pairs['active_pair']
        available_pairs = self.bot.settings.trading_pairs['available_pairs']
        
        # Фильтруем пары, которые можно удалить (не активная и не последняя)
        deletable_pairs = {
            pair_id: pair_name 
            for pair_id, pair_name in available_pairs.items()
            if pair_id != current_pair and len(available_pairs) > 1
        }
        
        if not deletable_pairs:
            message = """
🗑️ <b>УДАЛЕНИЕ ТОРГОВЫХ ПАР</b>

⚠️ <b>Нет доступных пар для удаления</b>

💡 <b>Примечание:</b>
• Нельзя удалить активную торговую пару
• Нельзя удалить последнюю торговую пару
"""
            inline_keyboard = {
                'inline_keyboard': [
                    [
                        {'text': '🔙 Назад к парам', 'callback_data': 'settings_pairs'}
                    ]
                ]
            }
            return message, inline_keyboard
        
        # Формируем список пар для удаления
        pairs_list = []
        for pair_id, pair_name in deletable_pairs.items():
            pairs_list.append(f"• {pair_name} ({pair_id})")
        
        pairs_text = "\n".join(pairs_list)
        
        message = f"""
🗑️ <b>УДАЛЕНИЕ ТОРГОВЫХ ПАР</b>

💡 <b>Выберите пару для удаления:</b>
{pairs_text}

⚠️ <b>Внимание:</b> Удаление пары нельзя отменить.
"""
        
        # Формируем кнопки для удаляемых пар (каждая пара в отдельной строке)
        inline_keyboard = {'inline_keyboard': []}
        pairs_items = list(deletable_pairs.items())
        
        # Добавляем каждую кнопку пары для удаления в отдельную строку
        for pair_id, pair_name in pairs_items:
            inline_keyboard['inline_keyboard'].append([{
                'text': f"🗑️ {pair_name}",
                'callback_data': f'pair_delete_{pair_id}'
            }])
        
        # Добавляем кнопку назад
        inline_keyboard['inline_keyboard'].append([
            {'text': '🔙 Назад к парам', 'callback_data': 'settings_pairs'}
        ])

        return message, inline_keyboard

    def send_ml_settings_menu(self):
        """Меню настроек Machine Learning"""
        ml_enabled = self.bot.settings.ml_settings['enabled']
        buy_threshold = self.bot.settings.ml_settings['confidence_threshold_buy']
        sell_threshold = self.bot.settings.ml_settings['confidence_threshold_sell']

        message = f"""
🤖 <b>НАСТРОЙКИ MACHINE LEARNING</b>

🎯 <b>Текущие настройки:</b>
• ML: {'✅ ВКЛЮЧЕН' if ml_enabled else '❌ ВЫКЛЮЧЕН'}
• Порог покупки: {buy_threshold:.1f}
• Порог продажи: {sell_threshold:.1f}

💡 <b>Настройки ML модели:</b>
• Порог покупки - минимальная уверенность ML для сигнала покупки
• Порог продажи - минимальная уверенность ML для сигнала продажи
• Чем выше значения, тем строже фильтрация сигналов

Выберите параметр для настройки:
"""

        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': f'🤖 ML: {"✅ ВКЛ" if ml_enabled else "❌ ВЫКЛ"}', 'callback_data': 'ml_toggle'},
                    {'text': '🔄 Переобучить', 'callback_data': 'ml_retrain'}
                ],
                [
                    {'text': f'🎯 Покупка: {buy_threshold:.1f}', 'callback_data': 'ml_buy_threshold'},
                    {'text': f'🎯 Продажа: {sell_threshold:.1f}', 'callback_data': 'ml_sell_threshold'}
                ],
                [
                    {'text': '🔙 Назад', 'callback_data': 'settings'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_trading_control_menu(self):
        """Меню управления торговлей"""
        trading_enabled = self.bot.settings.settings['trading_enabled']
        trade_signals = self.bot.settings.settings['enable_trade_signals']
        demo_mode = self.bot.settings.settings['demo_mode']

        message = f"""
⚡ <b>УПРАВЛЕНИЕ ТОРГОВЛЕЙ</b>

🎯 <b>Текущий статус:</b>
• Торговля: {'✅ ВКЛЮЧЕНА' if trading_enabled else '❌ ОСТАНОВЛЕНА'}
• Сигналы: {'✅ ВКЛЮЧЕНЫ' if trade_signals else '❌ ВЫКЛЮЧЕНЫ'}
• Режим: {'🟢 ДЕМО-РЕЖИМ' if demo_mode else '🔴 РЕАЛЬНАЯ ТОРГОВЛЯ'}

⚠️ <b>Внимание:</b>
• В демо-режиме сделки не исполняются на бирже
• В реальном режиме будьте осторожны - бот торгует реальными деньгами

Выберите действие:
"""

        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': f'📊 Торговля: {"✅" if trading_enabled else "❌"}', 'callback_data': 'control_toggle_trading'},
                    {'text': f'🎯 Сигналы: {"✅" if trade_signals else "❌"}', 'callback_data': 'control_toggle_signals'}
                ],
                [
                    {'text': f'🔧 Режим: {"🟢 ДЕМО" if demo_mode else "🔴"}', 'callback_data': 'control_toggle_demo'},
                    {'text': '🧪 Торговля в демо-режиме', 'callback_data': 'control_demo_trade'}
                ],
                [
                    {'text': '🔄 Перезагрузить', 'callback_data': 'control_restart'},
                    {'text': '🚨 Экстренная остановка', 'callback_data': 'control_emergency'}
                ],
                [
                    {'text': '🏠 Главное меню', 'callback_data': 'main_menu'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_risk_settings_menu(self):
        """Меню настроек рисков"""
        max_position = self.bot.settings.risk_settings.get('max_position_size', 25.0)
        max_daily_loss = self.bot.settings.risk_settings.get('max_daily_loss', 3.0)
        max_consecutive = self.bot.settings.risk_settings.get('max_consecutive_losses', 3)

        message = f"""
⚡ <b>НАСТРОЙКИ РИСК-МЕНЕДЖМЕНТА</b>

🎯 <b>Текущие лимиты:</b>
• Макс. размер позиции: {max_position:.1f}%
• Макс. убыток в день: {max_daily_loss:.1f}%
• Макс. убыточных подряд: {max_consecutive}

💡 <b>Рекомендации:</b>
• Макс. позиция: 5-25% от баланса
• Макс. убыток: 2-5% в день
• Убыточные: 3-5 сделок подряд

📌 <b>Примечание:</b> Stop Loss настраивается в настройках стратегии (EMA)

Выберите параметр для настройки:
"""

        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': f'💼 Позиция: {max_position:.1f}%', 'callback_data': 'risk_max_position'},
                    {'text': f'📉 Убыток/день: {max_daily_loss:.1f}%', 'callback_data': 'risk_max_loss'}
                ],
                [
                    {'text': f'🔴 Убыточных: {max_consecutive}', 'callback_data': 'risk_max_consecutive'}
                ],
                [
                    {'text': '🔙 Назад', 'callback_data': 'settings'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_analytics_menu(self):
        """Меню аналитики"""
        message = f"""
📊 <b>АНАЛИТИКА И ОТЧЕТЫ</b>

📈 <b>Общая статистика:</b>
• Всего сделок: {self.bot.metrics.total_trades}
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыль: {self.bot.metrics.total_profit:.2f}% ({self.bot.metrics.total_profit_usdt:.2f} USDT)
• Profit Factor: {self.bot.metrics.profit_factor:.2f}
• Макс. просадка: {self.bot.metrics.max_drawdown:.2f}%

💡 <b>Доступные отчеты:</b>
• Детальный отчет - полная статистика торговли
• Графики - визуализация данных (в разработке)
• Очистка статистики - сброс всех метрик

Выберите действие:
"""

        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': '📈 Детальный отчет', 'callback_data': 'analytics_detailed'},
                    {'text': '📊 Графики', 'callback_data': 'analytics_charts'}
                ],
                [
                    {'text': '🧹 Очистить статистику', 'callback_data': 'analytics_clear'}
                ],
                [
                    {'text': '🔄 Обновить', 'callback_data': 'analytics'},
                    {'text': '🏠 Главное меню', 'callback_data': 'main_menu'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_trade_history(self):
        """История сделок"""
        if not self.bot.metrics.trade_history:
            message = "📊 <b>ИСТОРИЯ СДЕЛОК</b>\n\nИстория сделок пуста."
        else:
            recent_trades = self.bot.metrics.trade_history[-10:]  # Последние 10 сделок
            trade_list = []
            
            for trade in recent_trades:
                emoji = "🟢" if trade['profit'] > 0 else "🔴"
                profit_str = f"+{trade['profit']:.2f}%" if trade['profit'] > 0 else f"{trade['profit']:.2f}%"
                time_str = trade['timestamp'].strftime("%H:%M") if hasattr(trade['timestamp'], 'strftime') else "N/A"
                
                trade_list.append(
                    f"{emoji} {time_str} {trade['signal'].upper()} {trade['symbol']} - {profit_str}"
                )
            
            trade_history_text = "\n".join(trade_list)
            
            message = f"""
📊 <b>ИСТОРИЯ СДЕЛОК</b>

🕐 <b>Последние 10 сделок:</b>
{trade_history_text}

📈 <b>Общая статистика:</b>
• Всего сделок: {self.bot.metrics.total_trades}
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыль: {self.bot.metrics.total_profit:.2f}% ({self.bot.metrics.total_profit_usdt:.2f} USDT)
"""
        
        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': '🔄 Обновить', 'callback_data': 'trades'},
                    {'text': '🏠 Главное меню', 'callback_data': 'main_menu'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_account_info(self):
        """Информация об аккаунте"""
        balance = self.bot.exchange.get_balance()
        if not balance:
            message = "❌ Не удалось получить информацию о балансе"
        else:
            # Получаем информацию о Take Profit
            tp_info = self.bot.get_take_profit_info()
            if tp_info['mode'] == 'USDT':
                tp_display = f"{self.smart_format(tp_info['take_profit_usdt'], 4)} USDT"
            else:
                tp_display = f"{self.smart_format(tp_info['take_profit_percent'], 4)}%"

            message = f"""
💼 <b>ИНФОРМАЦИЯ ОБ АККАУНТЕ</b>

💰 <b>Баланс:</b>
• USDT: {balance['total_usdt']:.2f}
  ├ Свободно: {balance['free_usdt']:.2f}
  └ Занято: {balance['used_usdt']:.2f}
  
• BTC: {balance['total_btc']:.6f}
  ├ Свободно: {balance['free_btc']:.6f}
  └ Занято: {balance.get('used_btc', 0):.6f}

🎯 <b>Торговые настройки:</b>
• Размер ставки: {self.bot.settings.settings['trade_amount_percent'] * 100:.1f}%
• Take Profit: {tp_display}
• Следующая ставка: {balance['free_usdt'] * self.bot.settings.settings['trade_amount_percent']:.2f} USDT

📊 <b>Статистика:</b>
• Сделок: {self.bot.metrics.total_trades}
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыль: {self.bot.metrics.total_profit:.2f}% ({self.bot.metrics.total_profit_usdt:.2f} USDT)
"""
        
        inline_keyboard = {
            'inline_keyboard': [
                [
                    {'text': '🔄 Обновить', 'callback_data': 'account_info'},
                    {'text': '🏠 Главное меню', 'callback_data': 'main_menu'}
                ]
            ]
        }

        return message, inline_keyboard

    def send_main_menu_inline(self):
        """Главное меню с inline-кнопками"""
        market_data = self.bot.exchange.get_market_data(
            self.bot.settings.trading_pairs['active_pair']
        )
        
        current_price = market_data['current_price'] if market_data else 0
        position_status = "🟢 ОТКРЫТА" if self.bot.position == 'long' else "⚪ ОЖИДАНИЕ"
        
        tp_info = self.bot.get_take_profit_info()
        if tp_info['mode'] == 'USDT':
            tp_display = f"{self.smart_format(tp_info['take_profit_usdt'], 4)} USDT"
        else:
            tp_display = f"{self.smart_format(tp_info['take_profit_percent'], 4)}%"

        message = f"""
🤖 <b>ГЛАВНОЕ МЕНЮ ТОРГОВОГО БОТА</b>

💱 <b>Текущая пара:</b> {self.bot.settings.get_active_pair_name()}
💰 <b>Цена:</b> {current_price:.2f} USDT
🎯 <b>Стратегия:</b> {self.bot.settings.get_active_strategy_name()}
💼 <b>Позиция:</b> {position_status}
🎯 <b>Take Profit:</b> {tp_display}

📊 <b>Статистика:</b>
• Сделок: {self.bot.metrics.total_trades}
• Win Rate: {self.bot.metrics.win_rate:.1f}%
• Прибыль: {self.bot.metrics.total_profit:.2f}% ({self.bot.metrics.total_profit_usdt:.2f} USDT)

💡 <b>Выберите действие:</b>
"""

        # Получаем WEBAPP_URL из переменной окружения
        webapp_url = os.getenv('WEBAPP_URL', '')
        
        # Формируем inline-клавиатуру
        keyboard_rows = [
            [
                {'text': '📊 Статус', 'callback_data': 'status'},
                {'text': '💼 Аккаунт', 'callback_data': 'account_info'}
            ],
            [
                {'text': '📈 Сделки', 'callback_data': 'trades'},
                {'text': '📊 Аналитика', 'callback_data': 'analytics'}
            ],
            [
                {'text': '⚙️ Настройки', 'callback_data': 'settings'},
                {'text': '⚡ Управление', 'callback_data': 'control'}
            ]
        ]
        
        # Добавляем кнопку WebApp только если URL настроен правильно
        last_row = [{'text': '🔄 Обновить', 'callback_data': 'refresh'}]
        
        if webapp_url and webapp_url != 'https://your-server.com' and webapp_url.startswith('https://'):
            last_row.append({'text': '🚀 Открыть Web App', 'web_app': {'url': webapp_url}})
        
        keyboard_rows.append(last_row)
        
        inline_keyboard = {
            'inline_keyboard': keyboard_rows
        }

        return message, inline_keyboard

    def create_cancel_keyboard(self):
        """Клавиатура для отмены ввода с кнопкой главного меню"""
        return {
            'keyboard': [
                ['❌ Отменить ввод', '🏠 Главное меню']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }