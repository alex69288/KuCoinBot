"""
УПРАВЛЕНИЕ НАСТРОЙКАМИ
"""
import json
import os
from dotenv import load_dotenv
from .constants import DEFAULT_SETTINGS, DEFAULT_ML_SETTINGS, DEFAULT_RISK_SETTINGS, STRATEGIES, TRADING_PAIRS

# Загружаем переменные окружения
load_dotenv()

class SettingsManager:
    def __init__(self):
        self.settings_file = 'bot_settings.json'
        self.settings = DEFAULT_SETTINGS.copy()
        self.strategy_settings = {
            'active_strategy': 'ema_ml',
            'available_strategies': STRATEGIES
        }
        self.trading_pairs = {
            'active_pair': 'BTC/USDT',
            'available_pairs': TRADING_PAIRS
        }
        self.ml_settings = DEFAULT_ML_SETTINGS.copy()
        self.risk_settings = DEFAULT_RISK_SETTINGS.copy()
        
        # Добавляем Telegram настройки из .env
        self.settings['telegram_token'] = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.settings['telegram_chat_id'] = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Добавляем поля для сохранения настроек стратегий
        self.ml_settings['last_take_profit_usdt'] = 0.0
        self.ml_settings['last_take_profit_percent'] = 2.0
        self.ml_settings['last_stop_loss_percent'] = 1.5  # 🔧 Сохраняем Stop Loss
        # EMA настройки
        self.ml_settings['last_ema_fast_period'] = 9
        self.ml_settings['last_ema_slow_period'] = 21
        self.ml_settings['last_ema_threshold'] = 0.0025  # 0.25%
        
        self.bot = None  # Ссылка на бота для доступа к стратегиям
        self.load_settings()

    def set_bot_reference(self, bot):
        """Устанавливает ссылку на бота для доступа к стратегиям"""
        self.bot = bot
        # 🔧 НЕ загружаем настройки стратегий здесь, так как стратегии еще не созданы
        # Загрузка будет вызвана после создания стратегий в bot.__init__()

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Проверка на пустой файл
                    if not content:
                        print("⚠️ Файл настроек пуст, использую значения по умолчанию")
                        self.save_settings()
                        return
                    
                    saved_settings = json.loads(content)
                    
                    # Обновляем настройки
                    self.settings.update(saved_settings.get('settings', {}))
                    self.strategy_settings.update(saved_settings.get('strategy_settings', self.strategy_settings))
                    self.trading_pairs.update(saved_settings.get('trading_pairs', self.trading_pairs))
                    self.ml_settings.update(saved_settings.get('ml_settings', self.ml_settings))
                    self.risk_settings.update(saved_settings.get('risk_settings', self.risk_settings))
                    
                print("✅ Настройки загружены")
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка формата JSON в файле настроек: {e}")
            print("⚠️ Создаю новый файл с настройками по умолчанию")
            self.save_settings()
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек: {e}")
            print("⚠️ Использую настройки по умолчанию")

    def load_strategy_settings(self):
        """Загрузка настроек для активной стратегии"""
        try:
            # 🔧 ПРОВЕРКА: убеждаемся, что бот и стратегии инициализированы
            if not self.bot:
                return
            if not hasattr(self.bot, 'strategies') or not self.bot.strategies:
                return
            
            strategy = self.bot.get_active_strategy()
            if strategy:
                # Восстанавливаем настройки Take Profit из сохраненных
                last_tp_usdt = self.ml_settings.get('last_take_profit_usdt')
                last_tp_percent = self.ml_settings.get('last_take_profit_percent')
                last_sl_percent = self.ml_settings.get('last_stop_loss_percent', 1.5)  # 🔧 Загружаем Stop Loss
                
                # Загружаем EMA настройки
                last_ema_fast = self.ml_settings.get('last_ema_fast_period', 9)
                last_ema_slow = self.ml_settings.get('last_ema_slow_period', 21)
                last_ema_threshold = self.ml_settings.get('last_ema_threshold', 0.0025)
                
                if last_tp_usdt is not None:
                    strategy.settings['take_profit_usdt'] = last_tp_usdt
                if last_tp_percent is not None:
                    strategy.settings['take_profit_percent'] = last_tp_percent
                if last_sl_percent is not None:  # 🔧 Загружаем Stop Loss
                    strategy.settings['stop_loss_percent'] = last_sl_percent
                
                # Загружаем EMA настройки
                if last_ema_fast is not None:
                    strategy.settings['ema_fast_period'] = last_ema_fast
                if last_ema_slow is not None:
                    strategy.settings['ema_slow_period'] = last_ema_slow
                if last_ema_threshold is not None:
                    strategy.settings['ema_threshold'] = last_ema_threshold
                
                print(f"✅ Настройки стратегии загружены: TP_USDT={last_tp_usdt}, TP_%={last_tp_percent}, SL_%={last_sl_percent}, EMA={last_ema_fast}/{last_ema_slow}, Threshold={last_ema_threshold*100:.2f}%")
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек стратегии: {e}")

    def save_settings(self, sync_from_strategy=True):
        """Сохранение настроек в файл
        sync_from_strategy: если True, синхронизирует ml_settings из стратегии перед сохранением
        """
        try:
            # Сохраняем настройки активной стратегии (только если sync_from_strategy=True)
            if sync_from_strategy and self.bot:
                strategy = self.bot.get_active_strategy()
                if strategy:
                    # Сохраняем настройки Take Profit и Stop Loss стратегии
                    self.ml_settings['last_take_profit_usdt'] = strategy.settings.get('take_profit_usdt', 0.0)
                    self.ml_settings['last_take_profit_percent'] = strategy.settings.get('take_profit_percent', 2.0)
                    self.ml_settings['last_stop_loss_percent'] = strategy.settings.get('stop_loss_percent', 1.5)  # 🔧 Сохраняем Stop Loss
                    # Сохраняем EMA настройки
                    self.ml_settings['last_ema_fast_period'] = strategy.settings.get('ema_fast_period', 9)
                    self.ml_settings['last_ema_slow_period'] = strategy.settings.get('ema_slow_period', 21)
                    self.ml_settings['last_ema_threshold'] = strategy.settings.get('ema_threshold', 0.0025)
            
            settings_to_save = {
                'settings': self.settings,
                'strategy_settings': self.strategy_settings,
                'trading_pairs': self.trading_pairs,
                'ml_settings': self.ml_settings,
                'risk_settings': self.risk_settings
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=2, ensure_ascii=False)
                
            print("✅ Настройки сохранены")
        except Exception as e:
            print(f"❌ Ошибка сохранения настроек: {e}")

    def update_setting(self, category, key, value):
        """Обновление конкретной настройки"""
        try:
            if category == 'main':
                self.settings[key] = value
            elif category == 'strategy':
                self.strategy_settings[key] = value
            elif category == 'trading_pairs':
                self.trading_pairs[key] = value
            elif category == 'ml':
                self.ml_settings[key] = value
            elif category == 'risk':
                self.risk_settings[key] = value
            
            self.save_settings()
            return True
        except Exception as e:
            print(f"❌ Ошибка обновления настройки: {e}")
            return False

    def get_active_strategy_name(self):
        """Получение названия активной стратегии"""
        return self.strategy_settings['available_strategies'].get(
            self.strategy_settings['active_strategy'],
            'Неизвестная стратегия'
        )

    def get_active_pair_name(self):
        """Получение названия активной пары"""
        return self.trading_pairs['available_pairs'].get(
            self.trading_pairs['active_pair'],
            'Неизвестная пара'
        )
    
    def is_telegram_configured(self):
        """Проверка настройки Telegram"""
        return bool(self.settings.get('telegram_token') and self.settings.get('telegram_chat_id'))

    def get_take_profit_info(self):
        """Получение информации о текущих настройках Take Profit"""
        if self.bot:
            strategy = self.bot.get_active_strategy()
            if strategy:
                take_profit_usdt = strategy.settings.get('take_profit_usdt', 0.0)
                take_profit_percent = strategy.settings.get('take_profit_percent', 2.0)
                
                return {
                    'take_profit_usdt': take_profit_usdt,
                    'take_profit_percent': take_profit_percent,
                    'mode': 'USDT' if take_profit_usdt > 0 else 'percent'
                }
        return {
            'take_profit_usdt': 0.0,
            'take_profit_percent': 2.0,
            'mode': 'percent'
        }

    def save_strategy_settings(self):
        """Сохранение настроек текущей стратегии"""
        try:
            if self.bot:
                strategy = self.bot.get_active_strategy()
                if strategy:
                    # Сохраняем настройки Take Profit и Stop Loss
                    self.ml_settings['last_take_profit_usdt'] = strategy.settings.get('take_profit_usdt', 0.0)
                    self.ml_settings['last_take_profit_percent'] = strategy.settings.get('take_profit_percent', 2.0)
                    self.ml_settings['last_stop_loss_percent'] = strategy.settings.get('stop_loss_percent', 1.5)  # 🔧 Сохраняем Stop Loss
                    # Сохраняем EMA настройки
                    self.ml_settings['last_ema_fast_period'] = strategy.settings.get('ema_fast_period', 9)
                    self.ml_settings['last_ema_slow_period'] = strategy.settings.get('ema_slow_period', 21)
                    self.ml_settings['last_ema_threshold'] = strategy.settings.get('ema_threshold', 0.0025)
                    
                    # Сохраняем другие настройки стратегии если нужно
                    self.save_settings()
                    print("✅ Настройки стратегии сохранены")
        except Exception as e:
            print(f"❌ Ошибка сохранения настроек стратегии: {e}")

    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        try:
            self.settings = DEFAULT_SETTINGS.copy()
            self.ml_settings = DEFAULT_ML_SETTINGS.copy()
            self.risk_settings = DEFAULT_RISK_SETTINGS.copy()
            
            # Сохраняем Telegram настройки
            self.settings['telegram_token'] = os.getenv('TELEGRAM_BOT_TOKEN', '')
            self.settings['telegram_chat_id'] = os.getenv('TELEGRAM_CHAT_ID', '')
            
            # Сбрасываем настройки стратегий
            self.ml_settings['last_take_profit_usdt'] = 0.0
            self.ml_settings['last_take_profit_percent'] = 2.0
            self.ml_settings['last_stop_loss_percent'] = 1.5  # 🔧 Сбрасываем Stop Loss
            
            self.save_settings()
            print("✅ Настройки сброшены к значениям по умолчанию")
            
            # Обновляем настройки в активной стратегии
            if self.bot:
                strategy = self.bot.get_active_strategy()
                if strategy:
                    strategy.settings['take_profit_usdt'] = 0.0
                    strategy.settings['take_profit_percent'] = 2.0
                    strategy.settings['stop_loss_percent'] = 1.5  # 🔧 Сбрасываем Stop Loss
            
            return True
        except Exception as e:
            print(f"❌ Ошибка сброса настроек: {e}")
            return False

    def get_settings_summary(self):
        """Получение сводки всех настроек"""
        tp_info = self.get_take_profit_info()
        
        summary = f"""
📊 <b>СВОДКА НАСТРОЕК</b>

🎯 <b>Торговля:</b>
• Пара: {self.get_active_pair_name()}
• Стратегия: {self.get_active_strategy_name()}
• Размер ставки: {self.settings.get('trade_amount_percent', 0.1) * 100:.1f}%
• Режим: {'🟢 ДЕМО' if self.settings.get('demo_mode', True) else '🔴 РЕАЛЬНЫЙ'}

📈 <b>Take Profit:</b>
• Режим: {tp_info['mode']}
• Значение: {tp_info['take_profit_usdt'] if tp_info['mode'] == 'USDT' else tp_info['take_profit_percent']} {tp_info['mode']}

⚡ <b>Риски:</b>
• Макс. позиция: {self.risk_settings.get('max_position_size', 25.0):.1f}%
• Макс. убыток/день: {self.risk_settings.get('max_daily_loss', 3.0):.1f}%
• Макс. убыточных: {self.risk_settings.get('max_consecutive_losses', 3)}

🤖 <b>ML:</b>
• Включен: {'✅ ДА' if self.ml_settings.get('enabled', True) else '❌ НЕТ'}
• Порог покупки: {self.ml_settings.get('confidence_threshold_buy', 0.4):.1f}
• Порог продажи: {self.ml_settings.get('confidence_threshold_sell', 0.3):.1f}
"""
        return summary