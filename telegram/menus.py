"""
МЕНЮ TELEGRAM БОТА
"""
from utils.helpers import format_price, format_percent

class MenuManager:
    def __init__(self, trading_bot):
        self.bot = trading_bot

    def create_keyboard(self, buttons, one_time=False):
        """Создание клавиатуры"""
        return {
            'keyboard': buttons,
            'resize_keyboard': True,
            'one_time_keyboard': one_time
        }

    def create_inline_keyboard(self, buttons):
        """Создание инлайн-клавиатуры"""
        return {
            'inline_keyboard': buttons
        }

    def create_cancel_keyboard(self):
        """Клавиатура для отмены ввода"""
        return self.create_keyboard([['❌ Отменить ввод']], one_time=True)

    def send_main_menu(self):
        """Главное меню"""
        settings = self.bot.settings
        current_pair = settings.get_active_pair_name()
        strategy_name = settings.get_active_strategy_name()
        trading_status = "✅" if settings.settings['trading_enabled'] else "❌"
        ml_status = "✅" if settings.ml_settings['enabled'] else "❌"
        keyboard = [
            ['📊 Статус', '💼 Инфо аккаунта'],
            ['📊 Аналитика', '📈 Сделки'],
            ['⚙️ Настройки', '⚡ Управление'],
            ['🔄 Обновить', '🚨 Экстренная остановка']
        ]
        message = f"""
🤖 <b>РАСШИРЕННЫЙ ТОРГОВЫЙ БОТ v4.0</b>

💱 <b>Пара:</b> {current_pair}
🎯 <b>Стратегия:</b> {strategy_name}
{trading_status} <b>Торговля:</b> {'ВКЛ' if settings.settings['trading_enabled'] else 'ВЫКЛ'}
{ml_status} <b>ML:</b> {'ВКЛ' if settings.ml_settings['enabled'] else 'ВЫКЛ'}

🚀 <b>ВОЗМОЖНОСТИ:</b>
• 🎯 5 торговых стратегий
• 💱 Смена пар в 1 клик  
• 🤖 Гибкие настройки ML
• ⚡ Централизованное управление

💡 <b>Команды:</b>
• ⚙️ Настройки - все параметры бота
• ⚡ Управление - контроль торговли
• 📊 Аналитика - статистика эффективности
"""
        return message, self.create_keyboard(keyboard)

    def send_settings_menu(self):
        """Меню настроек"""
        settings = self.bot.settings
        current_pair = settings.get_active_pair_name()
        current_threshold = settings.settings['ema_cross_threshold'] * 100
        keyboard = [
            [f"📈 EMA порог: {current_threshold:.2f}%"],
            [f"💰 Размер позиции: {settings.settings['trade_amount_percent']*100:.1f}%"],
            [f"🎯 Стратегия: {settings.get_active_strategy_name()}"],
            [f"💱 Пара: {current_pair}"],
            ["🤖 ML Настройки"],
            ["⚙️ Настройки EMA"],
            [f"🔄 Обновления: {'✅' if settings.settings['enable_price_updates'] else '❌'}"],
            ['🏠 Главное меню']
        ]
        message = f"""
⚙️ <b>НАСТРОЙКИ БОТА</b>

📈 <b>Стратегия EMA:</b>
• Порог срабатывания: <b>{current_threshold:.2f}%</b>
• Размер позиции: <b>{settings.settings['trade_amount_percent']*100:.1f}%</b>

🎯 <b>Активная стратегия:</b> <b>{settings.get_active_strategy_name()}</b>

💱 <b>Торговая пара:</b> <b>{current_pair}</b>

🤖 <b>Machine Learning:</b> {'✅ ВКЛЮЧЕН' if settings.ml_settings['enabled'] else '❌ ВЫКЛЮЧЕН'}

💡 Нажмите на параметр для изменения
"""
        return message, self.create_keyboard(keyboard)

    def send_ema_settings_menu(self):
        """Меню настроек EMA стратегии"""
        settings = self.bot.settings
        strategy = self.bot.get_active_strategy()
        if hasattr(strategy, 'settings'):
            ema_settings = strategy.settings
        else:
            ema_settings = {}
        take_profit = ema_settings.get('take_profit_percent', 2.0)
        stop_loss = ema_settings.get('stop_loss_percent', 1.5)
        trailing_stop = ema_settings.get('trailing_stop', False)
        min_hold_time = ema_settings.get('min_hold_time', 300) // 60
        keyboard = [
            [f"🎯 Take Profit: {take_profit:.1f}%"],
            [f"🛑 Stop Loss: {stop_loss:.1f}%"],
            [f"📉 Trailing Stop: {'✅ ВКЛ' if trailing_stop else '❌ ВЫКЛ'}"],
            [f"⏰ Min Hold Time: {min_hold_time} мин"],
            ['🔙 Назад к настройкам']
        ]
        message = f"""
⚙️ <b>НАСТРОЙКИ EMA СТРАТЕГИИ</b>

🎯 <b>Условия закрытия:</b>
• Take Profit: <b>{take_profit:.1f}%</b>
• Stop Loss: <b>{stop_loss:.1f}%</b>
• Trailing Stop: {'✅ ВКЛ' if trailing_stop else '❌ ВЫКЛ'}
• Min Hold Time: <b>{min_hold_time} мин</b>

💡 <b>Объяснение:</b>
• Take Profit - фиксация прибыли
• Stop Loss - ограничение убытков  
• Trailing Stop - защита прибыли
• Min Hold Time - минимальное время удержания
"""
        return message, self.create_keyboard(keyboard)

    def send_strategy_menu(self):
        """Меню выбора стратегии"""
        settings = self.bot.settings
        keyboard = []
        for strategy_id, strategy_name in settings.strategy_settings['available_strategies'].items():
            prefix = "✅" if strategy_id == settings.strategy_settings['active_strategy'] else "⚪"
            keyboard.append([f"{prefix} {strategy_name}"])
        keyboard.append(['🔙 Назад к настройкам'])
        message = f"""
🎯 <b>ВЫБОР ТОРГОВОЙ СТРАТЕГИИ</b>

💡 Активная стратегия:
<b>{settings.get_active_strategy_name()}</b>

📊 Доступные стратегии:
• 📈 EMA + ML - Основная стратегия с AI
• ⚡ Price Action - По движению цены
• 🎯 MACD + RSI - Комбо индикаторы
• 📊 Bollinger Bands - Торговля в каналах
• 🔄 Гибридная - Комбинация стратегий
"""
        return message, self.create_keyboard(keyboard)

    def send_pairs_menu(self):
        """Меню выбора торговой пары"""
        settings = self.bot.settings
        keyboard = []
        pairs_list = list(settings.trading_pairs['available_pairs'].items())
        for i in range(0, len(pairs_list), 2):
            row = []
            for j in range(2):
                if i + j < len(pairs_list):
                    pair_id, pair_name = pairs_list[i + j]
                    prefix = "✅" if pair_id == settings.trading_pairs['active_pair'] else "⚪"
                    row.append(f"{prefix} {pair_name}")
            keyboard.append(row)
        keyboard.append(['🔙 Назад к настройкам'])
        current_pair = settings.trading_pairs['active_pair']
        current_name = settings.get_active_pair_name()
        message = f"""
💱 <b>ВЫБОР ТОРГОВОЙ ПАРЫ</b>

💰 Активная пара:
<b>{current_pair} - {current_name}</b>

💡 Выберите торговую пару для мониторинга и торговли.
"""
        return message, self.create_keyboard(keyboard)

    def send_ml_settings_menu(self):
        """Меню настроек ML"""
        settings = self.bot.settings
        ml_status = "✅ ВКЛЮЧЕН" if settings.ml_settings['enabled'] else "❌ ВЫКЛЮЧЕН"
        keyboard = [
            [f"🤖 ML: {ml_status}"],
            [f"🎯 Порог покупки: {settings.ml_settings['confidence_threshold_buy']:.1f}"],
            [f"🎯 Порог продажи: {settings.ml_settings['confidence_threshold_sell']:.1f}"],
            ["🔄 Переобучить модель"],
            ['🔙 Назад к настройкам']
        ]
        message = f"""
🤖 <b>НАСТРОЙКИ MACHINE LEARNING</b>

📊 <b>Текущий статус:</b> <b>{ml_status}</b>

🎯 <b>Пороги уверенности:</b>
• Покупка: > <b>{settings.ml_settings['confidence_threshold_buy']:.1f}</b>
• Продажа: < <b>{settings.ml_settings['confidence_threshold_sell']:.1f}</b>

💡 Объяснение:
ML модель фильтрует сигналы стратегии. Чем выше порог, тем строже фильтрация.
"""
        return message, self.create_keyboard(keyboard)

    def send_trading_control_menu(self):
        """Меню управления торговлей"""
        settings = self.bot.settings
        trading_status = "✅ ВКЛЮЧЕНА" if settings.settings['trading_enabled'] else "❌ ОСТАНОВЛЕНА"
        signals_status = "✅ ВКЛЮЧЕНЫ" if settings.settings['enable_trade_signals'] else "❌ ВЫКЛЮЧЕНЫ"
        demo_status = "🟢 ДЕМО" if settings.settings['demo_mode'] else "🔴 РЕАЛЬНЫЙ"
        keyboard = [
            [f"📊 Торговля: {trading_status}"],
            [f"🎯 Сигналы: {signals_status}"],
            [f"🔧 Режим: {demo_status}"],
            ["🔄 Перезагрузить бот", "🛑 Экстренная остановка"],
            ['🏠 Главное меню']
        ]
        message = f"""
⚡ <b>УПРАВЛЕНИЕ ТОРГОВЛЕЙ</b>

📊 <b>Статус торговли:</b> <b>{trading_status}</b>
🎯 <b>Торговые сигналы:</b> <b>{signals_status}</b>
🔧 <b>Режим работы:</b> <b>{demo_status}</b>

💡 Возможности:
• Включить/выключить автоматическую торговлю
• Остановить все операции
• Переключить демо/режим
• Перезагрузить бота
"""
        return message, self.create_keyboard(keyboard)

    def send_analytics_menu(self):
        """Меню аналитики"""
        metrics = self.bot.metrics.get_summary()
        message = f"""
📊 <b>ДЕТАЛЬНАЯ АНАЛИТИКА</b>

📈 <b>ОСНОВНЫЕ МЕТРИКИ:</b>
• Всего сделок: <b>{metrics['total_trades']}</b>
• Win Rate: <b>{metrics['win_rate']:.1f}%</b>
• Profit Factor: <b>{metrics['profit_factor']:.2f}</b>
• Общая прибыль: <b>{metrics['total_profit']:.2f} USDT</b>

💰 <b>СТАТИСТИКА СДЕЛОК:</b>
• Прибыльных: <b>{metrics['winning_trades']}</b>
• Убыточных: <b>{metrics['losing_trades']}</b>
• Средняя прибыль: <b>{metrics['average_win']:.2f} USDT</b>
• Средний убыток: <b>{metrics['average_loss']:.2f} USDT</b>

🎯 <b>РЕКОРДЫ:</b>
• Лучшая сделка: <b>{metrics['best_trade']:.2f} USDT</b>
• Худшая сделка: <b>{metrics['worst_trade']:.2f} USDT</b>
• Серия побед: <b>{metrics['consecutive_wins']}</b>
• Серия поражений: <b>{metrics['consecutive_losses']}</b>

⚡ <b>РИСКИ:</b>
• Макс просадка: <b>{metrics['max_drawdown']:.2f}%</b>
• Текущая просадка: <b>{metrics['current_drawdown']:.2f}%</b>
"""
        keyboard = [
            ['📈 Детальный отчет', '📊 Графики'],
            ['🧹 Очистить статистику', '🏠 Главное меню']
        ]
        return message, self.create_keyboard(keyboard)