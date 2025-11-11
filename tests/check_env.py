"""
Проверка переменных окружения для Amvera
"""
import os
import sys

def check_environment():
    """Проверяет наличие всех необходимых переменных окружения"""
    print("=" * 60, flush=True)
    print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ", flush=True)
    print("=" * 60, flush=True)
    
    required_vars = {
        'KUCOIN_API_KEY': 'API ключ KuCoin',
        'KUCOIN_SECRET_KEY': 'API секрет KuCoin',
        'KUCOIN_PASSPHRASE': 'API парольная фраза KuCoin',
        'TELEGRAM_BOT_TOKEN': 'Токен Telegram бота',
        'TELEGRAM_CHAT_ID': 'ID чата Telegram'
    }
    
    optional_vars = {
        'PORT': 'Порт для Web App',
        'WEBAPP_URL': 'URL Web App'
    }
    
    missing = []
    present = []
    
    print("\n📋 Обязательные переменные:", flush=True)
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            present.append(var)
            # Показываем только первые 4 символа для безопасности
            masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '***'
            print(f"✅ {var}: {masked_value}", flush=True)
        else:
            missing.append(var)
            print(f"❌ {var}: НЕ УСТАНОВЛЕНА", flush=True)
    
    print("\n📋 Опциональные переменные:", flush=True)
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}", flush=True)
        else:
            print(f"⚠️  {var}: не установлена (будет использовано значение по умолчанию)", flush=True)
    
    print("\n" + "=" * 60, flush=True)
    
    if missing:
        print(f"❌ ОШИБКА: Не установлены {len(missing)} обязательные переменные:", flush=True)
        for var in missing:
            print(f"   - {var}", flush=True)
        print("\nНастройте переменные окружения в панели Amvera:", flush=True)
        print("https://amvera.ru/", flush=True)
        return False
    else:
        print(f"✅ ВСЕ ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ УСТАНОВЛЕНЫ", flush=True)
        print(f"✅ Найдено переменных: {len(present)}", flush=True)
        return True

if __name__ == "__main__":
    if check_environment():
        sys.exit(0)
    else:
        sys.exit(1)
