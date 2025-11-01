"""
РАСЧЕТ МИНИМАЛЬНЫХ СТАВОК ДЛЯ ТОРГОВЫХ ПАР
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def calculate_min_trades():
    """Расчет минимальных ставок для всех пар"""
    from core.exchange import ExchangeManager
    
    print("💰 РАСЧЕТ МИНИМАЛЬНЫХ СТАВОК")
    print("=" * 60)
    
    exchange = ExchangeManager()
    
    if not exchange.connected:
        print("❌ Не удалось подключиться к бирже")
        return
    
    # 🔧 ИСПРАВЛЕННЫЕ минимальные количества для KuCoin
    min_amounts = {
        'BTC/USDT': 0.00001,  # 🔧 ИСПРАВЛЕНО: 0.00001 BTC
        'ETH/USDT': 0.001,
        'SOL/USDT': 0.1,
        'ADA/USDT': 1.0,
        'DOT/USDT': 0.1,
        'LINK/USDT': 0.1
    }
    
    print("📊 МИНИМАЛЬНЫЕ СТАВКИ ДЛЯ ТОРГОВЛИ:")
    print("-" * 60)
    
    for symbol, min_amount in min_amounts.items():
        # Получаем текущую цену
        market_data = exchange.get_market_data(symbol)
        if market_data:
            current_price = market_data['current_price']
            min_usdt = min_amount * current_price
            
            print(f"🔹 {symbol}:")
            print(f"   Минимальное количество: {min_amount} {symbol.split('/')[0]}")
            print(f"   Текущая цена: {current_price:.2f} USDT")
            print(f"   Минимальная ставка: {min_usdt:.4f} USDT")
            
            # Рекомендуемый размер ставки (минимум + 10%)
            recommended_usdt = min_usdt * 1.1
            print(f"   Рекомендуемая ставка: {recommended_usdt:.4f} USDT")
            print()
    
    # Проверяем баланс
    balance = exchange.get_balance()
    if balance:
        print("💰 ВАШ БАЛАНС:")
        print(f"   USDT: {balance['free_usdt']:.2f} свободно")
        print(f"   BTC: {balance['free_btc']:.6f} свободно")
        print()
        
        # Какие пары доступны для торговли
        print("🎯 ДОСТУПНЫЕ ДЛЯ ТОРГОВЛИ ПАРЫ:")
        available_pairs = []
        
        for symbol, min_amount in min_amounts.items():
            market_data = exchange.get_market_data(symbol)
            if market_data:
                min_usdt = min_amount * market_data['current_price']
                if balance['free_usdt'] >= min_usdt:
                    available_pairs.append((symbol, min_usdt))
        
        if available_pairs:
            for symbol, min_usdt in available_pairs:
                print(f"   ✅ {symbol} - мин. {min_usdt:.4f} USDT")
        else:
            print("   ❌ Нет доступных пар - пополните баланс!")
            
        # 🔧 РАСЧЕТ ДЛЯ BTC/USDT С ТЕКУЩИМ БАЛАНСОМ
        btc_min_amount = 0.00001
        btc_price = exchange.get_market_data('BTC/USDT')['current_price']
        btc_min_usdt = btc_min_amount * btc_price
        
        print(f"\n🎯 РАСЧЕТ ДЛЯ BTC/USDT:")
        print(f"   Минимальная ставка: {btc_min_usdt:.4f} USDT")
        print(f"   Ваш баланс: {balance['free_usdt']:.2f} USDT")
        print(f"   Доступно ставок: {int(balance['free_usdt'] / btc_min_usdt)}")
        
        # Рекомендуемый размер позиции
        recommended_percent = (btc_min_usdt / balance['free_usdt']) * 100
        print(f"   Рекомендуемый размер позиции: {recommended_percent:.1f}%")
    
    print("=" * 60)
    print("💡 Теперь бот сможет торговать с вашим текущим балансом!")

if __name__ == "__main__":
    calculate_min_trades()