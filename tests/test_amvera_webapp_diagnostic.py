"""
Диагностика WebApp кнопки - проверка на Amvera
"""
import os
import sys
from dotenv import load_dotenv

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем .env файл
load_dotenv()

def check_webapp_configuration():
    """Проверка конфигурации WebApp"""
    
    print("\n" + "="*60)
    print("🔍 ДИАГНОСТИКА WEBAPP КОНФИГУРАЦИИ")
    print("="*60 + "\n")
    
    # Проверяем переменные окружения
    webapp_url = os.getenv('WEBAPP_URL', '')
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    
    print("📋 Переменные окружения:")
    print(f"  WEBAPP_URL: {webapp_url if webapp_url else '❌ НЕ УСТАНОВЛЕНА'}")
    print(f"  TELEGRAM_BOT_TOKEN: {'✅ Установлен' if telegram_token else '❌ НЕ УСТАНОВЛЕН'}")
    print(f"  TELEGRAM_CHAT_ID: {'✅ Установлен' if telegram_chat_id else '❌ НЕ УСТАНОВЛЕН'}")
    print()
    
    # Валидация WEBAPP_URL
    is_valid = False
    reason = ""
    
    if not webapp_url:
        reason = "❌ URL не установлен"
    elif webapp_url == 'https://your-server.com':
        reason = "❌ Используется URL по умолчанию (заглушка)"
    elif not webapp_url.startswith('https://'):
        reason = f"❌ URL должен начинаться с https:// (текущий: {webapp_url[:50]})"
    else:
        is_valid = True
        reason = "✅ URL корректен"
    
    print("🔍 Валидация WEBAPP_URL:")
    print(f"  {reason}")
    print()
    
    # Рекомендации
    if not is_valid:
        print("⚠️  WEBAPP НЕ БУДЕТ РАБОТАТЬ!")
        print()
        print("📝 Что нужно сделать:")
        print("  1. Зайдите в панель Amvera: https://console.amvera.io")
        print("  2. Откройте ваш проект")
        print("  3. Настройки → Переменные окружения")
        print("  4. Добавьте переменную:")
        print("     Ключ: WEBAPP_URL")
        print("     Значение: https://kucoinbot-alex69288.amvera.io/")
        print("  5. Сохраните и перезапустите проект")
        print()
    else:
        print("✅ WEBAPP НАСТРОЕН ПРАВИЛЬНО!")
        print()
        print(f"🌐 URL: {webapp_url}")
        print()
        print("💡 Что должно происходить:")
        print("  1. При запуске бота отправляется кнопка WebApp")
        print("  2. При команде /start появляется кнопка '🚀 Открыть Web App'")
        print("  3. При нажатии кнопки открывается WebApp интерфейс")
        print()
    
    # Проверка логики из telegram/bot.py
    print("🧪 Имитация логики telegram/bot.py:")
    print()
    
    if not webapp_url or webapp_url == 'https://your-server.com':
        print("  ⚠️  send_webapp_button() вернет False")
        print("  📝 Будет показано информационное сообщение")
    elif not webapp_url.startswith('https://'):
        print("  ⚠️  send_webapp_button() вернет False")
        print("  📝 Будет показано сообщение об ошибке HTTPS")
    else:
        print("  ✅ send_webapp_button() отправит кнопку WebApp")
        print("  ✅ В главном меню будет кнопка '🚀 Открыть Web App'")
    
    print()
    print("="*60)
    
    return is_valid


def check_telegram_connection():
    """Проверка подключения к Telegram"""
    import requests
    
    print("\n" + "="*60)
    print("🔌 ПРОВЕРКА ПОДКЛЮЧЕНИЯ К TELEGRAM")
    print("="*60 + "\n")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не установлен")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Подключение успешно!")
                print(f"  Имя бота: {bot_info.get('first_name')}")
                print(f"  Username: @{bot_info.get('username')}")
                print(f"  ID: {bot_info.get('id')}")
                print()
                return True
        
        print(f"❌ Ошибка: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def main():
    """Запуск диагностики"""
    
    print("\n🤖 ДИАГНОСТИКА KUCOIN BOT НА AMVERA\n")
    
    # Проверка конфигурации
    config_ok = check_webapp_configuration()
    
    # Проверка подключения к Telegram
    telegram_ok = check_telegram_connection()
    
    # Итоги
    print("="*60)
    print("📊 ИТОГИ ДИАГНОСТИКИ")
    print("="*60)
    print(f"  Конфигурация WebApp: {'✅ OK' if config_ok else '❌ ТРЕБУЕТ НАСТРОЙКИ'}")
    print(f"  Подключение Telegram: {'✅ OK' if telegram_ok else '❌ ОШИБКА'}")
    print()
    
    if config_ok and telegram_ok:
        print("🎉 ВСЕ НАСТРОЕНО! Бот должен работать корректно.")
        print()
        print("💡 Проверьте в Telegram:")
        print("   1. Отправьте боту /start")
        print("   2. Должна появиться кнопка '🚀 Открыть Web App'")
        print("   3. При нажатии откроется WebApp")
    else:
        print("⚠️  ТРЕБУЕТСЯ НАСТРОЙКА!")
        print()
        if not config_ok:
            print("   → Добавьте WEBAPP_URL на Amvera")
        if not telegram_ok:
            print("   → Проверьте TELEGRAM_BOT_TOKEN")
    
    print()
    print("="*60)
    print()
    
    return config_ok and telegram_ok


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
