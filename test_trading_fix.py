"""
ТЕСТ ИСПРАВЛЕНИЙ ТОРГОВЛИ
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_min_amount_fix():
    """Тест исправления минимальных количеств"""
    from core.bot import AdvancedTradingBot
    
    print("🧪 ТЕСТ ИСПРАВЛЕНИЙ МИНИМАЛЬНЫХ КОЛИЧЕСТВ")
    print("=" * 50)
    
    bot = AdvancedTradingBot()
    
    # Тестируем минимальные количества для всех пар
    test_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT']
    
    for symbol in test_pairs:
        min_amount = bot.get_min_amount(symbol)
        market_data = bot.exchange.get_market_data(symbol)
        
        if market_data:
            current_price = market_data['current_price']
            min_usdt = min_amount * current_price
            
            print(f"🔹 {symbol}:")
            print(f"   Минимальное количество: {min_amount}")
            print(f"   Текущая цена: {current_price:.2f} USDT")
            print(f"   Минимальная ставка: {min_usdt:.4f} USDT")
            
            # Проверяем баланс
            balance = bot.exchange.get_balance()
            if balance:
                if balance['free_usdt'] >= min_usdt:
                    print(f"   ✅ Доступно для торговли")
                else:
                    print(f"   ❌ Недостаточно средств (нужно: {min_usdt:.4f} USDT)")
            print()

def test_btc_calculation():
    """Тест расчета для BTC/USDT"""
    from core.exchange import ExchangeManager
    
    print("🧪 ТЕСТ РАСЧЕТА BTC/USDT")
    print("=" * 50)
    
    exchange = ExchangeManager()
    balance = exchange.get_balance()
    market_data = exchange.get_market_data('BTC/USDT')
    
    if balance and market_data:
        current_price = market_data['current_price']
        min_amount = 0.00001  # Правильное минимальное количество
        min_usdt = min_amount * current_price
        
        print(f"💰 Баланс: {balance['free_usdt']:.2f} USDT")
        print(f"💰 Цена BTC: {current_price:.2f} USDT")
        print(f"💰 Минимальная ставка: {min_usdt:.4f} USDT")
        print(f"🎯 Доступно ставок: {int(balance['free_usdt'] / min_usdt)}")
        
        # Расчет размера позиции
        trade_percent = 0.1  # 10%
        calculated_position = balance['free_usdt'] * trade_percent
        calculated_amount = calculated_position / current_price
        
        print(f"\n📊 РАСЧЕТ ПОЗИЦИИ (10%):")
        print(f"   Размер ставки: {calculated_position:.4f} USDT")
        print(f"   Количество BTC: {calculated_amount:.6f}")
        
        if calculated_amount >= min_amount:
            print(f"   ✅ Достаточно для минимального количества")
        else:
            print(f"   ❌ Меньше минимального количества")
            
            # Автоматическое увеличение
            required_position = min_amount * current_price
            print(f"   💡 Авто-увеличение до: {required_position:.4f} USDT")

if __name__ == "__main__":
    test_min_amount_fix()
    print("\n" + "="*50)
    test_btc_calculation()