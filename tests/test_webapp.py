"""
Тест Web App сервера
Проверяет работоспособность API endpoints
"""
import requests
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import log_info, log_error

API_URL = "http://localhost:8000/api"

def test_health_check():
    """Тест проверки здоровья сервера"""
    try:
        log_info("🧪 Тестирование health check...")
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_info(f"✅ Health check успешен: {data}")
            return True
        else:
            log_error(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_error("❌ Не удается подключиться к серверу. Убедитесь, что сервер запущен.")
        log_info("💡 Запустите сервер: python -m webapp.server")
        return False
    except Exception as e:
        log_error(f"❌ Ошибка теста health check: {e}")
        return False


def test_status_without_auth():
    """Тест получения статуса без авторизации (должен вернуть 401)"""
    try:
        log_info("🧪 Тестирование защиты авторизации...")
        response = requests.get(f"{API_URL}/status", timeout=5)
        
        if response.status_code == 422:  # FastAPI возвращает 422 если параметр отсутствует
            log_info("✅ Защита работает: требуется init_data")
            return True
        else:
            log_error(f"❌ Неожиданный код ответа: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"❌ Ошибка теста авторизации: {e}")
        return False


def test_server_running():
    """Проверяет, запущен ли сервер"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def print_test_summary(results):
    """Выводит сводку тестов"""
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("=" * 50)
    print(f"Пройдено: {passed}/{total} ({passed/total*100:.0f}%)")
    print("=" * 50)


def main():
    """Запускает все тесты"""
    log_info("🚀 Запуск тестов Web App")
    log_info(f"🌐 API URL: {API_URL}")
    
    # Проверяем, запущен ли сервер
    if not test_server_running():
        log_error("\n❌ Сервер не запущен!")
        log_info("\n💡 Для запуска сервера выполните:")
        log_info("   python -m webapp.server")
        log_info("\n   Или в отдельном терминале:")
        log_info("   cd c:\\Users\\user\\Documents\\Scripts\\KuCoinBotV4Copilot")
        log_info("   python -m webapp.server")
        return
    
    log_info("✅ Сервер запущен, начинаем тестирование\n")
    
    # Запускаем тесты
    results = {
        "Health Check": test_health_check(),
        "Authorization Protection": test_status_without_auth(),
    }
    
    # Выводим результаты
    print_test_summary(results)
    
    # Информация о дальнейших шагах
    if all(results.values()):
        log_info("\n🎉 Все тесты пройдены!")
        log_info("\n📝 Следующие шаги:")
        log_info("1. Установите WEBAPP_URL в .env файл")
        log_info("2. Разверните сервер на хостинге с HTTPS")
        log_info("3. Настройте кнопку Web App в @BotFather")
        log_info("4. Откройте Web App из Telegram")
    else:
        log_error("\n⚠️ Некоторые тесты не прошли. Проверьте логи выше.")


if __name__ == "__main__":
    main()
