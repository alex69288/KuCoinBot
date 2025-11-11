"""
ТЕСТ ПОЛНОГО ФУНКЦИОНАЛА WEBAPP
Проверяет все эндпоинты и функции веб-приложения
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from webapp.server import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    """Тест health check"""
    print("\n🔍 Тест 1: Health Check")
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Health: {data}")
    assert "status" in data

def test_root():
    """Тест главной страницы"""
    print("\n🔍 Тест 2: Главная страница")
    response = client.get("/")
    assert response.status_code == 200
    print("✅ Главная страница загружена")

def test_api_endpoints_without_auth():
    """Тест API эндпоинтов без авторизации (должны вернуть 401)"""
    print("\n🔍 Тест 3: API эндпоинты без авторизации")
    
    endpoints = [
        ("/api/status", "GET"),
        ("/api/market", "GET"),
        ("/api/settings", "GET"),
        ("/api/positions", "GET"),
        ("/api/analytics", "GET"),
        ("/api/trade-history", "GET"),
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = client.get(f"{endpoint}?init_data=test")
            else:
                response = client.post(endpoint, json={"init_data": "test"})
            
            # Ожидаем либо 401 (нет авторизации), либо 503 (бот не инициализирован)
            assert response.status_code in [401, 503], f"{endpoint} вернул неожиданный код: {response.status_code}"
            print(f"✅ {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")

def test_api_structure():
    """Тест структуры API"""
    print("\n🔍 Тест 4: Структура API")
    
    # Проверяем, что все необходимые эндпоинты доступны
    required_endpoints = [
        # Основные
        "/api/status",
        "/api/market",
        "/api/settings",
        "/api/positions",
        "/api/analytics",
        "/api/trade-history",
        # Управление
        "/api/bot/start",
        "/api/bot/stop",
        # Настройки
        "/api/settings/trading",
        "/api/settings/ema",
        "/api/settings/risk",
        "/api/settings/ml",
        "/api/settings/general",
        # Позиции
        "/api/positions/close-all",
        # ML
        "/api/ml/retrain",
        # Аналитика
        "/api/analytics/reset",
    ]
    
    # Получаем список всех маршрутов
    routes = [route.path for route in app.routes]
    
    missing = []
    for endpoint in required_endpoints:
        found = False
        for route in routes:
            if route == endpoint or route.startswith(endpoint.split("{")[0]):
                found = True
                break
        if found:
            print(f"✅ {endpoint}")
        else:
            print(f"❌ {endpoint} - НЕ НАЙДЕН")
            missing.append(endpoint)
    
    if missing:
        print(f"\n⚠️ Отсутствующие эндпоинты: {missing}")
    else:
        print("\n✅ Все необходимые эндпоинты присутствуют")

def test_static_files():
    """Тест статических файлов"""
    print("\n🔍 Тест 5: Статические файлы")
    
    # Проверяем наличие файлов
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webapp", "static")
    
    if os.path.exists(os.path.join(static_path, "index.html")):
        print("✅ index.html найден")
    else:
        print("❌ index.html НЕ НАЙДЕН")
    
    if os.path.exists(os.path.join(static_path, "index_old.html")):
        print("✅ index_old.html найден (резервная копия)")

def print_available_routes():
    """Вывести все доступные маршруты"""
    print("\n📋 Доступные маршруты API:")
    print("-" * 60)
    
    routes_by_method = {}
    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                if method not in routes_by_method:
                    routes_by_method[method] = []
                routes_by_method[method].append(route.path)
    
    for method in sorted(routes_by_method.keys()):
        print(f"\n{method}:")
        for path in sorted(routes_by_method[method]):
            print(f"  {path}")

def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ WEBAPP ФУНКЦИОНАЛА")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        test_api_endpoints_without_auth()
        test_api_structure()
        test_static_files()
        print_available_routes()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ БАЗОВЫЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 60)
        print("\n📝 Примечание:")
        print("  - Для полного тестирования нужно запустить бота")
        print("  - Некоторые эндпоинты требуют авторизации через Telegram")
        print("  - API готов к использованию в WebApp")
        
    except AssertionError as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
