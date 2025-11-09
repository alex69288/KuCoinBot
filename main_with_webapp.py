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
    
    print("=" * 50)
    print("🤖 ЗАПУСК TRADING BOT + WEB APP")
    print("=" * 50)
    
    try:
        # Импортируем бота
        from core.bot import AdvancedTradingBot
        
        log_info("⚡ Создание экземпляра торгового бота...")
        bot = AdvancedTradingBot()
        
        init_time = time.time() - start_time
        log_info(f"✅ Бот готов за {init_time:.2f} сек")
        
        # Запускаем Web App сервер в отдельном потоке
        log_info("🚀 Запуск Web App сервера в фоновом режиме...")
        webapp_thread = threading.Thread(
            target=start_webapp_server,
            args=(bot,),
            daemon=True
        )
        webapp_thread.start()
        
        # Даем серверу время на запуск
        time.sleep(2)
        
        # Проверяем, что сервер запущен
        try:
            import requests
            port = int(os.getenv('PORT', 8000))
            response = requests.get(f"http://localhost:{port}/api/health", timeout=2)
            if response.status_code == 200:
                log_info("✅ Web App сервер успешно запущен")
                log_info(f"🌐 API доступен: http://localhost:{port}")
                log_info("📱 Откройте Web App через кнопку в Telegram боте")
            else:
                log_error("⚠️ Web App сервер запущен, но вернул неожиданный статус")
        except Exception as e:
            log_error(f"⚠️ Не удалось проверить Web App сервер: {e}")
        
        # Запускаем основной цикл бота
        log_info("=" * 50)
        log_info("🤖 Запуск основного цикла торгового бота...")
        log_info("=" * 50)
        bot.run()
        
    except KeyboardInterrupt:
        log_info("\n🛑 Получен сигнал остановки (Ctrl+C)")
        log_info("🛑 Остановка бота и Web App сервера...")
        
    except Exception as e:
        log_error(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()
        
    finally:
        log_info("👋 Завершение работы")


if __name__ == "__main__":
    main()
