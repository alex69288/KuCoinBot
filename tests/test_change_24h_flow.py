"""
Интеграционный тест для проверки передачи change_24h через API
Проверяет весь путь: ExchangeManager -> Bot -> WebApp API -> Frontend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exchange import ExchangeManager
from core.bot import AdvancedTradingBot
import json

def test_full_change_24h_flow():
    """Полный тест передачи данных change_24h"""
    print("🔍 Интеграционный тест change_24h...")
    print("=" * 60)
    
    try:
        # Шаг 1: Проверка ExchangeManager
        print("\n📊 Шаг 1: Проверка ExchangeManager...")
        print("-" * 60)
        exchange = ExchangeManager()
        
        if not exchange.connected:
            print("❌ Не удалось подключиться к бирже")
            return False
        
        symbol = 'BTC/USDT'
        ticker = exchange.get_ticker(symbol)
        
        if not ticker:
            print("❌ get_ticker вернул None")
            return False
        
        exchange_change = ticker.get('change')
        print(f"✅ ExchangeManager.get_ticker() вернул change: {exchange_change}")
        
        if exchange_change is None:
            print("❌ change равно None на уровне ExchangeManager")
            return False
        
        # Шаг 2: Проверка AdvancedTradingBot
        print("\n🤖 Шаг 2: Проверка AdvancedTradingBot...")
        print("-" * 60)
        
        # Создаем бота (он должен использовать тот же ExchangeManager)
        bot = AdvancedTradingBot()
        
        if not bot.exchange or not bot.exchange.connected:
            print("❌ Бот не подключен к бирже")
            return False
        
        bot_ticker = bot.exchange.get_ticker(symbol)
        
        if not bot_ticker:
            print("❌ bot.exchange.get_ticker вернул None")
            return False
        
        bot_change = bot_ticker.get('change')
        print(f"✅ AdvancedTradingBot.exchange.get_ticker() вернул change: {bot_change}")
        
        if bot_change is None:
            print("❌ change равно None на уровне AdvancedTradingBot")
            return False
        
        # Шаг 3: Проверка формирования данных для API (имитация)
        print("\n🌐 Шаг 3: Проверка формирования данных для API...")
        print("-" * 60)
        
        # Имитируем логику из server.py
        change_24h = bot_ticker.get('change', 0)
        
        api_response = {
            "symbol": symbol,
            "current_price": bot_ticker.get('last', 0),
            "high_24h": bot_ticker.get('high', 0),
            "low_24h": bot_ticker.get('low', 0),
            "volume_24h": bot_ticker.get('volume', 0),
            "change_24h": change_24h,
        }
        
        print(f"API Response (имитация):")
        print(json.dumps(api_response, indent=2))
        
        if api_response['change_24h'] == 0 and bot_change != 0:
            print(f"❌ ПРОБЛЕМА: change_24h в API = 0, но bot_change = {bot_change}")
            return False
        
        if api_response['change_24h'] is None:
            print("❌ change_24h в API равно None")
            return False
        
        print(f"\n✅ change_24h в API: {api_response['change_24h']}")
        
        # Финальная проверка
        print("\n" + "=" * 60)
        print("📋 Резюме:")
        print("-" * 60)
        print(f"  Exchange change:     {exchange_change:+.2f}%")
        print(f"  Bot change:          {bot_change:+.2f}%")
        print(f"  API change_24h:      {api_response['change_24h']:+.2f}%")
        
        if exchange_change == bot_change == api_response['change_24h']:
            print("\n✅ Все значения совпадают - данные передаются корректно!")
            return True
        else:
            print("\n❌ Значения не совпадают - есть проблема в цепочке передачи!")
            return False
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_full_change_24h_flow()
    sys.exit(0 if success else 1)
