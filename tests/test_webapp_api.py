"""
Тест всех API endpoints для WebApp
"""
import requests
import json

# URL сервера
BASE_URL = "http://localhost:8000"

# Тестовые данные (пустые для локального тестирования без авторизации)
INIT_DATA = "test_init_data"

def test_health():
    """Тест проверки здоровья API"""
    print("\n🔍 Тест /api/health")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    return response.status_code == 200

def test_debug_paths():
    """Тест отладочных путей"""
    print("\n🔍 Тест /api/debug/paths")
    response = requests.get(f"{BASE_URL}/api/debug/paths")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root():
    """Тест корневой страницы"""
    print("\n🔍 Тест /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Статус: {response.status_code}")
    print(f"Размер HTML: {len(response.text)} байт")
    return response.status_code == 200

def test_ping():
    """Тест ping"""
    print("\n🔍 Тест /ping")
    response = requests.get(f"{BASE_URL}/ping")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    return response.status_code == 200

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 50)
    print("🧪 ТЕСТИРОВАНИЕ WEBAPP API")
    print("=" * 50)
    
    tests = [
        ("Ping", test_ping),
        ("Health Check", test_health),
        ("Debug Paths", test_debug_paths),
        ("Root Page", test_root),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 РЕЗУЛЬТАТЫ: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print(f"\n⚠️ {failed} тест(ов) провалено")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
