"""
ОПТИМИЗИРОВАННЫЙ ЗАПУСК БОТА
"""
import sys
import os
import time
import traceback

# Переносим импорт логгера ВНЕ функции и ДО try
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.logger import log_info, log_error

def quick_start():
    """Быстрый старт с минимальной задержкой"""
    start_time = time.time()
    print("⚡ БЫСТРЫЙ ЗАПУСК ТОРГОВОГО БОТА")
    print("=" * 40)
    try:
        from core.bot import AdvancedTradingBot
        log_info("Создаем экземпляр бота...")
        bot = AdvancedTradingBot()
        init_time = time.time() - start_time
        log_info(f"✅ Бот готов за {init_time:.2f} сек")
        log_info("Запускаем основной цикл работы...")
        bot.run()
    except KeyboardInterrupt:
        log_info("🛑 Бот остановлен пользователем")
    except Exception as e:
        log_error(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    quick_start()