"""
Мониторинг WebSocket обновлений в реальном времени
Показывает все получаемые данные и статистику
"""
import asyncio
import websockets
import json
from datetime import datetime

async def monitor():
    """Мониторинг WebSocket обновлений в реальном времени"""
    uri = "ws://localhost:8000/ws"
    
    print("=" * 50)
    print("📡 Мониторинг WebSocket")
    print("=" * 50)
    print(f"\n🔍 Подключение к {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Подключено!")
            print("\n📊 Получение обновлений (Ctrl+C для остановки)...\n")
            print("-" * 50)
            
            message_count = 0
            start_time = datetime.now()
            
            while True:
                message = await websocket.recv()
                message_count += 1
                
                try:
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"\n[{timestamp}] 📨 Сообщение #{message_count}")
                    print("-" * 50)
                    
                    # Тип сообщения
                    msg_type = data.get('type', 'unknown')
                    print(f"Тип: {msg_type}")
                    
                    # Рыночные данные
                    if 'market' in data:
                        market = data['market']
                        print(f"\n💰 Рынок:")
                        print(f"  Пара:      {market.get('symbol')}")
                        print(f"  Цена:      ${market.get('current_price', 0):.2f}")
                        print(f"  Изменение: {market.get('change_24h', 0):+.2f}%")
                    
                    # EMA данные
                    if 'ema' in data:
                        ema = data['ema']
                        signal_emoji = {
                            'buy': '🟢',
                            'sell': '🔴',
                            'wait': '⚪'
                        }.get(ema.get('signal'), '⚪')
                        print(f"\n{signal_emoji} EMA:")
                        print(f"  Сигнал:  {ema.get('text')}")
                        print(f"  Процент: {ema.get('percent', 0):+.2f}%")
                    
                    # ML данные
                    if 'ml' in data:
                        ml = data['ml']
                        prediction = ml.get('prediction', 0)
                        ml_emoji = '🟢' if prediction > 0.6 else '🔴' if prediction < 0.4 else '🟡'
                        print(f"\n{ml_emoji} ML Предсказание:")
                        print(f"  Значение: {prediction*100:.1f}%")
                    
                    # Позиции
                    if 'positions' in data:
                        pos = data['positions']
                        profit = pos.get('current_profit_percent', 0)
                        profit_usdt = pos.get('current_profit_usdt', 0)
                        profit_emoji = '📈' if profit >= 0 else '📉'
                        print(f"\n{profit_emoji} Позиции:")
                        print(f"  Открыто: {pos.get('open_count', 0)}")
                        print(f"  Прибыль: {profit:+.2f}% ({profit_usdt:+.4f} USDT)")
                    
                    # Статистика
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = message_count / elapsed if elapsed > 0 else 0
                    print(f"\n⏱️  Статистика:")
                    print(f"  Время работы: {elapsed:.1f} сек")
                    print(f"  Частота:      {rate:.2f} сообщ/сек")
                    
                    print("-" * 50)
                    
                except json.JSONDecodeError:
                    print(f"⚠️  Неверный JSON: {message[:100]}...")
                    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("⏹️  ОСТАНОВЛЕНО ПОЛЬЗОВАТЕЛЕМ")
        print("=" * 50)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n📊 Итоговая статистика:")
        print(f"  Время работы:     {elapsed:.1f} сек")
        print(f"  Всего сообщений:  {message_count}")
        print(f"  Средняя частота:  {message_count/elapsed:.2f} сообщ/сек")
        
        if message_count / elapsed >= 0.9:
            print("\n✅ Частота обновлений оптимальна (~1 сообщ/сек)")
        else:
            print("\n⚠️  Частота обновлений ниже ожидаемой")
        
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
    asyncio.run(monitor())
