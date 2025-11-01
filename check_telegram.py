"""
ПРОВЕРКА НАСТРОЙКИ TELEGRAM
"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def check_telegram():
    print("🔍 ПРОВЕРКА НАСТРОЙКИ TELEGRAM")
    print("=" * 40)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"📱 TELEGRAM_BOT_TOKEN: {'✅ Установлен' if token else '❌ Отсутствует'}")
    print(f"👤 TELEGRAM_CHAT_ID: {'✅ Установлен' if chat_id else '❌ Отсутствует'}")
    
    if not token or not chat_id:
        print("\n❌ Telegram не настроен!")
        print("💡 Добавьте в файл .env:")
        print("TELEGRAM_BOT_TOKEN=ваш_токен_бота")
        print("TELEGRAM_CHAT_ID=ваш_chat_id")
        return False
    
    # Проверяем валидность токена
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print(f"✅ Бот: @{data['result']['username']}")
                print(f"✅ Имя: {data['result']['first_name']}")
                return True
        print(f"❌ Неверный токен: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    check_telegram()