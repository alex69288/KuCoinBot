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
        
        self.load_settings()

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    
                    # Обновляем настройки
                    self.settings.update(saved_settings.get('settings', {}))
                    self.strategy_settings.update(saved_settings.get('strategy_settings', self.strategy_settings))
                    self.trading_pairs.update(saved_settings.get('trading_pairs', self.trading_pairs))
                    self.ml_settings.update(saved_settings.get('ml_settings', {}))
                    self.risk_settings.update(saved_settings.get('risk_settings', {}))
                    
                print("✅ Настройки загружены")
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек: {e}")

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
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