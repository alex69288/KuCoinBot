"""
ФИКС ПРОБЛЕМ С TELEGRAM
"""
import os
import sys
import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def test_telegram_connection():
    print("🔧 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К TELEGRAM")
    print("=" * 50)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле")
        return False
    
    # Тестируем разные методы
    methods = [
        f"https://api.telegram.org/bot{token}/getMe",
        f"https://api.telegram.org/bot{token}/getUpdates",
    ]
    
    for method in methods:
        try:
            print(f"🔍 Тестируем: {method.split('/')[-1]}")
            response = requests.get(method, timeout=15)
            print(f"✅ Статус: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    print("✅ Подключение успешно!")
                    return True
                else:
                    print(f"❌ Ошибка API: {data}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
        except requests.exceptions.ConnectTimeout:
            print("❌ Таймаут подключения (15 сек)")
            print("💡 Возможные причины:")
            print("   - Проблемы с интернет-соединением")
            print("   - Блокировка Telegram в вашей сети")
            print("   - Используйте VPN если Telegram заблокирован")
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка соединения")
            print("💡 Проверьте интернет-подключение")
        except Exception as e:
            print(f"❌ Другая ошибка: {e}")
    
    return False

if __name__ == "__main__":
    test_telegram_connection()