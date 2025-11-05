"""
БАЗОВЫЙ КЛАСС СТРАТЕГИИ С ПОДДЕРЖКОЙ ПОЗИЦИЙ
"""
import time
from abc import ABC, abstractmethod
from utils.logger import log_info

class BaseStrategy(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.settings = {}
        self.position = None  # 'long', 'short', или None
        self.entry_price = 0
        self.position_opened_at = None
        self.position_size_usdt = 0  # Размер позиции в USDT
        
    @abstractmethod
    def calculate_signal(self, market_data, ml_confidence=0.5, ml_signal="⚪ НЕЙТРАЛЬНО"):
        """Расчет торгового сигнала"""
        pass
    
    def set_settings(self, settings):
        """Установка настроек стратегии"""
        self.settings.update(settings)
        log_info(f"⚙️ Настройки стратегии {self.name} обновлены")
    
    def get_settings_info(self):
        """Получение информации о настройках"""
        return self.settings
    
    def validate_market_data(self, market_data):
        """Валидация рыночных данных"""
        if not market_data:
            return False, "Нет рыночных данных"
        
        required_fields = ['current_price', 'ema_diff_percent']
        for field in required_fields:
            if field not in market_data:
                return False, f"Отсутствует поле {field}"
        
        return True, "OK"
    
    def update_position_info(self, signal, price):
        """Обновление информации о позиции"""
        if signal == 'buy':
            # 🔧 КРИТИЧНО: Если позиция уже существует, берем МАКСИМАЛЬНУЮ цену
            # Это гарантирует, что при закрытии позиции будет прибыль относительно всех покупок
            if self.position == 'long' and self.entry_price > 0:
                self.entry_price = max(self.entry_price, price)
            else:
                self.entry_price = price
            self.position = 'long'
            self.position_opened_at = time.time()
        elif signal == 'sell':
            self.position = None
            self.entry_price = 0
            self.position_opened_at = None
    
    def get_position_info(self):
        """Получение информации о текущей позиции"""
        if self.position:
            return {
                'position': self.position,
                'entry_price': self.entry_price,
                'opened_at': self.position_opened_at,
                'hold_time': time.time() - self.position_opened_at if self.position_opened_at else 0
            }
        return None
    
    def prepare_signal_message(self, signal, market_data, ml_confidence, ml_signal):
        """Подготовка сообщения о сигнале"""
        if signal == 'buy':
            emoji = "🟢"
            action = "ПОКУПКА"
        elif signal == 'sell':
            emoji = "🔴" 
            action = "ПРОДАЖА"
        else:
            emoji = "⚪"
            action = "ОЖИДАНИЕ"
        
        # Добавляем информацию о позиции
        position_info = ""
        if self.position:
            current_price = market_data['current_price']
            profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
            position_info = f"\n💼 Текущая позиция: {self.position.upper()}\n📈 Прибыль: {profit_percent:+.2f}%"
        
        message = f"""
{emoji} <b>СИГНАЛ {action}</b>

🎯 <b>Стратегия:</b> {self.name}
💰 <b>Цена:</b> {market_data['current_price']:.2f} USDT
📈 <b>EMA:</b> {market_data['ema_diff_percent']*100:+.2f}%
🤖 <b>ML:</b> {ml_signal} ({ml_confidence:.1%})
{position_info}

💡 {self.description}
"""
        return message
