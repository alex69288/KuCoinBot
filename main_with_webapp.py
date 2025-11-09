"""
ЗАПУСК БОТА С ИНТЕГРИРОВАННЫМ WEB APP
Запускает торгового бота вместе с Web App сервером
"""
import sys
import os
import time
import traceback
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.logger import log_info, log_error


def start_webapp_server(bot):
    """Запускает Web App сервер в отдельном потоке"""
    try:
        import uvicorn
        from webapp.server import app, set_trading_bot
        
        # Устанавливаем экземпляр бота в Web App
        set_trading_bot(bot)
        
        # Получаем порт из переменной окружения (для облачных платформ)
        # Amvera по умолчанию использует порт 8000
        port = int(os.getenv('PORT', 8000))
        
        log_info(f"🌐 Запуск Web App сервера на http://0.0.0.0:{port}")
        log_info("📱 Web App будет доступен через Telegram")
        
        # Запускаем uvicorn сервер
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        log_error(f"❌ Ошибка запуска Web App сервера: {e}")
        traceback.print_exc()


def main():
    """Основная функция запуска"""
    start_time = time.time()
    
    print("=" * 50, flush=True)
    print("🤖 ЗАПУСК TRADING BOT + WEB APP", flush=True)
    print("=" * 50, flush=True)
    
    try:
        print("📦 Импорт модуля торгового бота...", flush=True)
        # Импортируем бота
        from core.bot import AdvancedTradingBot
        print("✅ Модуль импортирован успешно", flush=True)
        
        print("⚡ Создание экземпляра торгового бота...", flush=True)
        bot = AdvancedTradingBot()
        print("✅ Экземпляр бота создан", flush=True)
        
        init_time = time.time() - start_time
        print(f"✅ Бот готов за {init_time:.2f} сек", flush=True)
        
        # Запускаем Web App сервер в отдельном потоке
        print("🚀 Запуск Web App сервера в фоновом режиме...", flush=True)
        webapp_thread = threading.Thread(
            target=start_webapp_server,
            args=(bot,),
            daemon=True
        )
        webapp_thread.start()
        print("✅ Web App поток запущен", flush=True)
        
        # Даем серверу время на запуск
        print("⏳ Ожидание запуска сервера (2 сек)...", flush=True)
        time.sleep(2)
        
        # Проверяем, что сервер запущен
        try:
            print("🔍 Проверка доступности Web App...", flush=True)
            import requests
            port = int(os.getenv('PORT', 8000))
            response = requests.get(f"http://localhost:{port}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Web App сервер успешно запущен", flush=True)
                print(f"🌐 API доступен: http://localhost:{port}", flush=True)
                print("📱 Откройте Web App через кнопку в Telegram боте", flush=True)
            else:
                print("⚠️ Web App сервер запущен, но вернул неожиданный статус", flush=True)
        except Exception as e:
            print(f"⚠️ Не удалось проверить Web App сервер: {e}", flush=True)
        
        # Запускаем основной цикл бота
        print("=" * 50, flush=True)
        print("🤖 Запуск основного цикла торгового бота...", flush=True)
        print("=" * 50, flush=True)
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки (Ctrl+C)", flush=True)
        print("🛑 Остановка бота и Web App сервера...", flush=True)
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА В MAIN: {e}", flush=True)
        print("=" * 50, flush=True)
        traceback.print_exc()
        print("=" * 50, flush=True)
        sys.exit(1)
        
    finally:
        print("👋 Завершение работы", flush=True)


if __name__ == "__main__":
    main()
