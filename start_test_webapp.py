"""
Быстрый запуск тестового Web App сервера
Для локального тестирования без ngrok
"""
import subprocess
import sys
import time
import webbrowser

print("=" * 60)
print("  🧪 ЗАПУСК ТЕСТОВОГО WEB APP")
print("=" * 60)
print()
print("⚠️  Это демо версия с тестовыми данными")
print("Для полной функциональности используйте ngrok")
print()

# Запускаем тестовый сервер
print("[1/2] Запуск тестового сервера...")
try:
    # Запускаем в фоне
    subprocess.Popen(
        [sys.executable, "-m", "webapp.server_test"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    # Ждем запуска
    time.sleep(3)
    
    print("✅ Сервер запущен на http://localhost:8000")
    print()
    print("[2/2] Открываем в браузере...")
    time.sleep(1)
    
    # Открываем в браузере
    webbrowser.open("http://localhost:8000")
    
    print()
    print("=" * 60)
    print("  ✅ WEB APP ЗАПУЩЕН")
    print("=" * 60)
    print()
    print("📱 Откройте в браузере: http://localhost:8000")
    print()
    print("⚠️  Это тестовая версия с демо данными")
    print()
    print("Для использования в Telegram:")
    print("1. Установите ngrok: https://ngrok.com/download")
    print("2. Запустите: start_webapp_with_ngrok.bat")
    print("3. Получите HTTPS URL и добавьте в .env")
    print()
    print("Для остановки сервера закройте консольное окно")
    print()
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print()
    input("Нажмите Enter для выхода...")
