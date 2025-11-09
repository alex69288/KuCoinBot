"""
УПРАВЛЕНИЕ РИСКАМИ
"""
from utils.logger import log_info, log_error
from utils.helpers import calculate_volatility

class RiskManager:
    def __init__(self, risk_settings):
        self.risk_settings = risk_settings
        self.daily_losses = 0.0
        self.consecutive_losses = 0
        self.trades_today = 0
        
    def check_trade_risk(self, signal_type, current_price, position_size, market_data):
        """Проверка рисков перед сделкой"""
        checks = []
        
        # 1. Проверка дневного лимита потерь
        if self.daily_losses >= self.risk_settings['max_daily_loss']:
            checks.append((
                False, 
                f"🚨 Превышен дневной лимит потерь: {self.daily_losses:.2f}%"
            ))
        
        # 2. Проверка серии убытков
        if self.consecutive_losses >= self.risk_settings['max_consecutive_losses']:
            checks.append((
                False,
                f"🚨 {self.consecutive_losses} убыточных сделок подряд"
            ))
        
        # 3. Проверка размера позиции
        max_position = self.risk_settings['max_position_size']
        if position_size > max_position:
            checks.append((
                False,
                f"🚨 Превышен размер позиции: {position_size:.1f}% > {max_position:.1f}%"
            ))
        
        # 4. Проверка волатильности
        if market_data and 'ohlcv' in market_data:
            volatility = calculate_volatility([candle[4] for candle in market_data['ohlcv']])
            if volatility > self.risk_settings['volatility_limit']:
                checks.append((
                    False,
                    f"🚨 Высокая волатильность: {volatility:.1f}%"
                ))
        
        # 5. Проверка стоп-лосса и тейк-профита (теперь берем из стратегии)
        # 🔧 УДАЛЕНО: stop_loss и take_profit теперь только в настройках стратегии
        # Проверка соотношения риск/прибыль должна быть в стратегии
        
        # Если есть критические ошибки - возвращаем первую
        critical_errors = [check for check in checks if not check[0]]
        if critical_errors:
            return critical_errors[0]
        
        # Все проверки пройдены
        return True, "✅ Риски в пределах нормы"
    
    def update_after_trade(self, trade_result):
        """Обновление статистики после сделки"""
        profit_percent = trade_result.get('profit_percent', 0)
        
        if profit_percent < 0:
            self.daily_losses += abs(profit_percent)
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        self.trades_today += 1
        
        log_info(f"📊 Статистика рисков: убытки {self.daily_losses:.2f}%, "
                f"серия убытков {self.consecutive_losses}, "
                f"сделок сегодня {self.trades_today}")
    
    def reset_daily_stats(self):
        """Сброс дневной статистики"""
        self.daily_losses = 0.0
        self.trades_today = 0
        log_info("🔄 Дневная статистика рисков сброшена")
    
    def get_risk_summary(self):
        """Получение сводки по рискам"""
        return {
            'daily_losses': self.daily_losses,
            'consecutive_losses': self.consecutive_losses,
            'trades_today': self.trades_today,
            'max_daily_loss': self.risk_settings['max_daily_loss'],
            'max_consecutive_losses': self.risk_settings['max_consecutive_losses']
        }
    
    def can_trade(self):
        """Проверка возможности торговли"""
        return (self.daily_losses < self.risk_settings['max_daily_loss'] and 
                self.consecutive_losses < self.risk_settings['max_consecutive_losses'])