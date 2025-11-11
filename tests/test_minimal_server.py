"""
Тест запуска минимального сервера
"""
import sys
import subprocess
import time
import requests
import os

def test_minimal_server_startup():
    """Проверка запуска минимального сервера"""
    print("=" * 60)
    print("🧪 ТЕСТ: Запуск minimal_server.py")
    print("=" * 60)
    
    # Запускаем сервер в фоне
    print("\n1️⃣ Запуск сервера...")
    
    # Устанавливаем переменную окружения PORT
    env = os.environ.copy()
    env['PORT'] = '8001'
    
    process = subprocess.Popen(
        [sys.executable, 'minimal_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Ждем запуска
    print("⏳ Ожидание запуска сервера (5 секунд)...")
    time.sleep(5)
    
    try:
        # Проверяем, что процесс жив
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("\n❌ СЕРВЕР ЗАВЕРШИЛСЯ С ОШИБКОЙ")
            print("\nSTDOUT:")
            print(stdout)
            print("\nSTDERR:")
            print(stderr)
            return False
        
        print("✅ Процесс запущен")
        
        # Пробуем подключиться
        print("\n2️⃣ Проверка подключения...")
        
        try:
            response = requests.get('http://localhost:8001/ping', timeout=5)
            print(f"✅ /ping ответил: {response.status_code}")
            print(f"   Ответ: {response.json()}")
            
            response = requests.get('http://localhost:8001/', timeout=5)
            print(f"✅ / ответил: {response.status_code}")
            print(f"   Ответ: {response.json()}")
            
            print("\n✅ МИНИМАЛЬНЫЙ СЕРВЕР РАБОТАЕТ!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
            
    finally:
        # Останавливаем сервер
        print("\n3️⃣ Остановка сервера...")
        process.terminate()
        try:
            process.wait(timeout=5)
            print("✅ Сервер остановлен")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️ Сервер принудительно остановлен")

if __name__ == "__main__":
    try:
        success = test_minimal_server_startup()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ТЕСТ ПРОЙДЕН")
            print("\n📝 Минимальный сервер работает корректно.")
            print("   Можно деплоить на Amvera!")
        else:
            print("❌ ТЕСТ НЕ ПРОЙДЕН")
            print("\n⚠️ Минимальный сервер не работает даже локально.")
            print("   Проверьте зависимости и настройки.")
        print("=" * 60)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван пользователем")
        sys.exit(1)
