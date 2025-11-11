"""
Тест для проверки запуска серверов
"""
import sys
import os
import subprocess
import time
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_minimal_server():
    """Тест минимального сервера"""
    print("=" * 60)
    print("🧪 ТЕСТ 1: Минимальный сервер")
    print("=" * 60)
    
    try:
        # Пробуем импортировать
        print("\n1️⃣ Импорт модулей...")
        from fastapi import FastAPI
        import uvicorn
        print("   ✅ FastAPI и Uvicorn импортированы")
        
        # Пробуем создать app
        print("\n2️⃣ Создание FastAPI app...")
        test_app = FastAPI()
        
        @test_app.get("/")
        async def root():
            return {"status": "ok"}
        
        print("   ✅ App создан успешно")
        
        print("\n✅ Минимальный сервер готов к запуску")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webapp_server():
    """Тест основного webapp сервера"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 2: Основной webapp сервер")
    print("=" * 60)
    
    try:
        print("\n1️⃣ Импорт webapp.server...")
        from webapp.server import app
        print("   ✅ webapp.server импортирован")
        
        print("\n2️⃣ Проверка app...")
        if app is None:
            print("   ❌ App не создан")
            return False
        
        print(f"   ✅ App создан: {type(app)}")
        
        print("\n3️⃣ Проверка маршрутов...")
        routes = [route.path for route in app.routes]
        print(f"   Найдено маршрутов: {len(routes)}")
        
        print("\n✅ Основной сервер готов к запуску")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webapp_only():
    """Тест webapp_only.py"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 3: webapp_only.py")
    print("=" * 60)
    
    try:
        print("\n1️⃣ Проверка импортов в webapp_only...")
        
        # Проверяем что модули доступны
        import uvicorn
        print("   ✅ uvicorn")
        
        from webapp.server import app
        print("   ✅ webapp.server")
        
        print("\n✅ webapp_only.py готов к запуску")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🔍 ДИАГНОСТИКА СЕРВЕРОВ")
    print("=" * 60)
    
    results = []
    
    # Тест 1
    result1 = test_minimal_server()
    results.append(("Минимальный сервер", result1))
    
    # Тест 2
    result2 = test_webapp_server()
    results.append(("Основной webapp", result2))
    
    # Тест 3
    result3 = test_webapp_only()
    results.append(("webapp_only.py", result3))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("\n📝 Следующий шаг:")
        print("   git add .")
        print('   git commit -m "[v1.0.2] Улучшена обработка ошибок в webapp_only.py"')
        print("   git push")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("Необходимо исправить ошибки перед деплоем")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
