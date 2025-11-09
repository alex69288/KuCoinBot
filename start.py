"""
Безопасный запуск бота с проверкой окружения
"""
import sys
import os

# Добавляем путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Главная функция с проверкой окружения"""
    print("=" * 60, flush=True)
    print("🚀 ЗАПУСК KUCOIN TRADING BOT", flush=True)
    print("=" * 60, flush=True)
    
    # Проверяем переменные окружения
    from check_env import check_environment
    
    if not check_environment():
        print("\n❌ Не удалось запустить бот: не настроены переменные окружения", flush=True)
        print("\nНастройте переменные в панели Amvera:", flush=True)
        print("1. KUCOIN_API_KEY", flush=True)
        print("2. KUCOIN_SECRET_KEY", flush=True)
        print("3. KUCOIN_PASSPHRASE", flush=True)
        print("4. TELEGRAM_BOT_TOKEN", flush=True)
        print("5. TELEGRAM_CHAT_ID", flush=True)
        return 1
    
    print("\n✅ Переменные окружения настроены корректно", flush=True)
    print("\n" + "=" * 60, flush=True)
    print("🤖 Запуск основного приложения...", flush=True)
    print("=" * 60 + "\n", flush=True)
    
    # Импортируем и запускаем основное приложение
    try:
        print("📦 Импорт главного модуля приложения...", flush=True)
        from main_with_webapp import main as app_main
        print("✅ Главный модуль импортирован", flush=True)
        
        print("🚀 Запуск приложения...", flush=True)
        app_main()
        return 0
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА В START.PY: {e}", flush=True)
        print("=" * 60, flush=True)
        import traceback
        traceback.print_exc()
        print("=" * 60, flush=True)
        return 1

if __name__ == "__main__":
    # Отключаем буферизацию вывода
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    sys.exit(main())
