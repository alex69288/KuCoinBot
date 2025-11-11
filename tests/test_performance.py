"""
Тест производительности WebSocket соединения
Измеряет задержку получения сообщений
"""
import asyncio
import websockets
import time
import statistics
from datetime import datetime

async def measure_latency():
    """Измерить задержку WebSocket соединения"""
    uri = "ws://localhost:8000/ws"
    latencies = []
    
    print("=" * 50)
    print("⚡ Тест производительности WebSocket")
    print("=" * 50)
    print(f"\n🔍 Подключение к {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Подключено!")
            print("\n📊 Измерение задержки (10 сообщений)...\n")
            
            for i in range(10):
                start = time.perf_counter()
                
                # Ждем сообщение
                message = await websocket.recv()
                
                end = time.perf_counter()
                latency = (end - start) * 1000  # в миллисекундах
                latencies.append(latency)
                
                # Определяем статус
                if latency < 100:
                    status = "🟢"
                elif latency < 500:
                    status = "🟡"
                else:
                    status = "🔴"
                
                print(f"  {status} Сообщение {i+1}: {latency:.2f} мс")
                
            print("\n" + "=" * 50)
            print("📈 СТАТИСТИКА")
            print("=" * 50)
            print(f"Среднее:  {statistics.mean(latencies):.2f} мс")
            print(f"Минимум:  {min(latencies):.2f} мс")
            print(f"Максимум: {max(latencies):.2f} мс")
            print(f"Медиана:  {statistics.median(latencies):.2f} мс")
            
            avg = statistics.mean(latencies)
            print("\n" + "=" * 50)
            print("💡 ОЦЕНКА")
            print("=" * 50)
            
            if avg < 100:
                print("🟢 Отлично! Задержка < 100 мс")
                print("   Система работает идеально")
            elif avg < 500:
                print("🟡 Приемлемо (100-500 мс)")
                print("   Можно улучшить производительность сервера")
            else:
                print("🔴 Высокая задержка (> 500 мс)")
                print("   Рекомендуется проверить:")
                print("   - Загрузку сервера")
                print("   - Скорость соединения")
                print("   - Производительность API KuCoin")
                
    except ConnectionRefusedError:
        print("\n❌ Ошибка: Сервер не запущен!")
        print("\n💡 Запустите сервер:")
        print("   python main_with_webapp.py")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 50)

if __name__ == "__main__":
    print(f"\n⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    asyncio.run(measure_latency())
