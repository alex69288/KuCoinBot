"""
Локальный тест WebApp с проверкой загрузки
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("="*60)
print("ЛОКАЛЬНЫЙ ТЕСТ WEBAPP")
print("="*60)

# Проверяем наличие index.html
webapp_dir = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static')
index_path = os.path.join(webapp_dir, 'index.html')

print(f"\n📂 Путь к webapp: {webapp_dir}")
print(f"📄 Путь к index.html: {index_path}")

if os.path.exists(index_path):
    print("✅ Файл index.html найден")
    
    # Читаем и проверяем содержимое
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем важные элементы
    checks = [
        ("Telegram WebApp SDK", "telegram-web-app.js" in content),
        ("DOMContentLoaded", "DOMContentLoaded" in content),
        ("loadData функция", "async function loadData" in content),
        ("loadStatus функция", "async function loadStatus" in content),
        ("loadMarket функция", "async function loadMarket" in content),
        ("Логи загрузки", "console.log" in content and "Начало загрузки данных" in content),
    ]
    
    print("\n🔍 Проверка содержимого:")
    all_ok = True
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result:
            all_ok = False
    
    if all_ok:
        print("\n🎉 Все проверки пройдены!")
        print("\n📝 Инструкция для тестирования:")
        print("1. Запустите бота: python main_with_webapp.py")
        print("2. Откройте в браузере: http://localhost:8000")
        print("3. Откройте консоль браузера (F12)")
        print("4. Проверьте логи: должны появиться сообщения:")
        print("   - 🚀 WebApp загружен")
        print("   - 📊 Начало загрузки данных...")
        print("   - ✅ Данные загружены успешно")
    else:
        print("\n⚠️ Некоторые проверки не прошли")
        
else:
    print("❌ Файл index.html не найден!")

print("\n" + "="*60)
