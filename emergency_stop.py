"""
ЭКСТРЕННАЯ ОСТАНОВКА БОТА
"""
import subprocess
import sys

print("⚠️  ВНИМАНИЕ: Это принудительно завершит ВСЕ процессы Python!")
print("Используйте только если не можете остановить бота вручную (Ctrl+C)")
print()

response = input("Продолжить? (yes/no): ")

if response.lower() in ['yes', 'y', 'да', 'д']:
    try:
        # Завершаем все процессы Python кроме текущего
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-Process python | Where-Object {{$_.Id -ne {sys.process.id}}} | Stop-Process -Force'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Процессы остановлены")
        else:
            print(f"⚠️  Результат: {result.stderr}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
else:
    print("❌ Отменено. Остановите бота вручную (Ctrl+C)")
