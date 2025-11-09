"""Подсчет открытых покупок через закрытые ордера"""
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

ex = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET_KEY'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),
    'enableRateLimit': True
})

print("=" * 60)
print("ПОДСЧЕТ ОТКРЫТЫХ ПОКУПОК ЧЕРЕЗ ЗАКРЫТЫЕ ОРДЕРА")
print("=" * 60)

# Получаем закрытые ордера
try:
    orders = ex.fetch_closed_orders('BTC/USDT', limit=100)
    print(f"✅ Получено закрытых ордеров: {len(orders)}\n")
    
    if orders:
        # Сортируем по времени
        orders.sort(key=lambda x: x['timestamp'])
        
        print("📋 Все закрытые ордера:")
        for i, order in enumerate(orders, 1):
            side = order['side'].upper()
            filled = order.get('filled', 0)
            price = order.get('price', 0)
            datetime = order['datetime']
            print(f"{i}. {datetime} - {side:4} {filled:.8f} BTC @ {price:,.2f} USDT")
        
        # Алгоритм: ищем последний SELL, считаем BUY после него
        last_sell_idx = -1
        for i in range(len(orders) - 1, -1, -1):
            if orders[i]['side'] == 'sell':
                last_sell_idx = i
                print(f"\n🔍 Последний SELL: индекс {i}, дата {orders[i]['datetime']}")
                break
        
        if last_sell_idx < 0:
            print("\n🔍 SELL ордеров нет, все BUY открыты")
            open_buys = [o for o in orders if o['side'] == 'buy']
        else:
            print(f"\n🔍 Берем все BUY после индекса {last_sell_idx}")
            open_buys = [o for o in orders[last_sell_idx+1:] if o['side'] == 'buy']
        
        print(f"\n📈 ОТКРЫТЫХ ПОКУПОК: {len(open_buys)}")
        if open_buys:
            print("\n💰 Детали открытых покупок:")
            total_cost = 0
            for i, order in enumerate(open_buys, 1):
                filled = order.get('filled', 0)
                price = order.get('price', 0)
                cost = filled * price
                total_cost += cost
                print(f"{i}. {order['datetime']}")
                print(f"   Количество: {filled:.8f} BTC")
                print(f"   Цена: {price:,.2f} USDT")
                print(f"   Стоимость: {cost:.2f} USDT\n")
            
            print(f"💵 ОБЩАЯ СТОИМОСТЬ: {total_cost:.2f} USDT")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
