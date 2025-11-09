"""
Безопасный запуск бота с проверкой окружения
"""
import sys
import os

# Добавляем путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Главная функция с проверкой окружения"""
    print("=" * 60)
    print("🚀 ЗАПУСК KUCOIN TRADING BOT")
    print("=" * 60)
    
    # Проверяем переменные окружения
    from check_env import check_environment
    
    if not check_environment():
        print("\n❌ Не удалось запустить бот: не настроены переменные окружения")
        print("\nНастройте переменные в панели Amvera:")
        print("1. KUCOIN_API_KEY")
        print("2. KUCOIN_API_SECRET")
        print("3. KUCOIN_API_PASSPHRASE")
        print("4. TELEGRAM_BOT_TOKEN")
        print("5. TELEGRAM_CHAT_ID")
        return 1
    
    print("\n✅ Переменные окружения настроены корректно")
    print("\n" + "=" * 60)
    print("🤖 Запуск основного приложения...")
    print("=" * 60 + "\n")
    
    # Импортируем и запускаем основное приложение
    try:
        from main_with_webapp import main as app_main
        app_main()
        return 0
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
