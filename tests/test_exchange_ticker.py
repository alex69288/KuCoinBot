"""
Тестирование метода get_ticker из ExchangeManager
Проверяет, что изменение цены за 24 часа правильно извлекается
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exchange import ExchangeManager
from utils.logger import log_info, log_error

def test_exchange_manager_ticker():
    """Тестирование метода get_ticker в ExchangeManager"""
    print("🔍 Тестирование ExchangeManager.get_ticker()...")
    print("=" * 60)
    
    try:
        # Создаем экземпляр ExchangeManager
        exchange_manager = ExchangeManager()
        
        if not exchange_manager.connected:
            print("❌ Не удалось подключиться к бирже")
            return False
        
        print("✅ Подключение к бирже успешно")
        
        # Получаем тикер
        symbol = 'BTC/USDT'
        print(f"\n📊 Запрос тикера через ExchangeManager для {symbol}...")
        ticker_data = exchange_manager.get_ticker(symbol)
        
        if not ticker_data:
            print("❌ Метод get_ticker вернул None")
            return False
        
        print("\n🔍 Данные, возвращенные методом get_ticker:")
        print("-" * 60)
        for key, value in ticker_data.items():
            print(f"  {key:20s}: {value}")
        
        print("\n" + "=" * 60)
        print("📈 Анализ поля 'change':")
        print("-" * 60)
        
        if 'change' not in ticker_data:
            print("❌ Поле 'change' отсутствует в ответе!")
            return False
        
        change_value = ticker_data['change']
        
        if change_value is None:
            print("❌ Поле 'change' равно None!")
            print("   Проблема: метод get_ticker возвращает None для percentage")
            return False
        
        if change_value == 0:
            print("⚠️  Поле 'change' равно 0")
            print("   Это может быть проблемой, если цена действительно изменилась")
            print("   Проверяем исходные данные из fetch_ticker...")
            
            # Получаем данные напрямую из CCXT
            raw_ticker = exchange_manager.exchange.fetch_ticker(symbol)
            print(f"\n   Исходное значение percentage из CCXT: {raw_ticker.get('percentage')}")
            
            if raw_ticker.get('percentage') != 0 and raw_ticker.get('percentage') is not None:
                print(f"   ❌ ПРОБЛЕМА НАЙДЕНА: CCXT возвращает {raw_ticker.get('percentage')}, но get_ticker возвращает {change_value}")
                return False
            else:
                print("   ✅ CCXT также возвращает 0, это реальное значение")
        else:
            print(f"✅ Поле 'change' содержит значение: {change_value:+.2f}%")
            
            # Проверяем, что значение логичное (в пределах -50% до +50% за 24 часа)
            if abs(change_value) > 50:
                print(f"⚠️  Значение выглядит подозрительно большим: {change_value:+.2f}%")
            else:
                print(f"✅ Значение в разумных пределах")
        
        # Дополнительная проверка других полей
        print("\n📊 Проверка других полей:")
        print("-" * 60)
        required_fields = ['symbol', 'last', 'high', 'low', 'volume', 'timestamp']
        all_ok = True
        for field in required_fields:
            if field in ticker_data and ticker_data[field] is not None:
                print(f"  ✅ {field:20s}: OK")
            else:
                print(f"  ❌ {field:20s}: Отсутствует или None")
                all_ok = False
        
        print("\n" + "=" * 60)
        if all_ok and change_value is not None:
            print("✅ Тест завершен успешно")
            return True
        else:
            print("❌ Тест выявил проблемы")
            return False
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_exchange_manager_ticker()
    sys.exit(0 if success else 1)
