"""
Тест конфигурации asyncio и WebSocket обработки
Проверяет, что конфигурация asyncio работает корректно на Windows
"""
import sys
import os
import asyncio
import time

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.asyncio_config import configure_asyncio, suppress_asyncio_debug_warnings
from utils.logger import log_info, log_error


def test_asyncio_config():
    """Тест конфигурации asyncio event loop"""
    print("\n" + "="*70)
    print("ТЕСТ 1: Конфигурация asyncio event loop")
    print("="*70 + "\n")
    
    try:
        # Конфигурируем asyncio
        configure_asyncio()
        suppress_asyncio_debug_warnings()
        
        # Получаем текущий event loop policy
        policy = asyncio.get_event_loop_policy()
        print(f"✅ Event loop policy: {policy}")
        
        # На Windows должен быть WindowsSelectorEventLoopPolicy
        if sys.platform == 'win32':
            assert isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy), \
                "На Windows должен использоваться WindowsSelectorEventLoopPolicy"
            print("✅ На Windows установлен правильный WindowsSelectorEventLoopPolicy")
        else:
            print(f"✅ На {sys.platform} используется стандартный policy")
        
        # Проверяем, что можем создать event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(f"✅ Event loop создан: {loop}")
        
        # Проверяем, что loop работает
        async def test_coroutine():
            await asyncio.sleep(0.1)
            return "OK"
        
        result = loop.run_until_complete(test_coroutine())
        assert result == "OK", "Coroutine должна вернуть 'OK'"
        print("✅ Event loop работает корректно")
        
        loop.close()
        print("✅ Event loop закрыт без ошибок")
        
        print("\n✅ ТЕСТ 1 ПРОЙДЕН\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ТЕСТ 1 НЕ ПРОЙДЕН: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_websocket_error_handling():
    """Тест обработки ошибок WebSocket (симуляция)"""
    print("\n" + "="*70)
    print("ТЕСТ 2: Обработка ошибок WebSocket")
    print("="*70 + "\n")
    
    try:
        # Симулируем обработку ConnectionResetError
        class MockWebSocket:
            def __init__(self):
                self.connected = True
            
            async def send_json(self, data):
                if not self.connected:
                    raise ConnectionResetError("Удаленный хост разорвал соединение")
                return True
            
            def disconnect(self):
                self.connected = False
        
        async def test_error_handling():
            ws = MockWebSocket()
            
            # Попытка 1: успешная отправка
            try:
                await ws.send_json({"test": "data"})
                print("✅ Отправка данных в открытое соединение: успешно")
            except ConnectionResetError:
                print("❌ Неожиданная ошибка при отправке в открытое соединение")
                return False
            
            # Симулируем отключение
            ws.disconnect()
            
            # Попытка 2: отправка в закрытое соединение (должна вызвать ConnectionResetError)
            try:
                await ws.send_json({"test": "data"})
                print("❌ Ожидалась ошибка ConnectionResetError")
                return False
            except ConnectionResetError as e:
                print(f"✅ ConnectionResetError корректно обработана: {e}")
                return True
        
        # Запускаем тест
        configure_asyncio()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(test_error_handling())
        loop.close()
        
        if result:
            print("\n✅ ТЕСТ 2 ПРОЙДЕН\n")
        else:
            print("\n❌ ТЕСТ 2 НЕ ПРОЙДЕН\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ТЕСТ 2 НЕ ПРОЙДЕН: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_connection_manager_simulation():
    """Тест симуляции ConnectionManager"""
    print("\n" + "="*70)
    print("ТЕСТ 3: Симуляция ConnectionManager broadcast")
    print("="*70 + "\n")
    
    try:
        class MockConnection:
            def __init__(self, name, fail=False):
                self.name = name
                self.should_fail = fail
            
            async def send_json(self, data):
                if self.should_fail:
                    raise ConnectionResetError(f"Соединение {self.name} разорвано")
                return True
        
        class MockConnectionManager:
            def __init__(self):
                self.active_connections = []
            
            def add_connection(self, conn):
                self.active_connections.append(conn)
            
            async def broadcast(self, message):
                """Рассылает сообщение всем подключенным клиентам"""
                disconnected = []
                
                for connection in list(self.active_connections):
                    try:
                        await connection.send_json(message)
                        print(f"  ✅ Сообщение отправлено: {connection.name}")
                    except ConnectionResetError as e:
                        print(f"  ⚠️  Соединение разорвано: {connection.name}")
                        disconnected.append(connection)
                    except Exception as e:
                        print(f"  ❌ Ошибка отправки: {connection.name}: {e}")
                        disconnected.append(connection)
                
                # Удаляем отключенные соединения
                for conn in disconnected:
                    if conn in self.active_connections:
                        self.active_connections.remove(conn)
                        print(f"  🔌 Соединение удалено: {conn.name}")
                
                return len(disconnected)
        
        async def test_broadcast():
            manager = MockConnectionManager()
            
            # Создаем несколько соединений
            manager.add_connection(MockConnection("Client-1", fail=False))
            manager.add_connection(MockConnection("Client-2", fail=True))  # Это соединение разорвется
            manager.add_connection(MockConnection("Client-3", fail=False))
            
            print(f"Создано соединений: {len(manager.active_connections)}")
            
            # Делаем broadcast
            print("\n📡 Выполняем broadcast...")
            disconnected = await manager.broadcast({"type": "test", "data": "hello"})
            
            print(f"\n📊 Результат:")
            print(f"  • Отключено: {disconnected}")
            print(f"  • Активных осталось: {len(manager.active_connections)}")
            
            # Проверки
            assert disconnected == 1, "Должно быть отключено 1 соединение"
            assert len(manager.active_connections) == 2, "Должно остаться 2 активных соединения"
            
            return True
        
        # Запускаем тест
        configure_asyncio()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(test_broadcast())
        loop.close()
        
        if result:
            print("\n✅ ТЕСТ 3 ПРОЙДЕН\n")
        else:
            print("\n❌ ТЕСТ 3 НЕ ПРОЙДЕН\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ТЕСТ 3 НЕ ПРОЙДЕН: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Запускает все тесты"""
    print("\n" + "="*70)
    print("ЗАПУСК ТЕСТОВ КОНФИГУРАЦИИ ASYNCIO И WEBSOCKET")
    print("="*70)
    
    results = {
        "Конфигурация asyncio": test_asyncio_config(),
        "Обработка ошибок WebSocket": test_websocket_error_handling(),
        "ConnectionManager broadcast": test_connection_manager_simulation(),
    }
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*70 + "\n")
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name:.<50} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nВсего тестов: {total_tests}")
    print(f"Пройдено: {total_passed}")
    print(f"Не пройдено: {total_tests - total_passed}")
    
    if total_passed == total_tests:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!\n")
        return True
    else:
        print(f"\n❌ НЕ ВСЕ ТЕСТЫ ПРОЙДЕНЫ ({total_passed}/{total_tests})\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
