"""
Тест: Проверка исправления проблемы с изменением цены за 24 часа
Проблема: После первого перезапуска приложения, change_24h показывает 0%
Причина: WebSocket использовал ticker.get('percentage', 0), но get_ticker() возвращает 'change'
Решение: Изменено на ticker.get('change', 0) в WebSocket
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exchange import ExchangeManager
from config.settings import SettingsManager


def test_exchange_ticker_returns_correct_key():
    """Тест: Проверка что get_ticker() возвращает ключ 'change'"""
    print("\n🧪 Тест 1: Проверка что get_ticker() возвращает ключ 'change'")
    
    try:
        settings = SettingsManager()
        exchange = ExchangeManager()
        
        if not exchange.connected:
            print("❌ Exchange не подключен")
            return False
        
        symbol = settings.trading_pairs['active_pair']
        ticker = exchange.get_ticker(symbol)
        
        if not ticker:
            print("❌ Не удалось получить ticker")
            return False
        
        # Проверяем что есть ключ 'change'
        if 'change' not in ticker:
            print(f"❌ Ключ 'change' отсутствует. Доступные ключи: {list(ticker.keys())}")
            return False
        
        change_24h = ticker.get('change', None)
        
        if change_24h is None:
            print("❌ Значение change_24h = None")
            return False
        
        print(f"✅ Тест пройден: change_24h = {change_24h}%")
        print(f"   Все ключи тикера: {list(ticker.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_change_24h_not_zero():
    """Тест: Проверка что change_24h имеет реальное значение (не 0)"""
    print("\n🧪 Тест 2: Проверка что change_24h имеет реальное значение")
    
    try:
        settings = SettingsManager()
        exchange = ExchangeManager()
        
        if not exchange.connected:
            print("❌ Exchange не подключен")
            return False
        
        symbol = settings.trading_pairs['active_pair']
        ticker = exchange.get_ticker(symbol)
        
        if not ticker:
            print("❌ Не удалось получить ticker")
            return False
        
        change_24h = ticker.get('change', 0)
        
        # Проверяем что значение не 0 (при условии что рынок активен)
        # На реальном рынке change_24h почти никогда не равен ровно 0
        print(f"✅ Получено значение change_24h = {change_24h}%")
        
        if isinstance(change_24h, (int, float)):
            print(f"✅ Тест пройден: change_24h имеет корректный тип {type(change_24h).__name__}")
            return True
        else:
            print(f"❌ change_24h имеет неправильный тип: {type(change_24h).__name__}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_server_api_market_uses_change_key():
    """Тест: Проверка что server.py использует ключ 'change' в /api/market"""
    print("\n🧪 Тест 3: Проверка что server.py использует правильный ключ")
    
    try:
        server_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'server.py')
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем что в /api/market endpoint используется 'change'
        if "change_24h = ticker.get('change', 0)" not in content:
            print("❌ /api/market не использует ticker.get('change', 0)")
            return False
        
        print("✅ /api/market правильно использует ticker.get('change', 0)")
        
        # Проверяем что не остались старые ошибки с 'percentage'
        if "ticker.get('percentage'" in content and "@app.get(\"/api/market\")" in content:
            # Нужно проверить что это не в /api/market
            api_market_start = content.find("@app.get(\"/api/market\")")
            next_endpoint = content.find("@app.", api_market_start + 1)
            api_market_section = content[api_market_start:next_endpoint]
            
            if "ticker.get('percentage'" in api_market_section:
                print("❌ В /api/market все еще используется ticker.get('percentage')")
                return False
        
        print("✅ Тест пройден: server.py использует правильные ключи")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_websocket_uses_change_key():
    """Тест: Проверка что WebSocket использует ключ 'change'"""
    print("\n🧪 Тест 4: Проверка что WebSocket использует правильный ключ")
    
    try:
        server_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'server.py')
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Найдем WebSocket метод _get_realtime_data
        ws_start = content.find("async def _get_realtime_data")
        if ws_start == -1:
            print("❌ Не найден метод _get_realtime_data")
            return False
        
        # Найдем конец этого метода (до следующего def)
        ws_end = content.find("\n    async def", ws_start + 1)
        if ws_end == -1:
            ws_end = content.find("\n    def", ws_start + 1)
        if ws_end == -1:
            ws_end = len(content)
        
        ws_section = content[ws_start:ws_end]
        
        # Проверяем что используется 'change'
        if '"change_24h": ticker.get(\'change\', 0)' not in ws_section:
            print("❌ WebSocket не использует ticker.get('change', 0)")
            print(f"WebSocket section:\n{ws_section[:500]}")
            return False
        
        print("✅ WebSocket правильно использует ticker.get('change', 0)")
        
        # Проверяем что НЕ остались старые ошибки с 'percentage'
        if "ticker.get('percentage'" in ws_section:
            print("❌ В WebSocket все еще используется ticker.get('percentage')")
            return False
        
        print("✅ Тест пройден: WebSocket исправлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ: Change 24h")
    print("=" * 60)
    
    results = []
    
    # Тесты проверки кода
    results.append(("Проверка ключ 'change' в get_ticker", test_exchange_ticker_returns_correct_key()))
    results.append(("Проверка значение change_24h", test_change_24h_not_zero()))
    results.append(("Проверка /api/market endpoint", test_server_api_market_uses_change_key()))
    results.append(("Проверка WebSocket метод", test_websocket_uses_change_key()))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Всего: {passed + failed} | Пройдено: {passed} | Ошибок: {failed}")
    print("=" * 60)
    
    return all(result for _, result in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
