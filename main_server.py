"""
ЗАПУСК БОТА С ИНТЕГРИРОВАННЫМ WEB APP - СЕРВЕРНАЯ ВЕРСИЯ
Запускает торгового бота вместе с Web App сервером
Использует переменные окружения из системы (Amvera, Railway, и т.д.)
БЕЗ загрузки .env файла
"""
import sys
import os
import time
import traceback
import threading

# 🔧 Исправление кодировки консоли для Windows (UTF-8)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# ========================================
# ВАЖНО: НЕ загружаем .env для серверного деплоя
# Переменные окружения устанавливаются в панели хостинга
# ========================================

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.logger import log_info, log_error


def check_environment():
    """Проверяет наличие критических переменных окружения"""
    print("\n🔍 Проверка переменных окружения...", flush=True)
    
    required_vars = {
        'KUCOIN_API_KEY': 'API ключ KuCoin',
        'KUCOIN_SECRET_KEY': 'API секрет KuCoin',
        'KUCOIN_PASSPHRASE': 'API парольная фраза KuCoin',
        'TELEGRAM_BOT_TOKEN': 'Токен Telegram бота',
        'TELEGRAM_CHAT_ID': 'ID чата Telegram'
    }
    
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(var)
            print(f"❌ {var}: НЕ УСТАНОВЛЕНА", flush=True)
        else:
            value = os.getenv(var)
            masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '***'
            print(f"✅ {var}: {masked}", flush=True)
    
    # Проверяем опциональные переменные
    webapp_url = os.getenv('WEBAPP_URL')
    if webapp_url:
        print(f"✅ WEBAPP_URL: {webapp_url}", flush=True)
    else:
        print(f"⚠️  WEBAPP_URL: не установлена (используется автоопределение)", flush=True)
    
    if missing:
        print(f"\n❌ ОШИБКА: Не установлены переменные: {', '.join(missing)}", flush=True)
        print("Настройте их в панели управления хостинга (Amvera, Railway и т.д.)", flush=True)
        return False
    
    print("✅ Все обязательные переменные установлены\n", flush=True)
    return True


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
    
    print("=" * 60, flush=True)
    print("🤖 ЗАПУСК TRADING BOT + WEB APP (СЕРВЕРНАЯ ВЕРСИЯ)", flush=True)
    print("=" * 60, flush=True)
    
    # Проверяем переменные окружения
    if not check_environment():
        print("❌ Запуск невозможен без необходимых переменных окружения", flush=True)
        print("💡 Настройте переменные в панели хостинга", flush=True)
        sys.exit(1)
    
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
        print("⏳ Ожидание запуска сервера (3 сек)...", flush=True)
        time.sleep(3)
        
        # Проверка доступности сервера
        port = int(os.getenv('PORT', 8000))
        webapp_url = os.getenv('WEBAPP_URL', f'http://0.0.0.0:{port}')
        print(f"✅ Web App сервер запущен", flush=True)
        print(f"🌐 Доступен по адресу: {webapp_url}", flush=True)
        print("📱 Откройте Web App через кнопку в Telegram боте", flush=True)
        
        # Запускаем основной цикл бота
        print("=" * 60, flush=True)
        print("🤖 Запуск основного цикла торгового бота...", flush=True)
        print("=" * 60, flush=True)
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки (Ctrl+C)", flush=True)
        print("🛑 Остановка бота и Web App сервера...", flush=True)
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА В MAIN: {e}", flush=True)
        print("=" * 60, flush=True)
        traceback.print_exc()
        print("=" * 60, flush=True)
        sys.exit(1)
        
    finally:
        print("👋 Завершение работы", flush=True)


if __name__ == "__main__":
    main()
