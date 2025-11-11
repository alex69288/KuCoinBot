"""
ЗАПУСК WEB APP КАК ОСНОВНОГО ПРОЦЕССА
Uvicorn работает в главном потоке, торговый бот - в фоне
Это правильная архитектура для облачных платформ типа Amvera
"""
import sys
import os
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.logger import log_info, log_error


def run_trading_bot(bot):
    """Запускает торговый цикл бота в фоновом потоке"""
    try:
        log_info("🤖 Запуск торгового цикла в фоновом режиме...")
        bot.run()
    except Exception as e:
        log_error(f"❌ Ошибка в торговом боте: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Основная функция - запускает Web App как главный процесс"""
    start_time = time.time()
    
    print("=" * 60, flush=True)
    print("🌐 ЗАПУСК WEB APP (главный процесс)", flush=True)
    print("=" * 60, flush=True)
    
    try:
        # 1. Импортируем и создаём бота
        print("📦 Создание торгового бота...", flush=True)
        from core.bot import AdvancedTradingBot
        bot = AdvancedTradingBot()
        print(f"✅ Бот создан за {time.time() - start_time:.2f} сек", flush=True)
        
        # 2. Запускаем торговый цикл в фоновом потоке
        print("🤖 Запуск торгового бота в фоновом потоке...", flush=True)
        bot_thread = threading.Thread(
            target=run_trading_bot,
            args=(bot,),
            daemon=True,
            name="TradingBotThread"
        )
        bot_thread.start()
        print("✅ Торговый бот запущен в фоне", flush=True)
        
        # 3. Настраиваем Web App сервер
        print("🌐 Настройка Web App сервера...", flush=True)
        import uvicorn
        from webapp.server import app, set_trading_bot
        
        # Устанавливаем экземпляр бота в Web App
        set_trading_bot(bot)
        
        # Получаем порт из переменной окружения
        port = int(os.getenv('PORT', 8000))
        
        print("=" * 60, flush=True)
        print(f"🚀 ЗАПУСК UVICORN НА ПОРТУ {port}", flush=True)
        print("=" * 60, flush=True)
        
        # 4. Запускаем Uvicorn как ГЛАВНЫЙ процесс
        # Это гарантирует, что Amvera увидит порт 8000
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            # Важно: без reload и workers для стабильности в облаке
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки", flush=True)
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
