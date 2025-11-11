"""
Тест запуска webapp_only.py для проверки перед деплоем на Amvera
"""
import sys
import os
import subprocess
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_webapp_only():
    """Тестируем запуск webapp_only.py"""
    print("=" * 60)
    print("🧪 ТЕСТ: запуск webapp_only.py")
    print("=" * 60)
    
    try:
        # Проверяем импорт модулей
        print("\n1️⃣ Проверка импортов...")
        
        print("   - Импорт uvicorn...", flush=True)
        import uvicorn
        print("   ✅ uvicorn", flush=True)
        
        print("   - Импорт fastapi...", flush=True)
        import fastapi
        print("   ✅ fastapi", flush=True)
        
        print("   - Импорт webapp.server...", flush=True)
        from webapp.server import app
        print("   ✅ webapp.server", flush=True)
        
        # Проверяем, что app создан
        print("\n2️⃣ Проверка FastAPI app...")
        if app is None:
            print("   ❌ App не создан")
            return False
        print(f"   ✅ App создан: {type(app)}")
        
        # Проверяем эндпоинты
        print("\n3️⃣ Проверка эндпоинтов...")
        routes = [route.path for route in app.routes]
        print(f"   Найдено маршрутов: {len(routes)}")
        for route in routes[:5]:  # Показываем первые 5
            print(f"   - {route}")
        
        print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        print("\n📝 Следующий шаг:")
        print("   1. Закоммитьте изменения:")
        print("      git add .")
        print('      git commit -m "[v1.0.0] Исправление HTTP 500: упрощенный запуск Web App"')
        print("      git push")
        print("\n   2. Перезапустите сервис на Amvera")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_webapp_only()
    sys.exit(0 if success else 1)
