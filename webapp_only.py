"""
Упрощенный запуск только Web App для Amvera
Без обязательной проверки переменных окружения - они нужны будут только при запуске бота
"""
import sys
import os
import time

# Отключаем буферизацию вывода
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Добавляем путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Запуск только Web App без торгового бота"""
    start_time = time.time()
    
    print("=" * 60, flush=True)
    print("🌐 ЗАПУСК WEB APP (только интерфейс)", flush=True)
    print("=" * 60, flush=True)
    
    try:
        # Импортируем необходимые модули
        print("📦 Импорт модулей...", flush=True)
        
        print("  - Импорт uvicorn...", flush=True)
        import uvicorn
        print("  ✅ uvicorn", flush=True)
        
        print("  - Импорт webapp.server...", flush=True)
        from webapp.server import app
        print("  ✅ webapp.server", flush=True)
        
        # Получаем порт из переменной окружения
        port = int(os.getenv('PORT', 8000))
        
        print("\n" + "=" * 60, flush=True)
        print(f"✅ Инициализация завершена за {time.time() - start_time:.2f} сек", flush=True)
        print(f"🚀 ЗАПУСК WEB APP НА ПОРТУ {port}", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)
        print("📝 ВАЖНО: Торговый бот будет запущен через веб-интерфейс", flush=True)
        print("   после настройки переменных окружения в Amvera.", flush=True)
        print("", flush=True)
        print("🔧 Необходимые переменные окружения:", flush=True)
        print("   - KUCOIN_API_KEY", flush=True)
        print("   - KUCOIN_SECRET_KEY", flush=True)
        print("   - KUCOIN_PASSPHRASE", flush=True)
        print("   - TELEGRAM_BOT_TOKEN", flush=True)
        print("   - TELEGRAM_CHAT_ID", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)
        
        # Запускаем Uvicorn как ГЛАВНЫЙ процесс
        print("🔄 Запуск Uvicorn сервера...", flush=True)
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            timeout_keep_alive=30,
        )
        
    except ImportError as e:
        print(f"\n❌ ОШИБКА ИМПОРТА: {e}", flush=True)
        print("Проверьте, что все зависимости установлены:", flush=True)
        print("  pip install -r requirements.txt", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки", flush=True)
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}", flush=True)
        print(f"Тип ошибки: {type(e).__name__}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
