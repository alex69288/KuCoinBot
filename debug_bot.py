"""
ДЕБАГ ЗАПУСКА БОТА
"""
import sys
import os
import time
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_bot():
    print("🔧 ДЕБАГ РЕЖИМ ЗАПУСКА БОТА")
    print("=" * 50)
    
    try:
        # Импортируем и создаем бота
        from core.bot import AdvancedTradingBot
        from utils.logger import log_info
        print("1. Импорт бота выполнен успешно")
        
        bot = AdvancedTradingBot()
        print("2. Экземпляр бота создан успешно")
        
        # Проверяем основные атрибуты
        print(f"3. Настройки: {type(bot.settings)}")
        print(f"4. Биржа: {type(bot.exchange)}")
        print(f"5. Менеджер рисков: {type(bot.risk_manager)}")
        print(f"6. Метрики: {type(bot.metrics)}")
        print(f"7. is_running: {bot.is_running}")
        print(f"8. trading_enabled: {bot.settings.settings.get('trading_enabled', 'NOT SET')}")
        
        # Запускаем один торговый цикл вручную
        print("9. Запускаем тестовый торговый цикл...")
        bot.execute_trading_cycle()
        print("10. Торговый цикл завершен")
        
        # Запускаем основной цикл
        print("11. ЗАПУСКАЕМ ОСНОВНОЙ ЦИКЛ...")
        bot.run()
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_bot()