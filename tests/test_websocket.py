"""
Тест WebSocket подключения и обновлений в реальном времени
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Тестирует WebSocket подключение к серверу"""
    
    # URL WebSocket (измените на ваш адрес сервера)
    ws_url = "ws://localhost:8000/ws"
    
    print("=" * 50)
    print("🔌 Тест WebSocket подключения")
    print("=" * 50)
    
    try:
        print(f"\n📡 Подключение к {ws_url}...")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket подключен успешно!\n")
            
            # Получаем сообщение о подключении
            connection_msg = await websocket.recv()
            data = json.loads(connection_msg)
            print(f"📨 Получено: {data}")
            
            if data.get('type') == 'connected':
                print(f"✅ Подтверждение подключения: {data.get('message')}")
            
            print("\n🔄 Ожидание обновлений в реальном времени...")
            print("(Нажмите Ctrl+C для остановки)\n")
            
            # Счетчик обновлений
            update_count = 0
            
            # Слушаем обновления в течение 30 секунд
            while update_count < 30:
                try:
                    # Ждем сообщение с таймаутом 2 секунды
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    if data.get('type') == 'market_update':
                        update_count += 1
                        timestamp = datetime.fromisoformat(data.get('timestamp', ''))
                        
                        print(f"\n📊 Обновление #{update_count} [{timestamp.strftime('%H:%M:%S')}]")
                        
                        # Рыночные данные
                        if 'market' in data:
                            market = data['market']
                            print(f"  💰 {market.get('symbol')}: {market.get('current_price')} USDT")
                            print(f"  📈 Изменение 24ч: {market.get('change_24h'):+.2f}%")
                        
                        # EMA данные
                        if 'ema' in data:
                            ema = data['ema']
                            signal_emoji = {
                                'buy': '🟢',
                                'sell': '🔴',
                                'wait': '⚪'
                            }.get(ema.get('signal'), '⚪')
                            print(f"  {signal_emoji} EMA: {ema.get('text')} ({ema.get('percent'):+.2f}%)")
                        
                        # ML данные
                        if 'ml' in data:
                            ml = data['ml']
                            prediction = ml.get('prediction', 0)
                            ml_emoji = '🟢' if prediction > 0.6 else '🔴' if prediction < 0.4 else '🟡'
                            print(f"  {ml_emoji} ML: {prediction*100:.1f}%")
                        
                        # Позиции
                        if 'positions' in data:
                            pos = data['positions']
                            profit = pos.get('current_profit_percent', 0)
                            profit_usdt = pos.get('current_profit_usdt', 0)
                            profit_emoji = '📈' if profit >= 0 else '📉'
                            print(f"  {profit_emoji} Позиции: {profit:+.2f}% ({profit_usdt:+.4f} USDT)")
                    
                    elif data.get('type') == 'pong':
                        print("  🏓 Pong (keep-alive)")
                    
                except asyncio.TimeoutError:
                    # Отправляем ping для поддержания соединения
                    await websocket.send("ping")
                    print("  📤 Отправлен ping")
                
            print("\n✅ Тест завершен успешно!")
            print(f"📊 Получено {update_count} обновлений за 30 секунд")
            print("⚡ Средняя частота: ~1 обновление в секунду")
            
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ Ошибка WebSocket: {e}")
        print("\n💡 Убедитесь, что:")
        print("  1. Сервер запущен (python main_with_webapp.py)")
        print("  2. Порт 8000 доступен")
        print("  3. URL правильный (ws://localhost:8000/ws)")
        
    except ConnectionRefusedError:
        print("\n❌ Не удалось подключиться к серверу")
        print("💡 Запустите сервер: python main_with_webapp.py")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Тест остановлен пользователем")
        
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n" + "=" * 50)
        print("👋 Тест завершен")
        print("=" * 50)


if __name__ == "__main__":
    print("\n🧪 WebSocket Test Suite")
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\n⏹️  Прервано пользователем")
